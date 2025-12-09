"""
Configuration settings for the PR Reviewer Agent System.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-5.1"
    openai_temperature: float = 0.1

    # Anthropic Configuration (Optional)
    anthropic_api_key: Optional[str] = None

    # GitHub Configuration
    github_token: Optional[str] = None

    # GitLab Configuration
    gitlab_token: Optional[str] = None
    gitlab_url: str = "https://gitlab.com"

    # Bitbucket Configuration
    bitbucket_username: Optional[str] = None
    bitbucket_password: Optional[str] = None
    bitbucket_url: str = "https://api.bitbucket.org"

    # Vector Store Configuration
    chroma_persist_directory: str = "./data/vector_db"
    embedding_model: str = "text-embedding-3-small"

    # Application Configuration
    log_level: str = "INFO"
    cache_enabled: bool = True
    cache_directory: str = "./data/cache"

    # Review Configuration
    review_mode: Literal["quick", "standard", "deep"] = "standard"
    max_issues_per_category: int = 10
    enable_self_reflection: bool = True
    min_confidence_score: float = 0.6

    # Agent Configuration
    max_agent_iterations: int = 5
    agent_timeout: int = 300  # seconds

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 5

    # Rate Limiting
    github_rate_limit: int = 50  # requests per hour
    gitlab_rate_limit: int = 50
    bitbucket_rate_limit: int = 50


# Global settings instance
settings = Settings()

