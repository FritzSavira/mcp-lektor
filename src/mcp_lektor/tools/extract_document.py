"""
MCP Tool: extract_document – Parse a .docx document and start a proofreading session.

This tool is the entry point for the proofreading workflow. It reads a Word document,
extracts its content (paragraphs, comments, track changes), and stores it in a temporary
session.

Parameters:
- file_content (str | None): Base64-encoded content of the .docx file.
  REQUIRED for cloud environments (Langdock, Straico, Remote MCP).
- file_path (str | None): Local file path to the .docx file.
  ONLY for local development or when the server has direct file access.
- filename (str | None): Optional filename for the uploaded document (default: "document.docx").

Returns:
- JSON string containing:
  - session_id: UUID to be used in subsequent tool calls (proofread_text, validate_bible_refs).
  - document: Structured representation of the document content.
"""

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
    file_content: str | None = None,
    file_path: str | None = None,
    filename: str | None = "document.docx"
) -> str:
    """Parse a .docx document and start a proofreading session.

    CRITICAL: For cloud environments like Langdock or Straico, ALWAYS use 'file_content'.
    DO NOT use 'file_path' unless the server is running on your local machine.

    Args:
        file_content: REQUIRED FOR CLOUD. The Base64-encoded content of the .docx file.
        file_path: ONLY FOR LOCAL DEV. Absolute path to a local .docx file.
        filename: Optional name for the file (e.g. "sermon.docx").

    Returns:
        JSON with 'session_id' and 'document' structure.
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
