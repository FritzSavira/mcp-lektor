"""Integration tests for the extract_document MCP tool."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_lektor.tools._session_store import clear_all, get_session
from mcp_lektor.tools.extract_document import extract_document


@pytest.fixture(autouse=True)
def _clean_sessions():
    """Ensure a clean session store for every test."""
    clear_all()
    yield
    clear_all()


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
        session = get_session(sid)
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
        with pytest.raises(FileNotFoundError):
            await extract_document(str(tmp_dir / "nope.docx"))
