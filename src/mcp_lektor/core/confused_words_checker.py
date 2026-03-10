"""Scan text for commonly confused German words."""

from __future__ import annotations

import re

from mcp_lektor.config.models import ConfusedWordEntry
from mcp_lektor.core.enums import ConfidenceLevel, CorrectionCategory
from mcp_lektor.core.models import (
    DocumentStructure,
    ProposedCorrection,
)


def scan_confused_words(
    structure: DocumentStructure,
    entries: list[ConfusedWordEntry],
) -> list[ProposedCorrection]:
    """Check all non-placeholder runs for confused word patterns.

    This scanner flags *potential* confused words with MEDIUM confidence.
    The LLM or user must decide whether the usage is actually incorrect.
    """
    corrections: list[ProposedCorrection] = []

    # Build lookup: lower-cased word -> entry
    lookup: dict[str, ConfusedWordEntry] = {}
    for entry in entries:
        lookup[entry.word.lower()] = entry
        lookup[entry.confused_with.lower()] = entry

    for para in structure.paragraphs:
        if para.is_placeholder_paragraph:
            continue

        for run_idx, run in enumerate(para.runs):
            if run.is_placeholder:
                continue
            text = run.text
            if not text.strip():
                continue

            for word_match in re.finditer(r"\b\w+\b", text):
                token = word_match.group(0)
                key = token.lower()
                if key not in lookup:
                    continue

                entry = lookup[key]
                corrections.append(
                    ProposedCorrection(
                        id="",
                        paragraph_index=para.index,
                        run_index=run_idx,
                        char_offset_start=word_match.start(),
                        char_offset_end=word_match.end(),
                        original_text=token,
                        suggested_text=f"[pr\u00fcfen: {entry.word}/{entry.confused_with}]",
                        category=CorrectionCategory.CONFUSED_WORD,
                        confidence=ConfidenceLevel.MEDIUM,
                        explanation=entry.explanation,
                        rule_reference=f"Verwechslung: {entry.word} / {entry.confused_with}",
                    )
                )
    return corrections
