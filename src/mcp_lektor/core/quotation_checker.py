"""Check for correct German quotation marks and pairing."""

from __future__ import annotations

import re

from mcp_lektor.core.models import (
    ConfidenceLevel,
    CorrectionCategory,
    DocumentStructure,
    ProposedCorrection,
)


def check_quotation_marks(
    structure: DocumentStructure,
) -> list[ProposedCorrection]:
    """Detect straight quotes that should be replaced with German typographic quotes."""
    corrections: list[ProposedCorrection] = []

    for para in structure.paragraphs:
        if para.is_placeholder_paragraph:
            continue

        for run_idx, run in enumerate(para.runs):
            if run.is_placeholder:
                continue
            text = run.text

            # Flag straight double quotes
            for match in re.finditer(r'"', text):
                corrections.append(
                    ProposedCorrection(
                        id="",
                        paragraph_index=para.index,
                        run_index=run_idx,
                        char_offset_start=match.start(),
                        char_offset_end=match.end(),
                        original_text='"',
                        suggested_text="\u201e oder \u201c",
                        category=CorrectionCategory.QUOTATION_MARKS,
                        confidence=ConfidenceLevel.HIGH,
                        explanation=(
                            "Gerade Anf\u00fchrungszeichen durch typografisch "
                            "korrekte deutsche Anf\u00fchrungszeichen ersetzen "
                            "(\u201e...\u201c oder \u00bb...\u00ab)."
                        ),
                        rule_reference="Typografie: Anf\u00fchrungszeichen",
                    )
                )

    return corrections
