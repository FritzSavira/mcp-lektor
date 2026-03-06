"""Integration tests for the proofread_text MCP tool."""

from __future__ import annotations

import json

import pytest

from mcp_lektor.core.models import (
    DocumentParagraph,
    DocumentStructure,
    ParagraphType,
    RunFormatting,
    TextRun,
)
from mcp_lektor.core.session_manager import session_manager
from mcp_lektor.tools.proofread_text import proofread_text


def _make_session_with_text(texts: list[str]) -> str:
    """Create a session with a DocumentStructure and return the session_id."""
    paragraphs = []
    for i, text in enumerate(texts):
        paragraphs.append(
            DocumentParagraph(
                index=i,
                paragraph_type=ParagraphType.BODY,
                runs=[TextRun(text=text, formatting=RunFormatting())],
            )
        )
    structure = DocumentStructure(
        filename="integration_test.docx",
        paragraphs=paragraphs,
        total_paragraphs=len(paragraphs),
        total_words=sum(len(t.split()) for t in texts),
    )
    return session_manager.create_session({"structure": structure, "file_path": "fake.docx"})


@pytest.fixture(autouse=True)
def _clean_sessions():
    session_manager._sessions.clear()
    yield
    session_manager._sessions.clear()


class TestProofreadTextTool:
    """Integration tests for the proofread_text tool."""

    @pytest.mark.asyncio
    async def test_returns_valid_json(self):
        sid = _make_session_with_text(['Er sagte "Hallo" - und ging...'])
        result_str = await proofread_text(
            session_id=sid,
            checks="typography,quotation",
        )
        result = json.loads(result_str)
        assert "total_corrections" in result
        assert "corrections" in result
        assert result["total_corrections"] > 0

    @pytest.mark.asyncio
    async def test_session_not_found(self):
        result_str = await proofread_text(session_id="nonexistent")
        result = json.loads(result_str)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_result_stored_in_session(self):
        sid = _make_session_with_text(["Das ist - ein Test."])
        await proofread_text(session_id=sid, checks="typography")
        session = session_manager.get_session(sid)
        assert "proofreading_result" in session

    @pytest.mark.asyncio
    async def test_selective_checks(self):
        sid = _make_session_with_text(["Ein sauberer Satz."])
        result_str = await proofread_text(
            session_id=sid,
            checks="typography",
        )
        result = json.loads(result_str)
        assert result["total_corrections"] == 0

    @pytest.mark.asyncio
    async def test_all_corrections_have_ids(self):
        sid = _make_session_with_text(['Er sagte "Hallo" - und ging...'])
        result_str = await proofread_text(session_id=sid, checks="typography,quotation")
        result = json.loads(result_str)
        for c in result["corrections"]:
            assert c["id"].startswith("C-")
