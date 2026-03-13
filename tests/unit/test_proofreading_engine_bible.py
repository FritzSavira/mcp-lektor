"""Unit tests for the Bible integration in ProofreadingEngine (Local version)."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from mcp_lektor.core.proofreading_engine import ProofreadingEngine
from mcp_lektor.core.enums import CorrectionCategory
from mcp_lektor.core.models import (
    DocumentParagraph,
    DocumentStructure,
    TextRun,
)
from mcp_lektor.core.bible_provider import BibleProvider

class TestProofreadingEngineBible:
    """Tests for Bible reference validation within the ProofreadingEngine."""

    def _make_structure(self, texts: list[str]) -> DocumentStructure:
        paras = []
        for i, t in enumerate(texts):
            # Split text into multiple runs to test run_index finding
            if "Gen 1,1" in t:
                parts = t.split("Gen 1,1")
                runs = [
                    TextRun(text=parts[0]),
                    TextRun(text="Gen 1,1"),
                    TextRun(text=parts[1])
                ]
            else:
                runs = [TextRun(text=t)]
                
            paras.append(
                DocumentParagraph(
                    index=i,
                    runs=runs,
                )
            )
        return DocumentStructure(
            filename="test.docx",
            paragraphs=paras,
            total_paragraphs=len(paras),
        )

    @pytest.mark.asyncio
    async def test_bible_integration_success(self, mocker):
        """Test that Bible references are integrated into proofread result with local texts."""
        # Mock BibleProvider
        mock_provider = MagicMock(spec=BibleProvider)
        mock_provider.exists.return_value = True
        mock_provider.normalize_book_name.return_value = "GEN"
        mock_provider.get_texts.return_value = {
            "menge": "Am Anfang...",
            "neu": "Im Anfang..."
        }
        
        # Patch BibleValidator to use our mock provider
        mocker.patch("mcp_lektor.core.bible_validator.BibleProvider", return_value=mock_provider)
        
        engine = ProofreadingEngine()
        structure = self._make_structure(["Lies Gen 1,1 heute."])
        
        result = await engine.proofread(structure, checks=[CorrectionCategory.BIBLE_REFERENCE])
        
        assert result.total_corrections == 1
        corr = result.corrections[0]
        assert corr.category == CorrectionCategory.BIBLE_REFERENCE
        assert corr.original_text == "Gen 1,1"
        assert "verifiziert" in corr.explanation
        assert "Menge: \"Am Anfang...\"" in corr.explanation
        assert "Neu: \"Im Anfang...\"" in corr.explanation

    @pytest.mark.asyncio
    async def test_bible_integration_error(self, mocker):
        """Test that invalid Bible references are marked as errors in proofread result."""
        # Mock BibleProvider
        mock_provider = MagicMock(spec=BibleProvider)
        mock_provider.exists.return_value = False
        
        mocker.patch("mcp_lektor.core.bible_validator.BibleProvider", return_value=mock_provider)
        
        engine = ProofreadingEngine()
        para = DocumentParagraph(index=0, runs=[TextRun(text="Lies Gen 60.")])
        structure = DocumentStructure(filename="test.docx", paragraphs=[para], total_paragraphs=1)
        
        result = await engine.proofread(structure, checks=[CorrectionCategory.BIBLE_REFERENCE])
        
        assert result.total_corrections == 1
        corr = result.corrections[0]
        assert "FEHLER" in corr.explanation
        assert "Stelle existiert nicht" in corr.explanation
