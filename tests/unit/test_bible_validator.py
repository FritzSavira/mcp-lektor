"""Unit tests for the Bible reference validator."""

from __future__ import annotations

import pytest
import httpx

from mcp_lektor.core.bible_validator import BibleValidator
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

    def test_chapter_only(self):
        refs = extract_references("Siehe Ps 23 für Trost.")
        assert len(refs) == 1
        assert refs[0]["book"] == "Ps"
        assert refs[0]["chapter"] == 23
        assert refs[0]["verse_start"] is None

    def test_multiple_references(self):
        text = "Vgl. Gen 1,1 und Offb 22,21."
        refs = extract_references(text)
        assert len(refs) == 2
        books = {r["book"] for r in refs}
        assert books == {"Gen", "Offb"}

    def test_numbered_book_with_dot_space(self):
        refs = extract_references("1. Mose 1,1")
        assert len(refs) == 1
        assert refs[0]["book"] == "1. Mose"
        assert refs[0]["chapter"] == 1

    def test_numbered_book_without_space(self):
        refs = extract_references("2.Tim 3,16")
        assert len(refs) == 1
        assert refs[0]["book"] == "2.Tim"
        assert refs[0]["chapter"] == 3
        assert refs[0]["verse_start"] == 16

    def test_en_dash_verse_range(self):
        refs = extract_references("Mt 5,3\u201312")
        assert len(refs) == 1
        assert refs[0]["verse_start"] == 3
        assert refs[0]["verse_end"] == 12

    def test_no_reference_in_normal_text(self):
        refs = extract_references("Das ist ein ganz normaler Satz.")
        assert len(refs) == 0

    def test_colon_separator(self):
        refs = extract_references("Joh 3:16")
        assert len(refs) == 1
        assert refs[0]["chapter"] == 3
        assert refs[0]["verse_start"] == 16

    def test_full_book_name(self):
        refs = extract_references("Epheser 5, 21")
        assert len(refs) == 1
        assert refs[0]["book"] == "Epheser"
        assert refs[0]["chapter"] == 5

    def test_verse_suffix_a(self):
        refs = extract_references("Epheser 5, 21a")
        assert len(refs) == 1
        assert refs[0]["book"] == "Epheser"
        assert refs[0]["chapter"] == 5
        assert refs[0]["verse_start"] == 21
        assert refs[0]["raw_text"] == "Epheser 5, 21a"

    def test_verse_suffix_f_ff(self):
        refs = extract_references("Ps 23, 1f und Mt 5, 3ff")
        assert len(refs) == 2
        assert refs[0]["raw_text"] == "Ps 23, 1f"
        assert refs[1]["raw_text"] == "Mt 5, 3ff"

    def test_verse_range_with_suffixes(self):
        refs = extract_references("Gen 1, 1a-2b")
        assert len(refs) == 1
        assert refs[0]["verse_start"] == 1
        assert refs[0]["verse_end"] == 2
        assert refs[0]["raw_text"] == "Gen 1, 1a-2b"


# ───────────────────────── BibleValidator integration ─────────────────


