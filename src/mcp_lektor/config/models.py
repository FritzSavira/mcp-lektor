"""Pydantic models for application configuration."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# We need CorrectionCategory for the config, but it's a domain enum.
# To avoid circular imports, we might need to keep shared Enums in core/models 
# or move them to a common place. 
# For now, let's import it from core/models as it is a fundamental domain type.
from mcp_lektor.core.models import CorrectionCategory


class ServerConfig(BaseModel):
    """Configuration for the MCP server."""
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "info"


class SessionConfig(BaseModel):
    """Configuration for user sessions."""
    ttl_minutes: int = 30
    cleanup_interval_seconds: int = 60


class ProofreadingConfig(BaseModel):
    """Configuration for the proofreading logic."""
    checks_enabled: list[CorrectionCategory] = Field(
        default_factory=lambda: list(CorrectionCategory)
    )
    llm_model: Optional[str] = "anthropic/claude-sonnet-4.5"
    smart_llm_selector: Optional[str] = None
    max_tokens_per_call: int = 4096
    temperature: float = 0.1
    author_name: str = "MCP Lektor"
    langdock_api_base: str = "https://api.langdock.com/openai/v1"
    langdock_api_key: str = ""
    
    # --- Logic Settings ---
    default_address_form: str = "Sie"
    
    # --- Bible Validation Settings ---
    bible_api_url: str = "https://bible-api.com"
    bible_api_timeout_seconds: float = 5.0
    use_bible_offline_fallback: bool = True
    
    # --- LLM Robustness Settings ---
    llm_max_retries: int = 3
    llm_retry_initial_delay_seconds: float = 2.0
    
    # --- Red-Text Detection Thresholds ---
    red_threshold_r: int = 180
    red_threshold_gb: int = 80


class ConfusedWordEntry(BaseModel):
    """Entry for the confused words dictionary."""
    word: str
    confused_with: str
    explanation: str
    example_correct: str
    example_incorrect: str


class TypographyRule(BaseModel):
    """Rule for typographic replacements."""
    name: str
    pattern: str
    replacement: str
    explanation: str
    category: str


class AppConfig(BaseModel):
    """Root configuration model matching config.yaml structure."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    proofreading: ProofreadingConfig = Field(default_factory=ProofreadingConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
