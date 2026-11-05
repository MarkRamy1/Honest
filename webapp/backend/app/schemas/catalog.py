from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class VerifiedProductSchema(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    original_msrp: float
    high_copy_avg_price: float
    copy_avg_price: float
    authentic_materials: str
    fake_materials: str
    verification_telltales: Optional[List[str]] = None
    recommended_sources: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class CatalogSearchResponse(BaseModel):
    success: bool
    count: int
    products: List[VerifiedProductSchema]


class StoreReputationSchema(BaseModel):
    id: int
    store_name: str
    platform: str
    specialty_tier: str
    trust_score: int
    material_honesty_rating: float
    verified_url: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    success: bool
    stores: List[StoreReputationSchema]
