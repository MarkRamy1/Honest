from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate
from app.api.dependencies import get_optional_user, get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("")
def get_reviews(
    product: Optional[str] = Query(None, description="Filter by product name"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve paginated community reviews and aggregate material inspection stats."""
    query = db.query(Review)

    if product and product.strip():
        query = query.filter(Review.product_name.ilike(f"%{product.strip()}%"))
    if tier and tier.strip():
        query = query.filter(Review.tier == tier.strip())
    if brand and brand.strip():
        query = query.filter(Review.brand.ilike(f"%{brand.strip()}%"))

    total = query.count()
    last_page = max(1, ceil(total / per_page))
    offset = (page - 1) * per_page
    reviews = query.order_by(Review.created_at.desc()).offset(offset).limit(per_page).all()

    # Aggregate statistics
    total_reviews_count = db.query(func.count(Review.id)).scalar() or 0
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 5.0
    avg_accuracy = db.query(func.avg(Review.material_accuracy_rating)).scalar() or 4.8

    items = []
    for r in reviews:
        items.append({
            "id": r.id,
            "user_id": r.user_id,
            "user_name": r.user_name,
            "product_name": r.product_name,
            "brand": r.brand,
            "category": r.category,
            "tier": r.tier,
            "rating": r.rating,
            "material_accuracy_rating": r.material_accuracy_rating,
            "price_paid": float(r.price_paid) if r.price_paid is not None else None,
            "store_purchased_from": r.store_purchased_from,
            "product_url": r.product_url,
            "comment": r.comment,
            "is_verified_buyer": r.is_verified_buyer,
            "upvotes": r.upvotes,
            "created_at": r.created_at.isoformat() if r.created_at else ""
        })

    return {
        "success": True,
        "reviews": items,
        "pagination": {
            "current_page": page,
            "last_page": last_page,
            "total": total
        },
        "stats": {
            "total_reviews": total_reviews_count,
            "avg_rating": round(float(avg_rating), 1),
            "avg_material_accuracy": round(float(avg_accuracy), 1)
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Submit a community review and material report."""
    author_name = current_user.name if current_user else (payload.user_name or "Verified Shopper")
    user_id = current_user.id if current_user else None

    review = Review(
        user_id=user_id,
        user_name=author_name,
        product_name=payload.product_name.strip(),
        tier=payload.tier,
        rating=payload.rating,
        material_accuracy_rating=payload.material_accuracy_rating,
        price_paid=payload.price_paid,
        store_purchased_from=payload.store_purchased_from,
        product_url=payload.product_url,
        comment=payload.comment.strip(),
        is_verified_buyer=True,
        upvotes=0
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "success": True,
        "message": "Review and material report saved successfully to database.",
        "review": {
            "id": review.id,
            "user_id": review.user_id,
            "user_name": review.user_name,
            "product_name": review.product_name,
            "tier": review.tier,
            "rating": review.rating,
            "material_accuracy_rating": review.material_accuracy_rating,
            "price_paid": float(review.price_paid) if review.price_paid is not None else None,
            "store_purchased_from": review.store_purchased_from,
            "product_url": review.product_url,
            "comment": review.comment,
            "is_verified_buyer": review.is_verified_buyer,
            "upvotes": review.upvotes,
            "created_at": review.created_at.isoformat() if review.created_at else ""
        }
    }


@router.post("/{review_id}/upvote")
def upvote_review(review_id: int, db: Session = Depends(get_db)):
    """Upvote a helpful community review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found."
        )

    review.upvotes += 1
    db.commit()

    return {
        "success": True,
        "upvotes": review.upvotes
    }


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a community review, strictly enforcing row-level user ownership."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found."
        )

    if review.user_id is None or review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews."
        )

    db.delete(review)
    db.commit()

    return {
        "success": True,
        "deleted_id": review_id
    }

