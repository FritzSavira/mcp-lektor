"""Load YAML and environment configuration for MCP Lektor."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from mcp_lektor.config.models import (
    AppConfig,
    ConfusedWordEntry,
    ProofreadingConfig,
    TypographyRule,
)

def _find_config_dir() -> Path:
    """Try to find the config directory in common locations."""
    # 1. Direct path /app/config (Docker)
    docker_path = Path("/app/config")
    if docker_path.exists():
        return docker_path
    
    # 2. Local development path (relative to this file)
    local_path = Path(__file__).resolve().parent.parent.parent.parent / "config"
    if local_path.exists():
        return local_path
    
    # 3. Current working directory + config
    cwd_path = Path.cwd() / "config"
    if cwd_path.exists():
        return cwd_path
        
    return local_path # Fallback

_CONFIG_DIR = _find_config_dir()
_CACHED_SETTINGS: AppConfig | None = None


def get_settings(reload: bool = False) -> AppConfig:
    """Get the full application configuration.
    
    If reload=True, the configuration is reloaded from disk and environment.
    """
    global _CACHED_SETTINGS
    if _CACHED_SETTINGS is None or reload:
        _CACHED_SETTINGS = _load_full_config()
    return _CACHED_SETTINGS


def _load_full_config() -> AppConfig:
    """Load config.yaml and apply environment overrides."""
    path = _CONFIG_DIR / "config.yaml"
    raw: dict[str, Any] = {}
    
    if path.exists():
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    
    # 1. Start with YAML data
    # 2. Apply environment overrides (LEKTOR_SECTION__KEY)
    _apply_env_overrides(raw)
    
    return AppConfig(**raw)


def _apply_env_overrides(config_dict: dict[str, Any]) -> None:
    """Apply environment variables starting with LEKTOR_ to the config dict.
    
    Pattern: LEKTOR_SECTION__KEY=VALUE (e.g. LEKTOR_PROOFREADING__LLM_MODEL=gpt-4)
    """
    for env_key, value in os.environ.items():
        if not env_key.startswith("LEKTOR_"):
            continue
        
        # Remove prefix
        parts = env_key[7:].lower().split("__")
        if len(parts) != 2:
            continue
            
        section, key = parts
        if section not in config_dict:
            config_dict[section] = {}
            
        # Try to parse numeric values
        try:
            if "." in value:
                parsed_value: Any = float(value)
            else:
                parsed_value = int(value)
        except ValueError:
            # Fallback to boolean or string
            if value.lower() in ("true", "yes", "on"):
                parsed_value = True
            elif value.lower() in ("false", "no", "off"):
                parsed_value = False
            elif value.lower() == "null":
                parsed_value = None
            else:
                parsed_value = value
                
        config_dict[section][key] = parsed_value


# ── Backward Compatibility API ──

def load_config(config_dir: Path | None = None) -> ProofreadingConfig:
    """Load the main config.yaml and return a ProofreadingConfig."""
    if config_dir is not None:
        # If a specific dir is provided, we don't use the cache
        path = config_dir / "config.yaml"
        if not path.exists():
            return ProofreadingConfig()
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        _apply_env_overrides(raw)
        return AppConfig(**raw).proofreading
        
    return get_settings().proofreading


def load_typography_rules(config_dir: Path | None = None) -> list[TypographyRule]:
    """Load typography_rules.yaml and return a list of TypographyRule."""
    base = config_dir or _CONFIG_DIR
    path = base / "typography_rules.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return [TypographyRule(**r) for r in raw.get("rules", [])]


def load_confused_words(config_dir: Path | None = None) -> list[ConfusedWordEntry]:
    """Load confused_words.yaml and return a list of ConfusedWordEntry."""
    base = config_dir or _CONFIG_DIR
    path = base / "confused_words.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    words = raw.get("words", [])
    return [ConfusedWordEntry(**w) for w in words]
