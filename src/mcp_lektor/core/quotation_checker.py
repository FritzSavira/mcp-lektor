"""Check for correct German quotation marks and pairing."""

from __future__ import annotations

from mcp_lektor.core.models import (
    DocumentStructure,
    ProposedCorrection,
)


def check_quotation_marks(
    structure: DocumentStructure,
) -> list[ProposedCorrection]:
    """Detect straight quotes that should be replaced with German typographic quotes.

    DEPRECATED: This functionality has been consolidated into the TypographyChecker
    via config/typography_rules.yaml (see ADR-0003).

    Currently returns an empty list. Could be repurposed for stateful balancing
    checks in the future.
    """
    return []
