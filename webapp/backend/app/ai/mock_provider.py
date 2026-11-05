import json
import time
from typing import Dict, Any, List, Optional, Type, TypeVar
from pydantic import BaseModel
from app.ai.base import (
    BaseAIProvider,
    ProviderResponse,
    TokenUsage,
    ToolDefinition,
    ToolCall,
    AIProviderError
)

T = TypeVar("T", bound=BaseModel)


class MockAIProvider(BaseAIProvider):
    """
    Deterministic mock provider for automated tests and offline local development.
    Requires no API keys or network access.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> ProviderResponse:
        start_time = time.time()
        prompt_lower = prompt.lower()

        # Deterministic responses based on prompt keywords
        if "redmi 13" in prompt_lower:
            text = (
                "### Evidence-Based Analysis: Xiaomi Redmi 13\n"
                "The Redmi 13 is a budget 4G/5G Android smartphone featuring a MediaTek Helio G91-Ultra chipset, "
                "a 108MP main camera, a 6.79-inch 90Hz FHD+ IPS display, and a 5030mAh battery with 33W fast charging. "
                "It must not be confused with the Redmi Note 13 (which features an AMOLED panel) or Redmi 13C (an entry-level tier)."
            )
        elif "sony" in prompt_lower and "xm5" in prompt_lower:
            text = (
                "### Evidence-Based Analysis: Sony WH-1000XM5\n"
                "Industry-benchmark noise-cancelling headphones with integrated V1/QN1 dual processors, "
                "30mm carbon composite drivers, 8-mic array, and 250g exact weight."
            )
        else:
            text = f"Mock AI provider response analyzing evidence for: {prompt[:80]}"

        elapsed = round(time.time() - start_time, 4)
        return ProviderResponse(
            text=text,
            structured_data=None,
            tool_calls=[],
            token_usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(text.split()),
                total_tokens=len(prompt.split()) + len(text.split()),
                estimated_cost_usd=0.0
            ),
            finish_reason="stop",
            provider_name=self.provider_name,
            model_name=self.model_name or "mock-model-v1",
            execution_time_seconds=elapsed,
            source_metadata={"mock": True, "mode": "deterministic_test"}
        )

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1
    ) -> T:
        prompt_lower = prompt.lower()
        schema_fields = response_schema.model_fields.keys()
        mock_data: Dict[str, Any] = {}

        for field in schema_fields:
            if field == "target_product":
                if "redmi 13" in prompt_lower:
                    mock_data[field] = "Xiaomi Redmi 13"
                else:
                    mock_data[field] = "Verified Product"
            elif field == "is_exact_match":
                mock_data[field] = "redmi 13" in prompt_lower
            elif field == "brand":
                if "redmi" in prompt_lower or "xiaomi" in prompt_lower:
                    mock_data[field] = "Xiaomi"
                else:
                    mock_data[field] = "Verified Brand"
            elif field == "category":
                mock_data[field] = "smartphones" if "phone" in prompt_lower or "redmi" in prompt_lower else "general"
            elif field == "summary":
                mock_data[field] = "Deterministic mock structured summary based on verified facts."
            elif field == "confidence_score":
                mock_data[field] = 0.95
            elif field == "discrepancies":
                mock_data[field] = []
            else:
                # Default fallback for unhandled fields
                mock_data[field] = "Mock Value"

        try:
            return response_schema.model_validate(mock_data)
        except Exception:
            # Fallback construct
            return response_schema.model_construct(**mock_data)

    def generate_grounded(
        self,
        prompt: str,
        tools: Optional[List[ToolDefinition]] = None,
        system_prompt: Optional[str] = None,
        web_search: bool = False
    ) -> ProviderResponse:
        start_time = time.time()
        prompt_lower = prompt.lower()

        # If tools are provided and searching products is applicable, generate tool calls
        tool_calls: List[ToolCall] = []
        if tools and "search" in prompt_lower:
            tool_calls.append(ToolCall(
                id="call_mock_search_1",
                name="search_products",
                arguments={"query": "Xiaomi Redmi 13", "category": "smartphones"}
            ))

        text = "Executed mock grounded research step."
        elapsed = round(time.time() - start_time, 4)

        return ProviderResponse(
            text=text,
            structured_data=None,
            tool_calls=tool_calls,
            token_usage=TokenUsage(
                prompt_tokens=40,
                completion_tokens=20,
                total_tokens=60,
                estimated_cost_usd=0.0
            ),
            finish_reason="tool_calls" if tool_calls else "stop",
            provider_name=self.provider_name,
            model_name=self.model_name or "mock-grounded-v1",
            execution_time_seconds=elapsed,
            source_metadata={"mock": True, "grounded": web_search or bool(tools)}
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": self.provider_name,
            "model": self.model_name or "mock-default",
            "connected": True,
            "requires_api_key": False,
            "note": "Ready for automated testing and local development"
        }
