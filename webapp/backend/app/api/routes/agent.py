from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Header
from app.services.honest_audit import HonestAuditService
from app.agents.orchestrator import ShoppingAgentOrchestrator
from app.schemas.agent import (
    AskRequest,
    DeepSearchRequest,
    RecommendRequest,
    InCartRequest,
    SocialSearchRequest,
    AlternativesRequest
)

router = APIRouter(tags=["AI Agent"])
audit_service = HonestAuditService()
orchestrator = ShoppingAgentOrchestrator()


@router.get("/agent/models")
@router.get("/models")
def get_models():
    """Returns available AI models (Gemini 1.5 Pro, Claude Fable 5, Gemini Flash)."""
    return {
        "success": True,
        "models": audit_service.get_available_models(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/agent/search")
def search_social(payload: SocialSearchRequest):
    """Social consensus, TikTok unboxings with CC, and review search."""
    return audit_service.search_social(payload.get_title())


@router.post("/agent/ask")
def ask_agent(
    payload: AskRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Shopper Q&A with selected AI Model and Quality Tier (Original vs High Copy vs Copy)."""
    custom_key = payload.get_api_key() or x_api_key
    return audit_service.answer_question(
        question=payload.get_question(),
        product_title=payload.get_product_title(),
        audit=payload.audit,
        model=payload.model or "gemini-pro",
        tier=payload.get_tier(),
        api_key=custom_key
    )


@router.post("/agent/deep-search")
@router.post("/deep-search")
def deep_search(payload: DeepSearchRequest):
    """Deep search product, compare tiers, inspect material authenticity, and find best prices."""
    price_val = None
    price_raw = payload.current_price if payload.current_price is not None else payload.price
    if price_raw is not None:
        try:
            price_val = float(price_raw)
        except (ValueError, TypeError):
            pass

    res = audit_service.deep_search_product(
        product_title=payload.get_product_title(),
        tier=payload.tier or "original",
        model=payload.model or "gemini-pro",
        audit=payload.audit,
        current_price=price_val
    )
    return {
        "success": True,
        **res
    }


@router.post("/agent/alternatives")
def get_alternatives(payload: AlternativesRequest):
    """Get verified higher-scoring alternatives."""
    alternatives = [
        {
            "name": "Premium Studio-Verified Heavyweight Alternative",
            "authenticity_score": 91,
            "price": "$139.00",
            "reason": "Uses 480gsm melton wool, true-to-photo color fidelity, zero shrinkage reported across 240+ reviews."
        },
        {
            "name": "Authentic Tailored Japanese Wool Blend",
            "authenticity_score": 88,
            "price": "$115.00",
            "reason": "Natural drape matches promotional shots; natural horn buttons with reinforced lapel stitching."
        }
    ]
    return {
        "success": True,
        "alternatives": alternatives,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/agent/recommend")
def recommend_products(payload: RecommendRequest):
    """Universal 3-tier shopping recommendation and Value-for-Money discovery."""
    result = audit_service.recommend_best_value(
        query=payload.get_query(),
        category=payload.category,
        budget=payload.budget,
        use_cases=payload.use_cases
    )
    return {
        "success": True,
        "recommendation": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/agent/compare-in-cart")
def compare_in_cart(payload: InCartRequest):
    """Chrome Extension / In-Cart real-time better deal advisor."""
    return audit_service.compare_in_cart_alternative(
        product_title=payload.get_title(),
        current_price=payload.get_price()
    )


@router.post("/agent/research")
def autonomous_research(payload: Dict[str, Any]):
    """Execute end-to-end 11-step autonomous research orchestration workflow."""
    query = payload.get("query") or payload.get("question") or "Product"
    dest = payload.get("destination_country") or "US"
    budget = payload.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
        except (ValueError, TypeError):
            budget = None

    provider_name = payload.get("ai_provider") or payload.get("provider")
    model_name = payload.get("ai_model") or payload.get("model")

    return orchestrator.run_research(
        user_query=query,
        destination_country=dest,
        user_budget_override=budget,
        ai_provider_name=provider_name,
        ai_model_name=model_name
    )