class TestBibleValidatorExtraction:
    """Tests for BibleValidator.extract_refs."""

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

    def test_extracts_from_paragraphs(self):
        structure = self._make_structure(
            [
                "Lies Mt 5,3 heute.",
                "Und dann Ps 23.",
            ]
        )
        validator = BibleValidator(use_online=False)
        refs = validator.extract_refs(structure)
        assert len(refs) == 2

    def test_skips_placeholder_paragraphs(self):
        para = DocumentParagraph(
            index=0,
            runs=[
                TextRun(
                    text="Mt 5,3",
                    formatting=RunFormatting(
                        color=TextColor(r=255, g=0, b=0),
                    ),
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
        validator = BibleValidator(use_online=False)
        refs = validator.extract_refs(structure)
        assert len(refs) == 0

    def test_empty_document(self):
        structure = DocumentStructure(filename="empty.docx")
        validator = BibleValidator(use_online=False)
        refs = validator.extract_refs(structure)
        assert len(refs) == 0


class TestBibleValidatorUtils:
    """Tests for utility methods of BibleValidator."""

    def test_get_bibelserver_url(self):
        from mcp_lektor.config.models import BibleTranslationEntry, ProofreadingConfig
        config = ProofreadingConfig()
        config.bible_translations = {
            "LUT": BibleTranslationEntry(label="Luther", enabled=True),
            "EU": BibleTranslationEntry(label="Einheit", enabled=True),
        }
        validator = BibleValidator(config=config, use_online=False)
        ref = BibleReference(
            paragraph_index=0,
            raw_text="1. Mose 1,1",
            book="1. Mose",
            chapter=1,
            verse_start=1,
        )
        url = validator.get_bibelserver_url(ref, "LUT")
        assert url == "https://www.bibleserver.com/LUT/1-mose1,1"

        ref_range = BibleReference(
            paragraph_index=0,
            raw_text="Joh 3,16-18",
            book="Joh",
            chapter=3,
            verse_start=16,
            verse_end=18,
        )
        url_range = validator.get_bibelserver_url(ref_range, "EU")
        assert url_range == "https://www.bibleserver.com/EU/johannes3,16-18"

        ref_no_verse = BibleReference(
            paragraph_index=0,
            raw_text="Ps 23",
            book="Ps",
            chapter=23,
        )
        url_no_verse = validator.get_bibelserver_url(ref_no_verse, "SLT")
        assert url_no_verse == "https://www.bibleserver.com/SLT/psalm23"


# ───────────────────────── Async validate (online mock) ───────────────


class TestBibleValidatorOnline:
    """Tests for BibleValidator.validate with online mocking."""

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
    async def test_validate_offline_mode_returns_error(self):
        """Verify that disabling online validation now returns explicit errors."""
        structure = self._make_structure(["Mt 5,3"])
        validator = BibleValidator(use_online=False)
        results = await validator.validate(structure)
        assert len(results) == 1
        assert results[0].is_valid is False
        assert "deaktiviert" in results[0].error_message

    @pytest.mark.asyncio
    async def test_validate_success(self, mocker):
        """Test successful validation with matching title."""
        mock_resp = mocker.MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.text = "<title>1.Mose 1,1 | Schlachter 2000</title>"
        mock_resp.url = "https://www.bibleserver.com/SLT/1-mose1,1"
        mock_resp.raise_for_status.return_value = None
        
        mocker.patch("httpx.AsyncClient.get", return_value=mock_resp)
        
        structure = self._make_structure(["Gen 1,1"])
        validator = BibleValidator(use_online=True)
        results = await validator.validate(structure)
        
        assert len(results) == 1
        assert results[0].is_valid is True
        assert "1-mose1,1" in results[0].source_url

    @pytest.mark.asyncio
    async def test_validate_autocorrect_fail(self, mocker):
        """Test failure when Bibelserver auto-corrects to another chapter."""
        mock_resp = mocker.MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.text = "<title>1.Mose 50 | Schlachter 2000</title>"
        mock_resp.url = "https://www.bibleserver.com/SLT/1-mose60"
        mock_resp.raise_for_status.return_value = None
        
        mocker.patch("httpx.AsyncClient.get", return_value=mock_resp)
        
        structure = self._make_structure(["Gen 60"])
        validator = BibleValidator(use_online=True)
        results = await validator.validate(structure)
        
        assert len(results) == 1
        assert results[0].is_valid is False
        assert "existiert nicht" in results[0].error_message
        assert "1.Mose 50" in results[0].error_message

    @pytest.mark.asyncio
    async def test_validate_network_error(self, mocker):
        """Test behavior on network failure."""
        mocker.patch("httpx.AsyncClient.get", side_effect=httpx.ConnectTimeout("Timeout"))
        
        structure = self._make_structure(["Mt 5,3"])
        validator = BibleValidator(use_online=True)
        results = await validator.validate(structure)
        
        assert len(results) == 1
        assert results[0].is_valid is False
        assert "nicht erreichbar" in results[0].error_message
