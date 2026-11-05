import pytest
from pydantic import BaseModel
from app.ai.base import AIProviderError, TokenUsage, ToolDefinition
from app.ai.mock_provider import MockAIProvider
from app.ai.gemini_provider import GeminiAIProvider
from app.ai.openai_provider import OpenAIAIProvider
from app.ai.factory import get_ai_provider, get_provider_health_status, OFFICIAL_MODEL_CATALOG


class DummyStructuredOutput(BaseModel):
    target_product: str
    is_exact_match: bool
    brand: str
    summary: str


def test_mock_provider_text_generation():
    provider = MockAIProvider(model_name="mock-v1")
    resp = provider.generate_text("Analyze Xiaomi Redmi 13 specifications")
    assert resp.provider_name == "mock"
    assert "Redmi 13" in resp.text
    assert resp.token_usage.total_tokens > 0
    assert resp.execution_time_seconds >= 0.0


def test_mock_provider_structured_generation():
    provider = MockAIProvider(model_name="mock-v1")
    structured = provider.generate_structured(
        prompt="Extract product details for Xiaomi Redmi 13",
        response_schema=DummyStructuredOutput
    )
    assert structured.target_product == "Xiaomi Redmi 13"
    assert structured.is_exact_match is True
    assert structured.brand == "Xiaomi"


def test_mock_provider_grounded_generation():
    provider = MockAIProvider(model_name="mock-v1")
    tools = [
        ToolDefinition(
            name="search_products",
            description="Search external product catalog",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}}
        )
    ]
    resp = provider.generate_grounded(prompt="search for Redmi 13", tools=tools)
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "search_products"
    assert "Redmi 13" in resp.tool_calls[0].arguments["query"]


def test_provider_factory_selection():
    mock_prov = get_ai_provider("mock", "mock-v1")
    assert mock_prov.provider_name == "mock"

    with pytest.raises(AIProviderError) as exc_info:
        get_ai_provider("unknown_provider_xyz")
    assert "Unsupported AI_PROVIDER" in str(exc_info.value)


def test_missing_api_key_raises_explicit_error():
    # Attempting to use gemini without key must raise explicit AIProviderError
    with pytest.raises(AIProviderError) as exc_info:
        get_ai_provider("gemini", api_key="")
    assert "GEMINI_API_KEY" in str(exc_info.value)
    assert exc_info.value.status_code == 401

    # Attempting to use openai without key must raise explicit AIProviderError
    with pytest.raises(AIProviderError) as exc_info:
        get_ai_provider("openai", api_key="")
    assert "OPENAI_API_KEY" in str(exc_info.value)
    assert exc_info.value.status_code == 401


def test_provider_health_check_endpoint(client):
    res = client.get("/api/providers/health")
    assert res.status_code == 200
    data = res.json()
    assert "active_provider" in data
    assert "providers" in data
    assert "mock" in data["providers"]
    assert data["providers"]["mock"]["status"] == "healthy"
    # Verify no API secrets are exposed
    for p_name, p_info in data["providers"].items():
        if "api_key" in p_info:
            assert not p_info["api_key"].startswith("AIza")
            assert not p_info["api_key"].startswith("sk-")
    assert "gemini" in data["supported_catalog"]
    assert "openai" in data["supported_catalog"]
