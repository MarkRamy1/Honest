from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_name: str = Field(..., min_length=1, max_length=255)
    user_name: Optional[str] = Field("Verified Shopper", max_length=100)
    tier: str = Field("original", pattern="^(original|high-copy|copy)$")
    rating: int = Field(5, ge=1, le=5)
    material_accuracy_rating: int = Field(5, ge=1, le=5)
    price_paid: Optional[float] = Field(None, ge=0)
    store_purchased_from: Optional[str] = Field(None, max_length=255)
    product_url: Optional[str] = Field(None, max_length=1000)
    comment: str = Field(..., min_length=5, max_length=2000)


class ReviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    user_name: str
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    tier: str
    rating: int
    material_accuracy_rating: int
    price_paid: Optional[float] = None
    store_purchased_from: Optional[str] = None
    product_url: Optional[str] = None
    comment: str
    is_verified_buyer: bool
    upvotes: int
    created_at: datetime


class PaginationSchema(BaseModel):
    current_page: int
    last_page: int
    total: int


class ReviewStatsSchema(BaseModel):
    total_reviews: int
    avg_rating: float
    avg_material_accuracy: float


class ReviewListResponse(BaseModel):
    success: bool
    reviews: List[ReviewSchema]
    pagination: PaginationSchema
    stats: ReviewStatsSchema


class ReviewCreateResponse(BaseModel):
    success: bool
    message: str
    review: ReviewSchema


class UpvoteResponse(BaseModel):
    success: bool
    upvotes: int
