from datetime import datetime, timezone
from fastapi import APIRouter
from app.ai.factory import get_provider_health_status

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Health check endpoint used by browser extension and web frontend."""
    return {
        "status": "online",
        "version": "4.0.0",
        "framework": "Python 3.11 (FastAPI + SQLAlchemy 2.0)",
        "edition": "Honest 4.0 Multimodal & Generative AI Platform",
        "capabilities": [
            "multimodal_vlm_audit",
            "generative_reality_synthesis",
            "social_sentiment_mining",
            "tiktok_cc_transcription",
            "interactive_scorecard_generator",
            "ask_honest_agent",
            "autonomous_shopping_research",
            "multi_provider_ai_architecture",
            "exact_product_identity_matching",
            "pdp_buy_link_validation",
            "verifiable_currency_engine"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/providers/health")
@router.get("/agent/providers/health")
def provider_health():
    """
    Provider health-check reporting multi-model AI configuration,
    model catalog, and connectivity status without leaking secrets.
    """
    return get_provider_health_status()
