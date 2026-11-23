from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Honest AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security
    SECRET_KEY: str = "dev_secret_key_honest_ai_shopping_platform_super_secure_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    GOOGLE_CLIENT_ID: str = ""

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://markramy1.github.io",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database
    # Defaults to PostgreSQL, but supports SQLite fallback for local test suites
    DATABASE_URL: str = "postgresql+psycopg://honest:honest_secret@localhost:5432/honest_db"

    # Multi-Provider AI Architecture
    AI_PROVIDER: str = "mock"  # "gemini" | "openai" | "mock"
    AI_MODEL: str = "gemini-2.5-flash"  # e.g. "gemini-2.5-flash", "gemini-1.5-pro", "gemini-4-argon", "gpt-4o", "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""

    # Search and Discovery Provider Credentials (Optional External Grounding)
    SERPAPI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    ENABLE_WEB_SEARCH_GROUNDING: bool = True

    # Currency and Exchange Rate Configuration
    EXCHANGE_RATE_API_URL: str = ""
    USD_TO_EGP_FALLBACK: float = 49.50
    USD_TO_EGP: float = 49.50  # Maintained for legacy compatibility

    # Execution, Rate-Limiting, and Budget Controls
    MAX_SEARCH_ITERATIONS: int = 3
    MAX_TOOL_CALLS: int = 6
    EXTERNAL_REQUEST_TIMEOUT_SECONDS: float = 12.0
    MAX_SEARCH_BUDGET_USD: float = 5.0
    MAX_MODEL_OUTPUT_TOKENS: int = 2048

    model_config = SettingsConfigDict(
        env_file=[
            str(Path(__file__).resolve().parents[2] / ".env"),
            ".env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

