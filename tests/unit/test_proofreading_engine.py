"""Unit tests for rule-based proofreading checkers."""

from __future__ import annotations

import pytest

from mcp_lektor.config.settings import load_confused_words, load_typography_rules
from mcp_lektor.core.confused_words_checker import scan_confused_words
from mcp_lektor.core.enums import ConfidenceLevel, CorrectionCategory, ParagraphType
from mcp_lektor.core.models import (
    DocumentParagraph,
    DocumentStructure,
    ProposedCorrection,
    RunFormatting,
    TextRun,
)
from mcp_lektor.core.typography_checker import check_typography


def _make_structure(texts: list[str]) -> DocumentStructure:
    """Helper: build a DocumentStructure from plain text strings."""
    paragraphs = []
    for i, text in enumerate(texts):
        paragraphs.append(
            DocumentParagraph(
                index=i,
                paragraph_type=ParagraphType.BODY,
                runs=[TextRun(text=text, formatting=RunFormatting())],
            )
        )
    return DocumentStructure(
        filename="test.docx",
        paragraphs=paragraphs,
        total_paragraphs=len(paragraphs),
        total_words=sum(len(t.split()) for t in texts),
    )


class TestTypographyChecker:
    """Tests for typography_checker.check_typography."""

    def test_detects_straight_dash(self):
        structure = _make_structure(["Das ist - ein Test."])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        dash_corrections = [
            c for c in corrections if "Gedankenstrich" in (c.rule_reference or "")
        ]
        assert len(dash_corrections) >= 1
        assert dash_corrections[0].suggested_text == " \u2013 "

    def test_detects_ellipsis(self):
        structure = _make_structure(["Und dann..."])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        ellipsis_corrections = [
            c for c in corrections if "Ellipse" in (c.rule_reference or "")
        ]
        assert len(ellipsis_corrections) >= 1
        assert ellipsis_corrections[0].suggested_text == "\u2026"

    def test_skips_placeholder_paragraphs(self):
        para = DocumentParagraph(
            index=0,
            paragraph_type=ParagraphType.BODY,
            runs=[TextRun(text="Das ist - ein Test.", formatting=RunFormatting())],
            is_placeholder_paragraph=True,
        )
        structure = DocumentStructure(
            filename="test.docx",
            paragraphs=[para],
            total_paragraphs=1,
            total_words=5,
        )
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        assert len(corrections) == 0

    def test_no_false_positives_clean_text(self):
        structure = _make_structure(["Ein sauberer Satz ohne Fehler."])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        assert len(corrections) == 0

    def test_category_is_typography(self):
        structure = _make_structure(["Ein - Strich."])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        for c in corrections:
            assert c.category in {
                CorrectionCategory.TYPOGRAPHY,
                CorrectionCategory.QUOTATION_MARKS,
            }


class TestConfusedWordsChecker:
    """Tests for confused_words_checker.scan_confused_words."""

    def test_detects_das_dass(self):
        from mcp_lektor.config.models import ConfusedWordEntry
        structure = _make_structure(["Ich wei\u00df, das das stimmt."])
        # Manually create entry to avoid dependency on external config file
        entry = ConfusedWordEntry(
            word="das",
            confused_with="dass",
            explanation="Test explanation",
            example_correct="Test",
            example_incorrect="Test"
        )
        corrections = scan_confused_words(structure, [entry])
        assert len(corrections) >= 1
        assert any(c.category == CorrectionCategory.CONFUSED_WORD for c in corrections)

    def test_detects_standart(self):
        structure = _make_structure(["Das ist der Standart."])
        words = load_confused_words()
        corrections = scan_confused_words(structure, words)
        standart_corrections = [c for c in corrections if "Standart" in c.original_text]
        assert len(standart_corrections) >= 1

    def test_skips_placeholder_run(self):
        para = DocumentParagraph(
            index=0,
            paragraph_type=ParagraphType.BODY,
            runs=[
                TextRun(
                    text="Standart",
                    formatting=RunFormatting(),
                    is_placeholder=True,
                )
            ],
        )
        structure = DocumentStructure(
            filename="test.docx",
            paragraphs=[para],
            total_paragraphs=1,
            total_words=1,
        )
        words = load_confused_words()
        corrections = scan_confused_words(structure, words)
        assert len(corrections) == 0


