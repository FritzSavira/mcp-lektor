"""Integration tests for the extract_document MCP tool."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_lektor.core.session_manager import session_manager
from mcp_lektor.tools.extract_document import extract_document


@pytest.fixture(autouse=True)
def _clean_sessions():
    """Ensure a clean session store for every test."""
    session_manager._sessions.clear()
    yield
    session_manager._sessions.clear()


class TestExtractDocumentTool:
    """Integration tests that call extract_document end-to-end."""

    @pytest.mark.asyncio
    async def test_returns_valid_json(self, sample_docx_path: Path) -> None:
        raw = await extract_document(str(sample_docx_path))
        data = json.loads(raw)
        assert "session_id" in data
        assert "document" in data

    @pytest.mark.asyncio
    async def test_session_created(self, sample_docx_path: Path) -> None:
        raw = await extract_document(str(sample_docx_path))
        sid = json.loads(raw)["session_id"]
        session = session_manager.get_session(sid)
        assert "structure" in session

    @pytest.mark.asyncio
    async def test_document_fields(self, sample_docx_path: Path) -> None:
        raw = await extract_document(str(sample_docx_path))
        doc = json.loads(raw)["document"]
        assert doc["filename"] == "sample_formatted.docx"
        assert doc["total_paragraphs"] == 4
        assert doc["placeholder_count"] == 1

    @pytest.mark.asyncio
    async def test_file_not_found(self, tmp_dir: Path) -> None:
        # Note: In the tool, we wrap parse_docx in a try/except that returns a JSON error
        raw = await extract_document(str(tmp_dir / "nope.docx"))
        data = json.loads(raw)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_extract_via_base64(self, sample_docx_path: Path) -> None:
        """Verify that documents can be uploaded via Base64 content."""
        import base64

        # Read the fixture file
        file_bytes = sample_docx_path.read_bytes()
        encoded = base64.b64encode(file_bytes).decode("utf-8")

        # Call tool with file_content instead of file_path
        raw = await extract_document(file_content=encoded, filename="base64_upload.docx")
        data = json.loads(raw)

        # Assertions
        assert "session_id" in data, f"Response should contain session_id. Got: {data}"
        assert "document" in data

        # Verify session was created
        sid = data["session_id"]
        session = session_manager.get_session(sid)
        assert session is not None
        assert "structure" in session
        assert len(session["temp_files"]) > 0  # Should track the temp file
