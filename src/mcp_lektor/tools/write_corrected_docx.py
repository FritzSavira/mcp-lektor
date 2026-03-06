"""Write accepted corrections back into the .docx with Track Changes."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from mcp_lektor.core.document_io import write_corrected_document

logger = logging.getLogger(__name__)

# Imported at module level so the server can register it
SESSION_STORE: dict[str, dict[str, Any]] = {}


async def write_corrected_docx(
    session_id: str,
    decisions: str = "",
    apply_all: bool = True,
    author: str = "MCP-Lektor",
) -> dict[str, Any]:
    """MCP tool: write corrections into the document as Track Changes.

    Args:
        session_id: The session identifier from extract_document.
        decisions: JSON string mapping correction index to
            "accept"/"reject"/"edit". Ignored if apply_all is True.
        apply_all: If True, apply all corrections regardless of decisions.
        author: Author name for Track Changes metadata.

    Returns:
        Dict with output_path, corrections_applied count, and status.
    """
    if session_id not in SESSION_STORE:
        return {
            "status": "error",
            "message": f"Session '{session_id}' not found. "
            "Please run extract_document first.",
        }

    session = SESSION_STORE[session_id]
    input_path = session.get("file_path")
    corrections = session.get("corrections", [])

    if not input_path or not Path(input_path).exists():
        return {
            "status": "error",
            "message": "Original document file not found in session.",
        }

    if not corrections:
        return {
            "status": "error",
            "message": "No corrections found. Please run proofread_text first.",
        }

    # Parse decisions
    decision_map: dict[int, str] | None = None
    if not apply_all and decisions:
        try:
            raw = json.loads(decisions)
            decision_map = {int(k): v for k, v in raw.items()}
        except (json.JSONDecodeError, ValueError) as exc:
            return {
                "status": "error",
                "message": f"Invalid decisions JSON: {exc}",
            }

    # Generate output path
    input_p = Path(input_path)
    output_path = input_p.parent / f"{input_p.stem}_corrected{input_p.suffix}"

    try:
        result_path = write_corrected_document(
            input_path=input_path,
            output_path=output_path,
            corrections=corrections,
            author=author,
            decisions=decision_map,
        )
    except Exception as exc:
        logger.exception("Failed to write corrected document")
        return {
            "status": "error",
            "message": f"Failed to write document: {exc}",
        }

    # Count applied
    if decision_map is not None:
        applied = sum(1 for v in decision_map.values() if v != "reject")
    else:
        applied = len(corrections)

    # Store output path in session
    session["output_path"] = str(result_path)

    return {
        "status": "success",
        "output_path": str(result_path),
        "corrections_applied": applied,
        "corrections_total": len(corrections),
        "message": (
            f"{applied} von {len(corrections)} Korrekturen wurden als "
            f"Track Changes in '{result_path.name}' geschrieben."
        ),
    }
