"""MCP tool: validate Bible references found in the document text."""

from __future__ import annotations

import json
import logging

from mcp_lektor.core.bible_validator import BibleValidator
from mcp_lektor.core.models import DocumentStructure
from mcp_lektor.tools._session_store import get_session, update_session

logger = logging.getLogger(__name__)


async def validate_bible_refs(session_id: str) -> str:
    """Detect and validate all Bible references in the uploaded document.

    Parameters
    ----------
    session_id:
        The session id returned by ``extract_document``.

    Returns
    -------
    JSON string with the list of ``BibleValidationResult`` objects.
    """
    session = get_session(session_id)
    structure = DocumentStructure(**session["document"])

    validator = BibleValidator(use_online=True)
    results = await validator.validate(structure)

    # Persist results in session so write_corrected_docx can use them later
    update_session(
        session_id,
        {"bible_validation_results": [r.model_dump() for r in results]},
    )

    payload = {
        "session_id": session_id,
        "total_references": len(results),
        "valid": sum(1 for r in results if r.is_valid),
        "invalid": sum(1 for r in results if not r.is_valid),
        "results": [r.model_dump() for r in results],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
