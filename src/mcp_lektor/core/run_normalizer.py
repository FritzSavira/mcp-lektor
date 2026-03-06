"""
Logic for normalizing fragmented Word runs.
Merges adjacent runs with identical formatting to simplify proofreading and Track Changes.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_lektor.core.models import RunFormatting, TextRun

logger = logging.getLogger(__name__)

def get_run_formatting_hash(fmt: RunFormatting) -> str:
    """
    Create a stable hashable representation of a RunFormatting object.
    Used to detect if two adjacent runs have identical visual properties.
    """
    # We use model_dump_json to get a stable string representation of all fields
    return fmt.model_dump_json()

def normalize_runs(runs: list[TextRun]) -> list[TextRun]:
    """
    Merge adjacent runs that have identical formatting.
    Does NOT merge runs if one is a placeholder and the other isn't.
    """
    if not runs:
        return []

    normalized: list[TextRun] = []
    current_run = runs[0].model_copy()
    current_fmt_hash = get_run_formatting_hash(current_run.formatting)

    for i in range(1, len(runs)):
        next_run = runs[i]
        next_fmt_hash = get_run_formatting_hash(next_run.formatting)

        # Merge conditions: 
        # 1. Identical formatting
        # 2. Both are placeholders OR both are not placeholders
        if (next_fmt_hash == current_fmt_hash and 
            next_run.is_placeholder == current_run.is_placeholder):
            
            # Merge text
            current_run.text += next_run.text
            logger.debug(f"Merged run {i} into {i-1} (same formatting)")
        else:
            # Different formatting or placeholder status, start a new run
            normalized.append(current_run)
            current_run = next_run.model_copy()
            current_fmt_hash = next_fmt_hash

    normalized.append(current_run)
    return normalized
