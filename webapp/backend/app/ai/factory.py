from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.ai.base import BaseAIProvider, AIProviderError
from app.ai.gemini_provider import GeminiAIProvider
from app.ai.openai_provider import OpenAIAIProvider
from app.ai.mock_provider import MockAIProvider


OFFICIAL_MODEL_CATALOG = {
    "gemini": [
        {
            "id": "gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "description": "Recommended for high-speed grounded research and visual verification.",
            "supports_grounding": True,
            "supports_structured": True
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "description": "Deep multi-step reasoning with 1M+ token context window.",
            "supports_grounding": True,
            "supports_structured": True
        },
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "description": "Ultra-low latency for browser extension audits.",
            "supports_grounding": True,
            "supports_structured": True
        },
        {
            "id": "gemini-4-argon",
            "name": "Gemini 4 Argon",
            "description": "Next-generation multimodal model for advanced research workflows.",
            "supports_grounding": True,
            "supports_structured": True
        }
    ],
    "openai": [
        {
            "id": "gpt-4o",
            "name": "OpenAI GPT-4o",
            "description": "Flagship multimodal intelligence with official tool calling and web search.",
            "supports_grounding": True,
            "supports_structured": True
        },
        {
            "id": "gpt-4o-mini",
            "name": "OpenAI GPT-4o Mini",
            "description": "Fast, cost-efficient model for structured queries.",
            "supports_grounding": True,
            "supports_structured": True
        }
    ],
    "mock": [
        {
            "id": "mock-evidence-v1",
            "name": "Honest Deterministic Mock Provider",
            "description": "Local test engine ensuring reproducible, zero-cost regression test runs.",
            "supports_grounding": True,
            "supports_structured": True
        }
    ]
}


def get_ai_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout_seconds: Optional[float] = None
) -> BaseAIProvider:
    """
    Factory creating configured AI providers without silent fallbacks.
    Validates presence of required credentials and models.
    """
    chosen_provider = (provider_name or settings.AI_PROVIDER or "mock").lower().strip()
    timeout = timeout_seconds or settings.EXTERNAL_REQUEST_TIMEOUT_SECONDS

    if chosen_provider == "gemini":
        key = settings.GEMINI_API_KEY if api_key is None else api_key
        model = model_name or settings.GEMINI_MODEL or settings.AI_MODEL or "gemini-2.5-flash"
        if not key:
            raise AIProviderError(
                message=(
                    "Configured provider 'gemini' requires GEMINI_API_KEY. "
                    "Set GEMINI_API_KEY in backend/.env or configure AI_PROVIDER=mock for local testing."
                ),
                provider="gemini",
                status_code=401
            )
        return GeminiAIProvider(model_name=model, api_key=key, timeout_seconds=timeout)

    elif chosen_provider == "openai":
        key = settings.OPENAI_API_KEY if api_key is None else api_key
        model = model_name or settings.OPENAI_MODEL or "gpt-4o"
        if not key:
            raise AIProviderError(
                message=(
                    "Configured provider 'openai' requires OPENAI_API_KEY. "
                    "Set OPENAI_API_KEY in backend/.env or configure AI_PROVIDER=mock for local testing."
                ),
                provider="openai",
                status_code=401
            )
        return OpenAIAIProvider(model_name=model, api_key=key, timeout_seconds=timeout)

    elif chosen_provider == "mock":
        model = model_name or "mock-evidence-v1"
        return MockAIProvider(model_name=model, api_key="", timeout_seconds=timeout)

    else:
        raise AIProviderError(
            message=f"Unsupported AI_PROVIDER '{chosen_provider}'. Supported options: 'gemini', 'openai', 'mock'.",
            provider=chosen_provider,
            status_code=400
        )


def get_provider_health_status() -> Dict[str, Any]:
    """Inspects all configured providers and returns connectivity status without revealing secrets."""
    results = {}
    for prov_name in ["gemini", "openai", "mock"]:
        try:
            if prov_name == "gemini":
                prov = GeminiAIProvider(
                    model_name=settings.GEMINI_MODEL,
                    api_key=settings.GEMINI_API_KEY
                )
            elif prov_name == "openai":
                prov = OpenAIAIProvider(
                    model_name=settings.OPENAI_MODEL,
                    api_key=settings.OPENAI_API_KEY
                )
            else:
                prov = MockAIProvider(model_name="mock-evidence-v1")
            results[prov_name] = prov.health_check()
        except Exception as e:
            results[prov_name] = {
                "status": "error",
                "provider": prov_name,
                "error": str(e)
            }

    active_provider = settings.AI_PROVIDER or "mock"
    return {
        "active_provider": active_provider,
        "active_model": settings.AI_MODEL,
        "providers": results,
        "supported_catalog": OFFICIAL_MODEL_CATALOG
    }
