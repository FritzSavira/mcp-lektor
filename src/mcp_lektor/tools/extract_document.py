"""MCP tool: extract_document – parse a .docx and store a session."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from mcp_lektor.core.document_io import parse_docx
from mcp_lektor.core.session_manager import session_manager

logger = logging.getLogger(__name__)

async def extract_document(file_path: str) -> str:
    """Read a .docx file and return a structured representation.

    Creates an in-memory session so subsequent tools can reference
    the parsed document via ``session_id``.
    """
    try:
        path = Path(file_path)
        if not path.is_absolute():
            # In a real MCP environment, we'd need to handle relative paths 
            # based on the workspace root.
            pass

        structure = parse_docx(path)

        session_id = session_manager.create_session(
            {
                "file_path": str(path),
                "structure": structure,
            }
        )

        result = {
            "session_id": session_id,
            "document": structure.model_dump(),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error extracting document {file_path}: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
