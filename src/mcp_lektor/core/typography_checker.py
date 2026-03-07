"""Rule-based typography checks using regex patterns."""

from __future__ import annotations

import re

from mcp_lektor.config.models import TypographyRule
from mcp_lektor.core.models import (
    ConfidenceLevel,
    CorrectionCategory,
    DocumentStructure,
    ProposedCorrection,
)


def check_typography(
    structure: DocumentStructure,
    rules: list[TypographyRule],
) -> list[ProposedCorrection]:
    """Apply typography rules to all non-placeholder paragraphs.

    Each rule contains a regex *pattern* and a *replacement*.
    Returns a ProposedCorrection for every match.
    """
    corrections: list[ProposedCorrection] = []

    for para in structure.paragraphs:
        if para.is_placeholder_paragraph:
            continue

        for run_idx, run in enumerate(para.runs):
            if run.is_placeholder:
                continue
            text = run.text
            if not text.strip():
                continue

            for rule in rules:
                for match in re.finditer(rule.pattern, text):
                    replaced = re.sub(rule.pattern, rule.replacement, match.group(0))
                    category = _rule_category(rule)
                    corrections.append(
                        ProposedCorrection(
                            id="",
                            paragraph_index=para.index,
                            run_index=run_idx,
                            char_offset_start=match.start(),
                            char_offset_end=match.end(),
                            original_text=match.group(0),
                            suggested_text=replaced,
                            category=category,
                            confidence=ConfidenceLevel.HIGH,
                            explanation=rule.explanation,
                            rule_reference=rule.name,
                        )
                    )
    return corrections


def _rule_category(rule: TypographyRule) -> CorrectionCategory:
    """Map a rule's category string to the enum."""
    mapping = {
        "Typografie": CorrectionCategory.TYPOGRAPHY,
        "Anfuehrungszeichen": CorrectionCategory.QUOTATION_MARKS,
    }
    return mapping.get(rule.category, CorrectionCategory.TYPOGRAPHY)
