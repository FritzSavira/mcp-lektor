"""Pydantic data models for MCP Lektor."""

from typing import Optional

from pydantic import BaseModel, Field

from mcp_lektor.core.enums import (
    ConfidenceLevel,
    CorrectionCategory,
    CorrectionDecision,
    ParagraphType,
)


class TextColor(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

    @property
    def is_red(self) -> bool:
        return self.r > 180 and self.g < 80 and self.b < 80


class RunFormatting(BaseModel):
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    color: Optional[TextColor] = None
    highlight: Optional[str] = None
    style_name: Optional[str] = None


class TextRun(BaseModel):
    text: str
    formatting: RunFormatting = Field(default_factory=RunFormatting)
    is_placeholder: bool = False

    @property
    def is_red_text(self) -> bool:
        return self.formatting.color is not None and self.formatting.color.is_red


class DocumentParagraph(BaseModel):
    index: int
    paragraph_type: ParagraphType = ParagraphType.BODY
    style_name: Optional[str] = None
    heading_level: Optional[int] = None
    runs: list[TextRun] = Field(default_factory=list)
    is_placeholder_paragraph: bool = False

    @property
    def plain_text(self) -> str:
        return "".join(run.text for run in self.runs)

    @property
    def proofreadable_text(self) -> str:
        return "".join(run.text for run in self.runs if not run.is_placeholder)


class DocumentStructure(BaseModel):
    filename: str
    paragraphs: list[DocumentParagraph] = Field(default_factory=list)
    total_paragraphs: int = 0
    total_words: int = 0
    placeholder_count: int = 0
    placeholder_locations: list[str] = Field(default_factory=list)


class ProposedCorrection(BaseModel):
    id: str
    paragraph_index: int
    run_index: int
    char_offset_start: int
    char_offset_end: int
    original_text: str
    suggested_text: str
    category: CorrectionCategory
    confidence: ConfidenceLevel
    explanation: str
    rule_reference: Optional[str] = None


class ProofreadingResult(BaseModel):
    document_filename: str
    total_corrections: int = 0
    corrections: list[ProposedCorrection] = Field(default_factory=list)
    predominant_address_form: Optional[str] = None
    address_form_deviations: int = 0
    placeholder_summary: str = ""
    processing_time_seconds: float = 0.0

    @property
    def high_confidence(self) -> list[ProposedCorrection]:
        return [c for c in self.corrections if c.confidence == ConfidenceLevel.HIGH]

    @property
    def medium_confidence(self) -> list[ProposedCorrection]:
        return [c for c in self.corrections if c.confidence == ConfidenceLevel.MEDIUM]

    @property
    def low_confidence(self) -> list[ProposedCorrection]:
        return [c for c in self.corrections if c.confidence == ConfidenceLevel.LOW]


class BibleReference(BaseModel):
    paragraph_index: int
    raw_text: str
    book: str
    chapter: int
    verse_start: Optional[int] = None
    verse_end: Optional[int] = None


class BibleValidationResult(BaseModel):
    reference: BibleReference
    is_valid: bool
    error_message: Optional[str] = None
    suggested_correction: Optional[str] = None
    source_url: Optional[str] = None
    comparison_links: dict[str, str] = Field(default_factory=dict)


class UserDecision(BaseModel):
    correction_id: str
    decision: CorrectionDecision
    edited_text: Optional[str] = None


class WriteRequest(BaseModel):
    document_session_id: str
    decisions: list[UserDecision] = Field(default_factory=list)
    apply_all: bool = False
