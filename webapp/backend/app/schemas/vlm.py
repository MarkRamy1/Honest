from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class VlmAuditRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_name: Optional[str] = Field(None, alias="productName")
    title: Optional[str] = None
    query: Optional[str] = None
    catalog_image_url: Optional[str] = Field(None, alias="catalogImageUrl")
    image_url: Optional[str] = Field(None, alias="imageUrl")
    image: Optional[str] = None
    category: Optional[str] = ""

    def get_product_name(self) -> str:
        return self.product_name or self.title or self.query or "Product"

    def get_image_url(self) -> str:
        return self.catalog_image_url or self.image_url or self.image or ""


class GenerateRealityRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: Optional[str] = "Real-world consumer product photo under natural room light"
    lighting: Optional[str] = "natural"


class VlmAuditResponse(BaseModel):
    success: bool
    audit: Dict[str, Any]
    timestamp: str


class GenerateRealityResponse(BaseModel):
    success: bool
    prompt: str
    lighting: str
    negative_prompt: str
    resolution: str
    suggested_seed: int
    preview_reality_url: str
    aspect_ratio: str
    timestamp: str
