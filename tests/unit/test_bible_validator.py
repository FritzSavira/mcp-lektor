"""Unit tests for the Bible reference validator (Local version)."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from mcp_lektor.core.bible_validator import BibleValidator
from mcp_lektor.core.bible_provider import BibleProvider
from mcp_lektor.core.models import (
    BibleReference,
    DocumentParagraph,
    DocumentStructure,
    RunFormatting,
    TextColor,
    TextRun,
)
from mcp_lektor.utils.bible_patterns import extract_references

# ───────────────────────── Regex extraction ─────────────────────────

class TestBiblePatterns:
    """Tests for bible_patterns.extract_references."""

    def test_simple_reference(self):
        refs = extract_references("Lies Mt 5,3 und sei gesegnet.")
        assert len(refs) == 1
        assert refs[0]["book"] == "Mt"
        assert refs[0]["chapter"] == 5
        assert refs[0]["verse_start"] == 3
        assert refs[0]["verse_end"] is None

    def test_verse_range(self):
        refs = extract_references("In 1. Kor 13,4-7 steht die Liebe.")
        assert len(refs) == 1
        assert refs[0]["book"] == "1. Kor"
        assert refs[0]["chapter"] == 13
        assert refs[0]["verse_start"] == 4
        assert refs[0]["verse_end"] == 7

    def test_multiple_references(self):
        text = "Vgl. Gen 1,1 und Offb 22,21."
        refs = extract_references(text)
        assert len(refs) == 2
        books = {r["book"] for r in refs}
        assert books == {"Gen", "Offb"}

# ───────────────────────── BibleValidator integration ─────────────────

class TestBibleValidatorLocal:
    """Tests for BibleValidator with local lookup."""

    def _make_structure(self, texts: list[str]) -> DocumentStructure:
        paras = []
        for i, t in enumerate(texts):
            paras.append(
                DocumentParagraph(
                    index=i,
                    runs=[TextRun(text=t)],
                )
            )
        return DocumentStructure(
            filename="test.docx",
            paragraphs=paras,
            total_paragraphs=len(paras),
        )

    @pytest.mark.asyncio
    async def test_validate_success(self):
        """Test successful local validation."""
        mock_provider = MagicMock(spec=BibleProvider)
        mock_provider.exists.return_value = True
        mock_provider.normalize_book_name.return_value = "GEN"
        mock_provider.get_texts.return_value = {"menge": "Am Anfang..."}
        
        structure = self._make_structure(["Gen 1,1"])
        validator = BibleValidator(provider=mock_provider)
        results = await validator.validate(structure)
        
        assert len(results) == 1
        assert results[0].is_valid is True
        assert results[0].local_texts["menge"] == "Am Anfang..."
        mock_provider.exists.assert_called_with("Gen", 1, 1)

    @pytest.mark.asyncio
    async def test_validate_fail(self):
        """Test local validation failure for non-existent verse."""
        mock_provider = MagicMock(spec=BibleProvider)
        mock_provider.exists.return_value = False
        
        structure = self._make_structure(["Gen 60,1"])
        validator = BibleValidator(provider=mock_provider)
        results = await validator.validate(structure)
        
        assert len(results) == 1
        assert results[0].is_valid is False
        assert "nicht in der Menge-Bibel" in results[0].error_message

    def test_get_bibelserver_url(self):
        from mcp_lektor.config.models import BibleTranslationEntry, ProofreadingConfig
        config = ProofreadingConfig()
        config.bible_translations = {
            "LUT": BibleTranslationEntry(label="Luther", enabled=True),
        }
        validator = BibleValidator(config=config)
        ref = BibleReference(
            paragraph_index=0,
            raw_text="Gen 1,1",
            book="Gen",
            chapter=1,
            verse_start=1,
        )
        url = validator.get_bibelserver_url(ref, "LUT")
        # bibleserver slug for Gen is 1-mose
        assert url == "https://www.bibleserver.com/LUT/1-mose1,1"

    def test_skips_placeholder_paragraphs(self):
        para = DocumentParagraph(
            index=0,
            runs=[
                TextRun(
                    text="Mt 5,3",
                    is_placeholder=True,
                )
            ],
            is_placeholder_paragraph=True,
        )
        structure = DocumentStructure(
            filename="test.docx",
            paragraphs=[para],
            total_paragraphs=1,
        )
        validator = BibleValidator()
        refs = validator.extract_refs(structure)
        assert len(refs) == 0
