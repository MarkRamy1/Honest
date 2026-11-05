import json
import time
from typing import Dict, Any, List, Optional, Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI, OpenAIError

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


class OpenAIAIProvider(BaseAIProvider):
    """
    OpenAI API Provider using the official OpenAI Python SDK.
    Supports supported models (e.g. 'gpt-4o', 'gpt-4o-mini'), tool calling,
    structured outputs, and token/cost tracking.
    """

    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, timeout_seconds: float = 12.0):
        super().__init__(model_name=model_name, api_key=api_key, timeout_seconds=timeout_seconds)
        if not self.api_key:
            logger.warning("OpenAIAIProvider initialized without an API key.")
        self._client: Optional[OpenAI] = None

    @property
    def provider_name(self) -> str:
        return "openai"

    def _get_client(self) -> OpenAI:
        if not self.api_key:
            raise AIProviderError(
                message="OPENAI_API_KEY is not configured. Set OPENAI_API_KEY in backend environment.",
                provider=self.provider_name,
                status_code=401
            )
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
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

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            elapsed = round(time.time() - start_time, 4)

            choice = response.choices[0]
            text = choice.message.content or ""

            prompt_toks = response.usage.prompt_tokens if response.usage else 0
            comp_toks = response.usage.completion_tokens if response.usage else 0

            return ProviderResponse(
                text=text,
                structured_data=None,
                tool_calls=[],
                token_usage=TokenUsage(
                    prompt_tokens=prompt_toks,
                    completion_tokens=comp_toks,
                    total_tokens=prompt_toks + comp_toks,
                    estimated_cost_usd=round((prompt_toks * 0.0000025) + (comp_toks * 0.00001), 6)
                ),
                finish_reason=choice.finish_reason or "stop",
                provider_name=self.provider_name,
                model_name=self.model_name,
                execution_time_seconds=elapsed,
                source_metadata={"grounding": False}
            )
        except OpenAIError as e:
            raise AIProviderError(
                message=f"OpenAI API Error: {str(e)}",
                provider=self.provider_name,
                status_code=getattr(e, "status_code", 500)
            ) from e
        except Exception as e:
            raise AIProviderError(
                message=f"OpenAI execution error: {str(e)}",
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

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.beta.chat.completions.parse(
                model=self.model_name,
                messages=messages,
                response_format=response_schema,
                temperature=temperature
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                raise ValueError("Structured parsing returned None.")
            return parsed
        except OpenAIError as e:
            raise AIProviderError(
                message=f"OpenAI Structured API Error: {str(e)}",
                provider=self.provider_name,
                status_code=getattr(e, "status_code", 500)
            ) from e
        except Exception as e:
            raise AIProviderError(
                message=f"Failed to parse structured output from OpenAI: {str(e)}",
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

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Format tools if provided
        openai_tools = []
        if tools:
            for t in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters
                    }
                })

        try:
            kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.2
            }
            if openai_tools:
                kwargs["tools"] = openai_tools

            response = client.chat.completions.create(**kwargs)
            elapsed = round(time.time() - start_time, 4)

            choice = response.choices[0]
            msg = choice.message
            text = msg.content or ""

            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    args = {}
                    try:
                        args = json.loads(tc.function.arguments)
                    except Exception:
                        args = {"raw": tc.function.arguments}
                    tool_calls.append(ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args
                    ))

            prompt_toks = response.usage.prompt_tokens if response.usage else 0
            comp_toks = response.usage.completion_tokens if response.usage else 0

            return ProviderResponse(
                text=text,
                structured_data=None,
                tool_calls=tool_calls,
                token_usage=TokenUsage(
                    prompt_tokens=prompt_toks,
                    completion_tokens=comp_toks,
                    total_tokens=prompt_toks + comp_toks
                ),
                finish_reason=choice.finish_reason or "stop",
                provider_name=self.provider_name,
                model_name=self.model_name,
                execution_time_seconds=elapsed,
                source_metadata={"tool_count": len(tool_calls)}
            )
        except OpenAIError as e:
            raise AIProviderError(
                message=f"OpenAI Grounded Error: {str(e)}",
                provider=self.provider_name,
                status_code=getattr(e, "status_code", 500)
            ) from e
        except Exception as e:
            raise AIProviderError(
                message=f"OpenAI grounded research failed: {str(e)}",
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
            "api_key_status": masked_key
        }
