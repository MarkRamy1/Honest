from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, SmallInteger, Numeric, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_reviews_product_tier_created", "product_name", "tier", "created_at"),
        Index("ix_reviews_created_at_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_name: Mapped[str] = mapped_column(String(100), default="Verified Shopper", nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tier: Mapped[str] = mapped_column(String(50), default="original", index=True, nullable=False)
    rating: Mapped[int] = mapped_column(SmallInteger, default=5, nullable=False)
    material_accuracy_rating: Mapped[int] = mapped_column(SmallInteger, default=5, nullable=False)
    price_paid: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    store_purchased_from: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    product_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    is_verified_buyer: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review id={self.id} product={self.product_name} rating={self.rating}>"
