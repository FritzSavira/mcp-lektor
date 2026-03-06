"""Unit tests for Pydantic data models."""

from mcp_lektor.core.models import (
    ConfidenceLevel,
    CorrectionCategory,
    DocumentParagraph,
    DocumentStructure,
    RunFormatting,
    TextColor,
    TextRun,
)


class TestTextColor:
    def test_is_red_true(self) -> None:
        color = TextColor(r=255, g=0, b=0)
        assert color.is_red is True

    def test_is_red_false_black(self) -> None:
        color = TextColor(r=0, g=0, b=0)
        assert color.is_red is False

    def test_is_red_false_blue(self) -> None:
        color = TextColor(r=0, g=0, b=255)
        assert color.is_red is False

    def test_is_red_boundary(self) -> None:
        color = TextColor(r=180, g=80, b=80)
        assert color.is_red is False

    def test_is_red_just_above_boundary(self) -> None:
        color = TextColor(r=181, g=79, b=79)
        assert color.is_red is True


class TestTextRun:
    def test_is_red_text(self) -> None:
        run = TextRun(
            text="Platzhalter",
            formatting=RunFormatting(color=TextColor(r=255, g=0, b=0)),
        )
        assert run.is_red_text is True

    def test_is_not_red_text(self) -> None:
        run = TextRun(text="Normal")
        assert run.is_red_text is False


class TestDocumentParagraph:
    def test_plain_text(self) -> None:
        para = DocumentParagraph(
            index=0,
            runs=[
                TextRun(text="Hello "),
                TextRun(text="World"),
            ],
        )
        assert para.plain_text == "Hello World"

    def test_proofreadable_text_excludes_placeholders(self) -> None:
        para = DocumentParagraph(
            index=0,
            runs=[
                TextRun(text="Normaler Text "),
                TextRun(text="[PLATZHALTER]", is_placeholder=True),
                TextRun(text=" und weiter."),
            ],
        )
        assert para.proofreadable_text == "Normaler Text  und weiter."


class TestDocumentStructure:
    def test_empty_structure(self) -> None:
        ds = DocumentStructure(filename="test.docx")
        assert ds.total_paragraphs == 0
        assert ds.total_words == 0
        assert ds.placeholder_count == 0


class TestCorrectionCategory:
    def test_all_categories_exist(self) -> None:
        expected = {
            "Rechtschreibung",
            "Grammatik",
            "Zeichensetzung",
            "Typografie",
            "Anfuehrungszeichen",
            "Anrede-Konsistenz",
            "Verwechslungswort",
            "Bibelstelle",
        }
        actual = {c.value for c in CorrectionCategory}
        assert actual == expected


class TestConfidenceLevel:
    def test_all_levels(self) -> None:
        assert set(ConfidenceLevel) == {
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.LOW,
        }
