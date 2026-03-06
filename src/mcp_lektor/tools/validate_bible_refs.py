"""MCP tool: validate Bible references found in the document text."""

from __future__ import annotations

import json
import logging

from mcp_lektor.core.bible_validator import BibleValidator
from mcp_lektor.core.session_manager import session_manager

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
    try:
        session = session_manager.get_session(session_id)
        structure = session["structure"]

        validator = BibleValidator(use_online=True)
        results = await validator.validate(structure)

        # Persist results in session so write_corrected_docx can use them later
        session_manager.update_session(
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
    except KeyError as e:
        logger.warning(f"Session not found: {session_id}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error validating Bible references in session {session_id}: {e}")
        return json.dumps({"error": f"Internal error: {str(e)}"}, ensure_ascii=False)
