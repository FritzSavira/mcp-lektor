"""Shared enumerations for MCP Lektor."""

from enum import Enum


class ParagraphType(str, Enum):
    """Types of paragraphs in a Word document."""
    HEADING = "heading"
    BODY = "body"
    LIST_ITEM = "list_item"
    TABLE_CELL = "table_cell"
    HEADER = "header"
    FOOTER = "footer"


class CorrectionCategory(str, Enum):
    """Categories of proofreading corrections."""
    SPELLING = "Rechtschreibung"
    GRAMMAR = "Grammatik"
    PUNCTUATION = "Zeichensetzung"
    TYPOGRAPHY = "Typografie"
    QUOTATION_MARKS = "Anfuehrungszeichen"
    ADDRESS_FORM = "Anrede-Konsistenz"
    CONFUSED_WORD = "Verwechslungswort"
    BIBLE_REFERENCE = "Bibelstelle"


class ConfidenceLevel(str, Enum):
    """Confidence level of a proposed correction."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CorrectionDecision(str, Enum):
    """User decision on a proposed correction."""
    ACCEPT = "accept"
    REJECT = "reject"
    EDIT = "edit"
