"""Load YAML configuration files for proofreading rules."""

from __future__ import annotations

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


def load_config(config_dir: Path | None = None) -> ProofreadingConfig:
    """Load the main config.yaml and return a ProofreadingConfig.
    
    Internally parses the full AppConfig to ensure server/session settings are valid too.
    """
    base = config_dir or _CONFIG_DIR
    path = base / "config.yaml"
    if not path.exists():
        return ProofreadingConfig()
    
    with open(path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}
    
    # Validate entire structure
    app_config = AppConfig(**raw)
    
    # Return only the proofreading section for backward compatibility
    return app_config.proofreading


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
