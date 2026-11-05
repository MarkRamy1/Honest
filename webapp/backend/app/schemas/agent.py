from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict


class AskRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question: Optional[str] = Field(None, alias="q")
    product_title: Optional[str] = Field(None, alias="productTitle")
    title: Optional[str] = None
    productName: Optional[str] = None
    audit: Optional[Dict[str, Any]] = None
    model: Optional[str] = "gemini-pro"
    tier: Optional[str] = Field("original", alias="quality_tier")
    api_key: Optional[str] = Field(None, alias="apiKey")
    gemini_api_key: Optional[str] = None

    def get_question(self) -> str:
        return self.question or self.title or "What should I know before buying?"

    def get_product_title(self) -> str:
        return self.product_title or self.title or self.productName or self.get_question()

    def get_tier(self) -> str:
        return self.tier or "original"

    def get_api_key(self) -> Optional[str]:
        return self.api_key or self.gemini_api_key


class DeepSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_title: Optional[str] = Field(None, alias="productTitle")
    title: Optional[str] = None
    productName: Optional[str] = None
    tier: Optional[str] = "original"
    model: Optional[str] = "gemini-pro"
    audit: Optional[Dict[str, Any]] = None
    current_price: Optional[Union[float, str]] = Field(None, alias="currentPrice")
    price: Optional[Union[float, str]] = None

    def get_product_title(self) -> str:
        return self.product_title or self.title or self.productName or "Product"


class RecommendRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: Optional[str] = Field(None, alias="q")
    title: Optional[str] = None
    category: Optional[str] = None
    budget: Optional[float] = None
    use_cases: Optional[List[str]] = Field(None, alias="useCases")

    def get_query(self) -> str:
        return self.query or self.title or "Product"


class InCartRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_title: Optional[str] = Field(None, alias="productTitle")
    title: Optional[str] = None
    current_price: Optional[Union[float, str]] = Field(None, alias="currentPrice")
    price: Optional[Union[float, str]] = None

    def get_title(self) -> str:
        return self.product_title or self.title or "Product"

    def get_price(self) -> Optional[float]:
        p = self.current_price or self.price
        if p is not None:
            try:
                return float(p)
            except (ValueError, TypeError):
                return None
        return None


class SocialSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = None
    query: Optional[str] = None
    product_title: Optional[str] = Field(None, alias="productTitle")
    product_name: Optional[str] = Field(None, alias="productName")

    def get_title(self) -> str:
        return self.title or self.query or self.product_title or self.product_name or "Product"


class AlternativesRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category: Optional[str] = "general"
    score: Optional[int] = 60
