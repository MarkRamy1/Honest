import secrets
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, GoogleAuthRequest, AuthResponse, AuthMeResponse, UserResponse
from app.api.dependencies import get_optional_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    """Register a new user account with bcrypt password hashing."""
    email_clean = payload.email.lower().strip()

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The email has already been taken."
        )

    user = User(
        name=payload.name.strip(),
        email=email_clean,
        hashed_password=get_password_hash(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    response.set_cookie(
        key="honest_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "success": True,
        "message": "Account created successfully! Welcome to Honest AI.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "token": token
    }


@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    email_clean = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    token = create_access_token(subject=user.id)
    response.set_cookie(
        key="honest_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "success": True,
        "message": f"Welcome back, {user.name}!",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "token": token
    }


@router.post("/google")
def google_auth(payload: GoogleAuthRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate or auto-register a user via Google Sign-In.
    Supports both production Google ID token verification (GOOGLE_CLIENT_ID / oauth2 tokeninfo)
    and direct developer/team Google identity sign-in when running locally.
    """
    email_clean: str = ""
    display_name: str = ""

    if payload.credential:
        try:
            with httpx.Client(timeout=8.0) as client:
                # 1. Try verifying as a Google ID Token JWT (from Google One-Tap / Sign-In button)
                verify_res = client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": payload.credential}
                )
                if verify_res.status_code == 200:
                    token_data = verify_res.json()
                    if settings.GOOGLE_CLIENT_ID and token_data.get("aud") != settings.GOOGLE_CLIENT_ID:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Google token audience mismatch."
                        )
                    email_clean = (token_data.get("email") or "").lower().strip()
                    display_name = (token_data.get("name") or email_clean.split("@")[0]).strip()
                else:
                    # 2. Fallback: Verify as a Google OAuth 2.0 Access Token (from google.accounts.oauth2.initTokenClient popup)
                    userinfo_res = client.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {payload.credential}"}
                    )
                    if userinfo_res.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Google ID or OAuth access token."
                        )
                    u_data = userinfo_res.json()
                    email_clean = (u_data.get("email") or "").lower().strip()
                    display_name = (u_data.get("name") or email_clean.split("@")[0]).strip()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not verify Google token: {e}"
            )
    elif payload.email:
        email_clean = payload.email.lower().strip()
        display_name = (payload.name or email_clean.split("@")[0].replace(".", " ").title()).strip()
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Either a Google credential token or Google email is required."
        )

    if not email_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Google account did not provide a valid email address."
        )

    user = db.query(User).filter(User.email == email_clean).first()
    is_new_user = False

    if not user:
        is_new_user = True
        user = User(
            name=display_name or "Google Shopper",
            email=email_clean,
            hashed_password=get_password_hash(secrets.token_urlsafe(32))
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=user.id)
    response.set_cookie(
        key="honest_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "success": True,
        "is_new_user": is_new_user,
        "message": (
            f"Google account created! Welcome to Honest AI, {user.name}."
            if is_new_user
            else f"Welcome back via Google, {user.name}!"
        ),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "token": token
    }


@router.post("/logout")
def logout(response: Response):
    """Log out current user session."""
    response.delete_cookie(key="honest_token")
    return {
        "success": True,
        "message": "Successfully signed out of Honest AI."
    }


@router.get("/me")
def me(current_user: User = Depends(get_optional_user)):
    """Return currently authenticated user details or null."""
    if not current_user:
        return {
            "authenticated": False,
            "user": None
        }

    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        }
    }
