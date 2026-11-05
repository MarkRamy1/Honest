from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, AuthResponse, AuthMeResponse, UserResponse
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
