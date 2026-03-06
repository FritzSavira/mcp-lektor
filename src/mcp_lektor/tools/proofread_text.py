"""MCP tool: proofread_text – run proofreading and return corrections."""

from __future__ import annotations

import json

from mcp_lektor.core.models import CorrectionCategory
from mcp_lektor.core.proofreading_engine import ProofreadingEngine
from mcp_lektor.tools._session_store import get_session, update_session

_CATEGORY_ALIASES: dict[str, CorrectionCategory | None] = {
    "all": None,
    "spelling": CorrectionCategory.SPELLING,
    "rechtschreibung": CorrectionCategory.SPELLING,
    "grammar": CorrectionCategory.GRAMMAR,
    "grammatik": CorrectionCategory.GRAMMAR,
    "punctuation": CorrectionCategory.PUNCTUATION,
    "zeichensetzung": CorrectionCategory.PUNCTUATION,
    "typography": CorrectionCategory.TYPOGRAPHY,
    "typografie": CorrectionCategory.TYPOGRAPHY,
    "quotation": CorrectionCategory.QUOTATION_MARKS,
    "anfuehrungszeichen": CorrectionCategory.QUOTATION_MARKS,
    "address": CorrectionCategory.ADDRESS_FORM,
    "anrede": CorrectionCategory.ADDRESS_FORM,
    "confused": CorrectionCategory.CONFUSED_WORD,
    "verwechslung": CorrectionCategory.CONFUSED_WORD,
    "bible": CorrectionCategory.BIBLE_REFERENCE,
    "bibelstelle": CorrectionCategory.BIBLE_REFERENCE,
}


def _parse_checks(checks_str: str | None) -> list[CorrectionCategory] | None:
    """Parse a comma-separated checks string into category list.

    Returns ``None`` when all checks should be run.
    """
    if not checks_str or checks_str.strip().lower() == "all":
        return None

    result: list[CorrectionCategory] = []
    for token in checks_str.split(","):
        token = token.strip().lower()
        if token in _CATEGORY_ALIASES:
            cat = _CATEGORY_ALIASES[token]
            if cat is not None and cat not in result:
                result.append(cat)
    return result or None


async def proofread_text(
    session_id: str,
    checks: str = "all",
) -> str:
    """Perform proofreading analysis on an extracted document.

    Parameters
    ----------
    session_id:
        The session id returned by ``extract_document``.
    checks:
        Comma-separated list of check categories, or ``"all"``.

    Returns
    -------
    JSON string with the ``ProofreadingResult``.
    """
    try:
        session = get_session(session_id)
    except KeyError:
        return json.dumps(
            {"error": f"Session not found: {session_id}"},
            ensure_ascii=False,
        )

    structure = session["structure"]
    parsed_checks = _parse_checks(checks)

    engine = ProofreadingEngine()
    result = await engine.proofread(structure, parsed_checks)

    # Store result in session for later use by write_corrected_docx
    update_session(session_id, {"proofreading_result": result})

    return json.dumps(
        result.model_dump(),
        ensure_ascii=False,
        indent=2,
    )
