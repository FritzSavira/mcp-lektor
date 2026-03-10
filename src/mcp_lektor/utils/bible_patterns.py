"""Regex patterns for detecting Bible references in German text."""

from __future__ import annotations

import re

# German book abbreviations / names  (order matters: longer first)
_BOOK_NAMES = (
    # Names often with numeric prefix or long names
    "Mose|Koenige|Könige|Samuel|Chronik|Korinther|Thessalonicher"
    "|Timotheus|Petrus|Johannes|Roemer|Römer|Galater|Epheser"
    "|Philipper|Kolosser|Hebreaer|Hebräer|Offenbarung"
    # Standard abbreviations (AT)
    "|Gen|Ex|Lev|Num|Dtn|Jos|Ri|Rut|Sam|Kön|Koen|Chr|Esr|Neh|Est"
    "|Ijob|Hiob|Hi|Ps|Spr|Koh|Pred|Hld|Jes|Jer|Klgl|Ez|Hes|Dan"
    "|Hos|Joel|Am|Obd|Jona|Mi|Nah|Hab|Zef|Hag|Sach|Mal"
    # Standard abbreviations (NT)
    "|Mt|Mk|Lk|Joh|Apg|Röm|Roem|Kor|Gal|Eph|Phil|Kol|Thess"
    "|Tim|Tit|Phlm|Hebr|Jak|Petr|Jud|Offb"
)

BIBLE_REF_PATTERN: re.Pattern[str] = re.compile(
    r"(?P<book>"
    r"(?:[12345]\.\s?)?"  # optional numeric prefix  "1. " / "2."
    r"(?:" + _BOOK_NAMES + r")"
    r")"
    r"\s*"
    r"(?P<chapter>\d{1,3})"
    r"(?:\s*[,:]\s*(?P<verse_start>\d{1,3})[abf]{0,2})?"
    r"(?:\s*[-\u2013]\s*(?P<verse_end>\d{1,3})[abf]{0,2})?",
    re.IGNORECASE,
)


def extract_references(
    text: str,
    paragraph_index: int = 0,
) -> list[dict[str, object]]:
    """Return a list of raw-match dicts for every Bible reference in *text*.

    Each dict contains: book, chapter, verse_start, verse_end, raw_text,
    paragraph_index, match_start, match_end.
    """
    results: list[dict[str, object]] = []
    for m in BIBLE_REF_PATTERN.finditer(text):
        results.append(
            {
                "book": m.group("book").strip(),
                "chapter": int(m.group("chapter")),
                "verse_start": (
                    int(m.group("verse_start")) if m.group("verse_start") else None
                ),
                "verse_end": (
                    int(m.group("verse_end")) if m.group("verse_end") else None
                ),
                "raw_text": m.group(0),
                "paragraph_index": paragraph_index,
                "match_start": m.start(),
                "match_end": m.end(),
            }
        )
    return results