class TestQuotationChecker:
    """Tests for quotation mark detection (now handled by TypographyChecker)."""

    def test_detects_straight_quotes_opening(self):
        structure = _make_structure(['Er sagte "Hallo".'])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        # Filter for quotation mark corrections
        q_corrs = [c for c in corrections if c.category == CorrectionCategory.QUOTATION_MARKS]
        assert len(q_corrs) >= 1
        # Check if it detected opening
        opening = [c for c in q_corrs if "„" in c.suggested_text]
        assert len(opening) >= 1

    def test_detects_straight_quotes_closing(self):
        structure = _make_structure(['Er sagte "Hallo".'])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        q_corrs = [c for c in corrections if c.category == CorrectionCategory.QUOTATION_MARKS]
        # Check if it detected closing (follows word/punctuation)
        closing = [c for c in q_corrs if "“" in c.suggested_text]
        assert len(closing) >= 1

    def test_correct_german_quotes_no_flag(self):
        structure = _make_structure(["Er sagte \u201eHallo\u201c zu ihr."])
        rules = load_typography_rules()
        corrections = check_typography(structure, rules)
        q_corrs = [c for c in corrections if c.category == CorrectionCategory.QUOTATION_MARKS]
        assert len(q_corrs) == 0


class TestDeduplication:
    """Tests for the deduplication logic."""

    def test_removes_exact_duplicate(self):
        from mcp_lektor.core.proofreading_engine import _deduplicate

        c1 = ProposedCorrection(
            id="",
            paragraph_index=0,
            run_index=0,
            char_offset_start=0,
            char_offset_end=5,
            original_text="test",
            suggested_text="Test",
            category=CorrectionCategory.SPELLING,
            confidence=ConfidenceLevel.MEDIUM,
            explanation="Gro\u00df",
        )
        c2 = ProposedCorrection(
            id="",
            paragraph_index=0,
            run_index=0,
            char_offset_start=0,
            char_offset_end=5,
            original_text="test",
            suggested_text="Test",
            category=CorrectionCategory.SPELLING,
            confidence=ConfidenceLevel.HIGH,
            explanation="Gro\u00df",
        )
        result = _deduplicate([c1, c2])
        assert len(result) == 1
        assert result[0].confidence == ConfidenceLevel.HIGH


class TestProofreadingEngine:
    """Tests for ProofreadingEngine with rule-based checks only."""

    @pytest.mark.asyncio
    async def test_rule_based_only(self):
        """Run engine with only rule-based categories (no LLM call)."""
        from mcp_lektor.config.models import ProofreadingConfig
        from mcp_lektor.core.proofreading_engine import ProofreadingEngine
        structure = _make_structure(
            [
                'Er sagte "Hallo" - und ging...',
            ]
        )
        config = ProofreadingConfig()
        engine = ProofreadingEngine(config)
        result = await engine.proofread(
            structure,
            checks=[
                CorrectionCategory.TYPOGRAPHY,
                CorrectionCategory.QUOTATION_MARKS,
                CorrectionCategory.CONFUSED_WORD,
            ],
        )
        assert result.total_corrections > 0
        assert result.document_filename == "test.docx"
        assert result.processing_time_seconds >= 0
        for c in result.corrections:
            assert c.id.startswith("C-")

    @pytest.mark.asyncio
    async def test_empty_document(self):
        """Empty document should produce zero corrections."""
        from mcp_lektor.config.models import ProofreadingConfig
        from mcp_lektor.core.proofreading_engine import ProofreadingEngine
        structure = _make_structure([])
        config = ProofreadingConfig()
        engine = ProofreadingEngine(config)
        result = await engine.proofread(
            structure,
            checks=[CorrectionCategory.TYPOGRAPHY],
        )
        assert result.total_corrections == 0
