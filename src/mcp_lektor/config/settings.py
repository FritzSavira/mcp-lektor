"""Load YAML configuration files for proofreading rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mcp_lektor.core.models import (
    ConfusedWordEntry,
    ProofreadingConfig,
    TypographyRule,
)

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"


def load_config(config_dir: Path | None = None) -> ProofreadingConfig:
    """Load the main config.yaml and return a ProofreadingConfig."""
    base = config_dir or _CONFIG_DIR
    path = base / "config.yaml"
    if not path.exists():
        return ProofreadingConfig()
    with open(path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}
    section = raw.get("proofreading", {})
    return ProofreadingConfig(**section)


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
    return [ConfusedWordEntry(**w) for w in raw.get("words", [])]
