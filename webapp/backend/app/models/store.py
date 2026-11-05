from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, SmallInteger, Numeric, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class StoreReputation(Base):
    __tablename__ = "stores_reputation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty_tier: Mapped[str] = mapped_column(String(50), default="original", nullable=False)
    trust_score: Mapped[int] = mapped_column(SmallInteger, default=85, nullable=False)
    material_honesty_rating: Mapped[float] = mapped_column(Numeric(3, 1), default=4.5, nullable=False)
    verified_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<StoreReputation id={self.id} store_name={self.store_name} trust_score={self.trust_score}>"
