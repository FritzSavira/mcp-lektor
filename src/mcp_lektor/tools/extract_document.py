"""MCP tool: extract_document – parse a .docx and store a session."""

from __future__ import annotations

import base64
import json
import logging
import tempfile
from pathlib import Path
from uuid import uuid4

from mcp_lektor.core.document_io import parse_docx
from mcp_lektor.core.session_manager import session_manager

logger = logging.getLogger(__name__)

async def extract_document(
    file_path: str | None = None,
    file_content: str | None = None,
    filename: str | None = "document.docx"
) -> str:
    """Read a .docx file and return a structured representation.

    Can accept either a local file path (local mode) or a Base64-encoded
    content string (cloud/remote mode).

    Creates an in-memory session so subsequent tools can reference
    the parsed document via ``session_id``.
    """
    try:
        temp_files_to_track = []

        if file_content:
            # Decode base64
            try:
                file_data = base64.b64decode(file_content)
            except Exception as e:
                return json.dumps(
                    {"error": f"Invalid base64 content: {e}"}, ensure_ascii=False
                )

            # Create temp directory
            temp_dir = Path(tempfile.gettempdir()) / "mcp_lektor"
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create temp file with unique name
            safe_filename = Path(filename).name
            unique_name = f"upload_{uuid4().hex}_{safe_filename}"
            temp_path = temp_dir / unique_name

            # Write to file
            temp_path.write_bytes(file_data)
            path = temp_path
            temp_files_to_track.append(str(path))

            logger.info(f"Saved Base64 content to temporary file: {path}")

        elif file_path:
            path = Path(file_path)
            if not path.is_absolute():
                # In a real MCP environment, we'd need to handle relative paths
                # based on the workspace root.
                path = path.resolve()
        else:
            return json.dumps(
                {"error": "Either file_path or file_content must be provided"},
                ensure_ascii=False,
            )

        structure = parse_docx(path)

        session_id = session_manager.create_session(
            {
                "file_path": str(path),
                "structure": structure,
                "temp_files": temp_files_to_track,
            }
        )

        result = {
            "session_id": session_id,
            "document": structure.model_dump(),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error extracting document: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
