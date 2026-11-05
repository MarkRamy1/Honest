from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    tool_call_id: str
    content: str


class ProviderResponse(BaseModel):
    text: str
    structured_data: Optional[Dict[str, Any]] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    finish_reason: str = "stop"
    provider_name: str
    model_name: str
    execution_time_seconds: float = 0.0
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class AIProviderError(Exception):
    """Custom exception raised when an AI provider call fails."""
    def __init__(self, message: str, provider: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.details = details or {}


T = TypeVar("T", bound=BaseModel)


class BaseAIProvider(ABC):
    """Abstract interface for all AI model providers (Gemini, OpenAI, Mock)."""

    def __init__(self, model_name: str, api_key: Optional[str] = None, timeout_seconds: float = 12.0):
        self.model_name = model_name
        self.api_key = api_key or ""
        self.timeout_seconds = timeout_seconds

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'gemini', 'openai', 'mock')."""
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> ProviderResponse:
        """Generates a text completion."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1
    ) -> T:
        """Generates a strictly-validated structured Pydantic object."""
        pass

    @abstractmethod
    def generate_grounded(
        self,
        prompt: str,
        tools: Optional[List[ToolDefinition]] = None,
        system_prompt: Optional[str] = None,
        web_search: bool = False
    ) -> ProviderResponse:
        """Generates a response with real tool calling or search grounding."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Validates configuration and provider connectivity without leaking secrets."""
        pass
