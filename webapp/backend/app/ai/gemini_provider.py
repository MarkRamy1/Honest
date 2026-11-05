import json
import time
from typing import Dict, Any, List, Optional, Type, TypeVar
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.ai.base import (
    BaseAIProvider,
    ProviderResponse,
    TokenUsage,
    ToolDefinition,
    ToolCall,
    AIProviderError
)
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class GeminiAIProvider(BaseAIProvider):
    """
    Google Gemini API Provider using the official Google GenAI SDK.
    Supports official dynamic model catalog (e.g. 'gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-4-argon'),
    Google Search grounding, structured Pydantic schemas, and token usage tracking.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None, timeout_seconds: float = 12.0):
        super().__init__(model_name=model_name, api_key=api_key, timeout_seconds=timeout_seconds)
        if not self.api_key:
            logger.warning("GeminiAIProvider initialized without an API key.")
        self._client: Optional[genai.Client] = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _get_client(self) -> genai.Client:
        if not self.api_key:
            raise AIProviderError(
                message="GEMINI_API_KEY is not configured. Set GEMINI_API_KEY in backend environment.",
                provider=self.provider_name,
                status_code=401
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> ProviderResponse:
        start_time = time.time()
        client = self._get_client()

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt if system_prompt else None
        )

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            elapsed = round(time.time() - start_time, 4)

            text = response.text or ""
            # Extract usage metadata if available
            prompt_toks = 0
            cand_toks = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                prompt_toks = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                cand_toks = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

            return ProviderResponse(
                text=text,
                structured_data=None,
                tool_calls=[],
                token_usage=TokenUsage(
                    prompt_tokens=prompt_toks,
                    completion_tokens=cand_toks,
                    total_tokens=prompt_toks + cand_toks,
                    estimated_cost_usd=round((prompt_toks * 0.00000015) + (cand_toks * 0.0000006), 6)
                ),
                finish_reason="stop",
                provider_name=self.provider_name,
                model_name=self.model_name,
                execution_time_seconds=elapsed,
                source_metadata={"grounding": False}
            )
        except APIError as e:
            raise AIProviderError(
                message=f"Gemini API Error [{e.code}]: {e.message}",
                provider=self.provider_name,
                status_code=e.code
            ) from e
        except Exception as e:
            raise AIProviderError(
                message=f"Gemini generation failure: {str(e)}",
                provider=self.provider_name
            ) from e

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1
    ) -> T:
        client = self._get_client()

        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=system_prompt if system_prompt else None
        )

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            raw_text = response.text or "{}"
            parsed_data = json.loads(raw_text)
            return response_schema.model_validate(parsed_data)
        except APIError as e:
            raise AIProviderError(
                message=f"Gemini API Error [{e.code}]: {e.message}",
                provider=self.provider_name,
                status_code=e.code
            ) from e
        except Exception as e:
            raise AIProviderError(
                message=f"Failed to generate valid structured response from Gemini: {str(e)}",
                provider=self.provider_name
            ) from e

    def generate_grounded(
        self,
        prompt: str,
        tools: Optional[List[ToolDefinition]] = None,
        system_prompt: Optional[str] = None,
        web_search: bool = False
    ) -> ProviderResponse:
        start_time = time.time()
        client = self._get_client()

        # Build tools config
        tool_configs: List[Any] = []
        if web_search:
            # Official Google Search Grounding tool
            tool_configs.append({"google_search": {}})

        config = types.GenerateContentConfig(
            temperature=0.2,
            tools=tool_configs if tool_configs else None,
            system_instruction=system_prompt if system_prompt else None
        )

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            elapsed = round(time.time() - start_time, 4)
            text = response.text or ""

            # Check for grounding metadata
            source_meta = {"grounded": web_search}
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                    gm = candidate.grounding_metadata
                    queries = getattr(gm, "web_search_queries", []) or []
                    source_meta["web_queries"] = queries
                    sources = []
                    chunks = getattr(gm, "grounding_chunks", []) or []
                    for chunk in chunks:
                        if hasattr(chunk, "web") and chunk.web:
                            sources.append({
                                "title": getattr(chunk.web, "title", ""),
                                "url": getattr(chunk.web, "uri", "")
                            })
                    source_meta["grounding_sources"] = sources

            return ProviderResponse(
                text=text,
                structured_data=None,
                tool_calls=[],
                token_usage=TokenUsage(total_tokens=len(prompt.split()) + len(text.split())),
                finish_reason="stop",
                provider_name=self.provider_name,
                model_name=self.model_name,
                execution_time_seconds=elapsed,
                source_metadata=source_meta
            )
        except APIError as e:
            raise AIProviderError(
                message=f"Gemini Grounded Error [{e.code}]: {e.message}",
                provider=self.provider_name,
                status_code=e.code
            ) from e
        except Exception as e:
            raise AIProviderError(
                message=f"Gemini grounded research failed: {str(e)}",
                provider=self.provider_name
            ) from e

    def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and len(self.api_key.strip()) > 8)
        masked_key = f"{self.api_key[:4]}...{self.api_key[-3:]}" if has_key else "Not Configured"
        return {
            "status": "configured" if has_key else "missing_key",
            "provider": self.provider_name,
            "model": self.model_name,
            "connected": has_key,
            "requires_api_key": True,
            "api_key_status": masked_key,
            "grounding_supported": True
        }
