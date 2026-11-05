from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Integer, String, Numeric, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class VerifiedProduct(Base):
    __tablename__ = "verified_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    original_msrp: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    high_copy_avg_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    copy_avg_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    authentic_materials: Mapped[str] = mapped_column(Text, nullable=False)
    fake_materials: Mapped[str] = mapped_column(Text, nullable=False)
    verification_telltales: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    recommended_sources: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<VerifiedProduct id={self.id} name={self.name} brand={self.brand}>"
