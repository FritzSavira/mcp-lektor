"""Unit tests for document_io – .docx parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_lektor.core.document_io import parse_docx
from mcp_lektor.core.models import ParagraphType


class TestParseDocx:
    """Tests for the parse_docx function."""

    def test_returns_document_structure(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        assert result.filename == "sample_formatted.docx"

    def test_paragraph_count(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        # heading + normal + placeholder + italic = 4
        assert result.total_paragraphs == 4

    def test_heading_detected(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        heading = result.paragraphs[0]
        assert heading.paragraph_type == ParagraphType.HEADING
        assert heading.heading_level == 1

    def test_bold_formatting_preserved(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        body_para = result.paragraphs[1]
        bold_runs = [r for r in body_para.runs if r.formatting.bold]
        assert len(bold_runs) == 1
        assert "fettgedrucktem" in bold_runs[0].text

    def test_italic_formatting_preserved(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        italic_para = result.paragraphs[3]
        assert any(r.formatting.italic for r in italic_para.runs)

    def test_placeholder_detected(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        placeholder_para = result.paragraphs[2]
        assert placeholder_para.is_placeholder_paragraph is True

    def test_placeholder_count(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        assert result.placeholder_count == 1

    def test_placeholder_locations(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        assert "Paragraph 2" in result.placeholder_locations

    def test_red_run_is_placeholder(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        placeholder_para = result.paragraphs[2]
        red_runs = [r for r in placeholder_para.runs if r.is_placeholder]
        assert len(red_runs) >= 1

    def test_total_words_positive(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        assert result.total_words > 0

    def test_empty_document(self, empty_docx_path: Path) -> None:
        result = parse_docx(empty_docx_path)
        assert result.total_paragraphs >= 0
        assert result.placeholder_count == 0

    def test_file_not_found_raises(self, tmp_dir: Path) -> None:
        with pytest.raises(FileNotFoundError):
            parse_docx(tmp_dir / "does_not_exist.docx")

    def test_wrong_extension_raises(self, tmp_dir: Path) -> None:
        txt_path = tmp_dir / "wrong.txt"
        txt_path.write_text("hello")
        with pytest.raises(ValueError, match=".docx"):
            parse_docx(txt_path)

    def test_plain_text_assembly(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        body = result.paragraphs[1]
        assert "normaler Absatz" in body.plain_text

    def test_proofreadable_text_excludes_placeholder(
        self, sample_docx_path: Path
    ) -> None:
        result = parse_docx(sample_docx_path)
        placeholder_para = result.paragraphs[2]
        assert placeholder_para.proofreadable_text == ""

    def test_font_size_extracted(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        body = result.paragraphs[1]
        sized_runs = [r for r in body.runs if r.formatting.font_size is not None]
        assert len(sized_runs) >= 1
        assert sized_runs[0].formatting.font_size == 12.0


class TestColorExtraction:
    """Verify that run colors are extracted correctly."""

    def test_red_color_values(self, sample_docx_path: Path) -> None:
        result = parse_docx(sample_docx_path)
        placeholder_para = result.paragraphs[2]
        red_runs = [r for r in placeholder_para.runs if r.formatting.color is not None]
        assert len(red_runs) >= 1
        c = red_runs[0].formatting.color
        assert c is not None
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0
