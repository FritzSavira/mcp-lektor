"""Unit tests for the Bible reference validator."""

from __future__ import annotations

import pytest

from mcp_lektor.core.bible_validator import BibleValidator, _validate_offline
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


# ───────────────────────── Offline validation ─────────────────────────


class TestOfflineValidation:
    """Tests for _validate_offline."""

    def test_valid_reference(self):
        ref = BibleReference(
            paragraph_index=0,
            raw_text="Gen 1,1",
            book="Gen",
            chapter=1,
            verse_start=1,
        )
        result = _validate_offline(ref)
        assert result.is_valid is True

    def test_chapter_out_of_range(self):
        ref = BibleReference(
            paragraph_index=0,
            raw_text="Gen 99,1",
            book="Gen",
            chapter=99,
            verse_start=1,
        )
        result = _validate_offline(ref)
        assert result.is_valid is False
        assert "50 Kapitel" in result.error_message

    def test_unknown_book(self):
        ref = BibleReference(
            paragraph_index=0,
            raw_text="Xyz 1,1",
            book="Xyz",
            chapter=1,
        )
        result = _validate_offline(ref)
        assert result.is_valid is False
        assert "Unbekanntes Buch" in result.error_message

    def test_chapter_zero_invalid(self):
        ref = BibleReference(
            paragraph_index=0,
            raw_text="Mt 0,1",
            book="Mt",
            chapter=0,
            verse_start=1,
        )
        result = _validate_offline(ref)
        assert result.is_valid is False


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


# ───────────────────────── Async validate (offline) ──────────────────


class TestBibleValidatorOffline:
    """Tests for BibleValidator.validate with use_online=False."""

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
    async def test_valid_refs_offline(self):
        structure = self._make_structure(["Mt 5,3 und Ps 23"])
        validator = BibleValidator(use_online=False)
        results = await validator.validate(structure)
        assert len(results) == 2
        assert all(r.is_valid for r in results)

    @pytest.mark.asyncio
    async def test_invalid_chapter_offline(self):
        structure = self._make_structure(["Gen 99,1"])
        validator = BibleValidator(use_online=False)
        results = await validator.validate(structure)
        assert len(results) == 1
        assert results[0].is_valid is False

    @pytest.mark.asyncio
    async def test_empty_document_returns_empty(self):
        structure = self._make_structure([])
        validator = BibleValidator(use_online=False)
        results = await validator.validate(structure)
        assert results == []
