"""MCP tool: extract_document – parse a .docx and store a session."""

from __future__ import annotations

import json

from mcp_lektor.core.document_io import parse_docx
from mcp_lektor.tools._session_store import create_session


async def extract_document(file_path: str) -> str:
    """Read a .docx file and return a structured representation.

    Creates an in-memory session so subsequent tools can reference
    the parsed document via ``session_id``.
    """
    structure = parse_docx(file_path)

    session_id = create_session(
        {
            "file_path": file_path,
            "structure": structure,
        }
    )

    result = {
        "session_id": session_id,
        "document": structure.model_dump(),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
