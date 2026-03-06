"""Integration tests for the write_corrected_docx tool."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from docx import Document as DocxDocument

from mcp_lektor.tools.write_corrected_docx import (
    SESSION_STORE,
    write_corrected_docx,
)


def _create_test_docx(
    path: Path, text: str = "Dies ist ein Testtext mit Fehler."
) -> Path:
    """Create a simple test .docx file."""
    doc = DocxDocument()
    doc.add_paragraph(text)
    doc.save(str(path))
    return path


def _setup_session(session_id: str, file_path: Path) -> None:
    """Set up a fake session with corrections."""
    SESSION_STORE[session_id] = {
        "file_path": str(file_path),
        "corrections": [
            {
                "paragraph_index": 0,
                "run_index": 0,
                "char_start": 27,
                "char_end": 33,
                "original_text": "Fehler",
                "replacement_text": "Erfolg",
                "category": "Rechtschreibung",
                "explanation": "Testkorrektur",
            },
        ],
    }


@pytest.mark.asyncio
class TestWriteCorrectedDocx:
    """Integration tests for the write_corrected_docx MCP tool."""

    async def test_apply_all_mode(self, tmp_path: Path) -> None:
        docx_path = _create_test_docx(tmp_path / "test.docx")
        _setup_session("test-session-1", docx_path)

        result = await write_corrected_docx(
            session_id="test-session-1",
            apply_all=True,
        )

        assert result["status"] == "success"
        assert result["corrections_applied"] == 1
        assert Path(result["output_path"]).exists()

    async def test_selective_decisions(self, tmp_path: Path) -> None:
        docx_path = _create_test_docx(tmp_path / "test2.docx")
        _setup_session("test-session-2", docx_path)

        decisions = json.dumps({"0": "reject"})
        result = await write_corrected_docx(
            session_id="test-session-2",
            decisions=decisions,
            apply_all=False,
        )

        assert result["status"] == "success"
        assert result["corrections_applied"] == 0

    async def test_missing_session(self) -> None:
        result = await write_corrected_docx(session_id="nonexistent")
        assert result["status"] == "error"
        assert "not found" in result["message"]

    async def test_no_corrections(self, tmp_path: Path) -> None:
        docx_path = _create_test_docx(tmp_path / "test3.docx")
        SESSION_STORE["empty-session"] = {
            "file_path": str(docx_path),
            "corrections": [],
        }

        result = await write_corrected_docx(session_id="empty-session")
        assert result["status"] == "error"
        assert "No corrections" in result["message"]

    async def test_output_opens_in_docx(self, tmp_path: Path) -> None:
        docx_path = _create_test_docx(tmp_path / "test4.docx")
        _setup_session("test-session-4", docx_path)

        result = await write_corrected_docx(session_id="test-session-4")
        assert result["status"] == "success"

        # Verify the output is a valid .docx
        output = DocxDocument(result["output_path"])
        assert len(output.paragraphs) > 0
