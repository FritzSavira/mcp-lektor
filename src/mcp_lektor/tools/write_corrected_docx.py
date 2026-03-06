"""Write accepted corrections back into the .docx with Track Changes."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from mcp_lektor.core.document_io import write_corrected_document
from mcp_lektor.core.session_manager import session_manager

logger = logging.getLogger(__name__)


async def write_corrected_docx(
    session_id: str,
    decisions: str = "",
    apply_all: bool = True,
    author: str = "MCP-Lektor",
) -> str:
    """MCP tool: write corrections into the document as Track Changes.

    Args:
        session_id: The session identifier from extract_document.
        decisions: JSON string mapping correction index to
            "accept"/"reject"/"edit". Ignored if apply_all is True.
        apply_all: If True, apply all corrections regardless of decisions.
        author: Author name for Track Changes metadata.

    Returns:
        JSON string with output_path, corrections_applied count, and status.
    """
    try:
        session = session_manager.get_session(session_id)
        input_path = session.get("file_path")
        
        # We need the corrections from proofreading_result
        proof_result = session.get("proofreading_result")
        if not proof_result:
            return json.dumps({
                "status": "error",
                "message": "No proofreading results found in session. Please run proofread_text first."
            }, ensure_ascii=False)
        
        corrections = [c.model_dump() for c in proof_result.corrections]

        if not input_path or not Path(input_path).exists():
            return json.dumps({
                "status": "error",
                "message": "Original document file not found in session."
            }, ensure_ascii=False)

        if not corrections:
            return json.dumps({
                "status": "success",
                "message": "No corrections were proposed, nothing to write.",
                "corrections_applied": 0
            }, ensure_ascii=False)

        # Parse decisions
        decision_map: dict[int, str] | None = None
        if not apply_all and decisions:
            try:
                raw = json.loads(decisions)
                # Map "C-001" style IDs or integer indices to "accept"/"reject"/"edit"
                # The core logic expects integer indices if possible, or we might need to map them.
                # Let's assume the user provides a map where keys can be parsed as int indices.
                decision_map = {int(k): v for k, v in raw.items()}
            except (json.JSONDecodeError, ValueError) as exc:
                return json.dumps({
                    "status": "error",
                    "message": f"Invalid decisions JSON format: {exc}"
                }, ensure_ascii=False)

        # Generate output path
        input_p = Path(input_path)
        output_path = input_p.parent / f"{input_p.stem}_corrected{input_p.suffix}"

        # write_corrected_document is synchronous in core/document_io.py
        result_path = write_corrected_document(
            input_path=input_path,
            output_path=output_path,
            corrections=corrections,
            author=author,
            decisions=decision_map,
        )

        # Count applied
        if decision_map is not None:
            applied = sum(1 for v in decision_map.values() if v != "reject")
        else:
            applied = len(corrections)

        # Store output path in session
        session_manager.update_session(session_id, {"output_path": str(result_path)})

        result = {
            "status": "success",
            "output_path": str(result_path),
            "corrections_applied": applied,
            "corrections_total": len(corrections),
            "message": (
                f"{applied} von {len(corrections)} Korrekturen wurden als "
                f"Track Changes in '{result_path.name}' geschrieben."
            ),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    except KeyError as e:
        logger.warning(f"Session not found: {session_id}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    except Exception as e:
        logger.exception(f"Error writing corrected document for session {session_id}")
        return json.dumps({"error": f"Internal error: {str(e)}"}, ensure_ascii=False)
