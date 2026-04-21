"""
Configuration management.

Design principle: Explicit configuration.
- No magic environment detection
- Fail fast if config is missing
- Easy to override for testing

Why Pydantic for config:
- Type validation
- Auto-documentation
- IDE autocomplete
- Easy to extend
"""

from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings.
    
    Design decisions:
    1. Use env vars for secrets (never commit API keys)
    2. Use defaults for non-sensitive config
    3. Validate at startup (fail fast)
    
    Why different LLM providers:
    - OpenAI: Industry standard, good reasoning
    - Anthropic: Best for complex legal analysis
    - Groq: FASTEST inference, open-source models (Llama, Mixtral)
    - Can A/B test or use different providers per agent
    """
    
    # API Keys (from environment) - at least one required
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key (optional)")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key (optional)")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key (optional)")
    supabase_url: Optional[str] = Field(default=None, description="Supabase project URL")
    supabase_service_role_key: Optional[str] = Field(default=None, description="Supabase service role key")
    supabase_bucket: str = Field(default="legal-documents", description="Supabase bucket")
    supabase_db_url: Optional[str] = Field(
        default=None,
        description="Direct Postgres connection string for pgvector queries"
    )
    
    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "groq"] = Field(
        default="groq",
        description="Which LLM provider to use"
    )
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="""Model name examples:
        - Groq: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
        - OpenAI: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
        - Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229
        """
    )
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM (0=deterministic, higher=creative)"
    )
    
    # Retrieval Configuration
    vector_store_type: Literal["faiss", "pgvector"] = Field(
        default="faiss",
        description="Vector store backend"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model for vector search"
    )
    retrieval_top_k: int = Field(
        default=8,
        ge=1,
        le=20,
        description="Number of clauses to retrieve"
    )
    retrieval_min_similarity: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold for accepting retrieved clauses"
    )
    allow_stub_fallback: bool = Field(
        default=False,
        description="Allow retriever to fall back to stub clauses when backend retrieval fails"
    )
    
    # Confidence & Risk Thresholds
    high_confidence_threshold: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Threshold for answering without warnings"
    )
    low_confidence_threshold: float = Field(
        default=60.0,
        ge=0.0,
        le=100.0,
        description="Below this, refuse to answer"
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload on code changes (dev only)")
    
    # Paths
    data_dir: str = Field(default="./data", description="Data directory")
    vector_store_path: str = Field(default="./data/vector_store", description="Vector store path")
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get settings singleton.
    
    Why singleton:
    - Load config once at startup
    - Share across entire app
    - Easy to override for testing
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

