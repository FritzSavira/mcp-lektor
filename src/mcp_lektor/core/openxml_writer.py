"""Insert Track Changes and comments into .docx files via OpenXML with text-based positioning."""

from __future__ import annotations

import logging
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional

from docx import Document as DocxDocument
from lxml import etree

logger = logging.getLogger(__name__)

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
W = f"{{{WORD_NS}}}"

COMMENTS_URI = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
COMMENTS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"


def apply_track_change(
    paragraph_element: etree._Element,
    original_text: str,
    replacement_text: str,
    author: str,
    timestamp: str,
    revision_id: int,
    char_start: Optional[int] = None,
) -> bool:
    """
    Locates original_text within the paragraph's runs and replaces it with 
    Track Changes (w:del and w:ins).
    
    If char_start is provided, it is used to disambiguate multiple occurrences 
    by picking the match closest to that offset.
    """
    if not original_text:
        return False

    # 1. Collect all text and their corresponding runs
    runs = paragraph_element.findall(f"{W}r")
    full_para_text = ""
    run_map = [] # list of (char_start_in_para, char_end_in_para, run_element)

    for run in runs:
        t_elem = run.find(f"{W}t")
        if t_elem is not None and t_elem.text:
            start = len(full_para_text)
            full_para_text += t_elem.text
            run_map.append((start, len(full_para_text), run))

    # 2. Find the original_text in the full paragraph text
    # We use fuzzy matching to account for apostrophe/quote/space variations
    fuzzy_pattern = _to_fuzzy_regex(original_text)
    
    match = None
    try:
        # Find ALL matches to handle duplicates
        matches = list(re.finditer(fuzzy_pattern, full_para_text))
        if not matches:
             # Fallback: case-insensitive
            matches = list(re.finditer(fuzzy_pattern, full_para_text, re.IGNORECASE))
        
        if not matches:
            logger.warning(f"Could not find text '{original_text}' in paragraph.")
            return False

        if char_start is not None and len(matches) > 1:
            # Disambiguate using char_start
            # Find the match whose start() is closest to char_start
            match = min(matches, key=lambda m: abs(m.start() - char_start))
        else:
            # Default to first match if no hint or only one match
            match = matches[0]

    except Exception as e:
        logger.error(f"Regex error searching for '{original_text}': {e}")
        return False

    match_start, match_end = match.span()
    # Use the ACTUAL text from the document for the delete tag to be accurate
    document_text = full_para_text[match_start:match_end]

    # 3. Identify which runs are affected
    affected_runs = []
    for r_start, r_end, run in run_map:
        if r_end > match_start and r_start < match_end:
            affected_runs.append((r_start, r_end, run))

    if not affected_runs:
        return False

    # To keep it simple and robust, we take the formatting from the FIRST affected run
    first_run_start, first_run_end, first_run = affected_runs[0]
    rpr = first_run.find(f"{W}rPr")
    rpr_copy = deepcopy(rpr) if rpr is not None else None

    # 4. Perform the replacement
    # We remove ALL affected runs and replace them with a single sequence:
    # [Text before match] [del] [ins] [Text after match]
    
    parent = paragraph_element
    insertion_point = list(parent).index(affected_runs[0][2])

    # Text before the match (within the first affected run or preceding)
    text_before = full_para_text[first_run_start:match_start]
    # Text after the match (within the last affected run or following)
    last_run_start, last_run_end, last_run = affected_runs[-1]
    text_after = full_para_text[match_end:last_run_end]

    # Remove all affected runs
    for _, _, run in affected_runs:
        parent.remove(run)

    new_elements = []
    if text_before:
        new_elements.append(_make_run(text_before, rpr_copy))

    # The actual Track Changes
    del_elem = etree.Element(f"{W}del", {f"{W}id": str(revision_id), f"{W}author": author, f"{W}date": timestamp})
    del_elem.append(_make_run(document_text, rpr_copy, is_delete=True))
    new_elements.append(del_elem)

    ins_elem = etree.Element(f"{W}ins", {f"{W}id": str(revision_id + 1), f"{W}author": author, f"{W}date": timestamp})
    ins_elem.append(_make_run(replacement_text, rpr_copy))
    new_elements.append(ins_elem)

    if text_after:
        new_elements.append(_make_run(text_after, rpr_copy))

    # Insert new elements
    for i, elem in enumerate(new_elements):
        parent.insert(insertion_point + i, elem)

    return True


def _to_fuzzy_regex(text: str) -> str:
    """Escapes text but allows common variations like apostrophes, quotes or spaces."""
    # We want to replace quotes, apostrophes and spaces with character classes.
    # To do this safely, we first escape everything, then replace the ESCAPED versions.
    # Note: re.escape does NOT escape ' or " in modern Python, but it DOES escape spaces.
    
    res = re.escape(text)
    
    # 1. Apostrophes: straight ('), smart (’, ‘)
    # Since re.escape doesn't escape ', we just replace it.
    res = res.replace("'", "['’‘]")
    
    # 2. Quotes: straight ("), German low („), smart high (“ ”)
    # Since re.escape doesn't escape ", we just replace it.
    res = res.replace('"', '[\\"„“”]')
    
    # 3. Spaces: re.escape turns " " into "\ "
    # We replace the escaped space "\ " with a character class for all types of spaces.
    res = res.replace(r"\ ", r"[\s\xa0]+")
    
    return res


def apply_corrections_to_document(
    doc: DocxDocument,
    corrections: list[dict],
    author: str = "MCP-Lektor-Auto",
    decisions: Optional[dict[int, str]] = None,
) -> DocxDocument:
    """Applies corrections using text-matching instead of indices."""
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    revision_id = 3000
    comment_id = 1

    # Sort by paragraph index and then original_text length (longer first) to avoid partial matches
    sorted_corrections = sorted(
        enumerate(corrections),
        key=lambda ic: (
            ic[1].get("paragraph_index", 0),
            len(ic[1].get("original_text", "")),
        ),
        reverse=True,
    )

    for original_idx, corr in sorted_corrections:
        if decisions is not None and decisions.get(original_idx) == "reject":
            continue

        p_idx = corr.get("paragraph_index", 0)
        if p_idx >= len(doc.paragraphs):
            continue
        
        para_obj = doc.paragraphs[p_idx]
        para_elem = para_obj._element

        original_text = corr.get("original_text", "")
        replacement_text = corr.get("suggested_text") or corr.get("replacement_text", "")

        # 1. Apply Track Change via Text Matching
        success = apply_track_change(
            paragraph_element=para_elem,
            original_text=original_text,
            replacement_text=replacement_text,
            author=author,
            timestamp=timestamp,
            revision_id=revision_id,
            char_start=corr.get("char_offset_start") or corr.get("char_start"),
        )

        if success:
            # 2. Apply Comment
            add_comment(
                document=doc,
                paragraph_element=para_elem,
                comment_text=f"[{corr.get('category', 'Lektorat')}] {corr.get('explanation', '')}",
                author=author,
                timestamp=timestamp,
                comment_id=comment_id
            )
            revision_id += 2
            comment_id += 1

    _save_comments_part(doc)
    return doc


def add_comment(
    document: DocxDocument,
    paragraph_element: etree._Element,
    comment_text: str,
    author: str,
    timestamp: str,
    comment_id: int,
) -> None:
    """Adds a comment to the END of a paragraph (simpler and safer for Auto-mode)."""
    comments_element = _get_or_create_comments_part(document)
    parent = paragraph_element

    range_start = etree.Element(f"{W}commentRangeStart", {f"{W}id": str(comment_id)})
    range_end = etree.Element(f"{W}commentRangeEnd", {f"{W}id": str(comment_id)})
    
    ref_run = etree.Element(f"{W}r")
    rpr = etree.SubElement(ref_run, f"{W}rPr")
    etree.SubElement(rpr, f"{W}rStyle", {f"{W}val": "Kommentarzeichen"})
    etree.SubElement(ref_run, f"{W}commentReference", {f"{W}id": str(comment_id)})

    # Append to paragraph end
    parent.append(range_start)
    parent.append(range_end)
    parent.append(ref_run)

    _add_comment_to_part(comments_element, comment_id, author, timestamp, comment_text)


def _make_run(text: str, rpr: Optional[etree._Element] = None, is_delete: bool = False) -> etree._Element:
    run = etree.Element(f"{W}r")
    if rpr is not None:
        run.append(deepcopy(rpr))
    
    tag = f"{W}delText" if is_delete else f"{W}t"
    t = etree.SubElement(run, tag)
    t.set(f"{{{XML_NS}}}space", "preserve")
    t.text = text
    return run


def _get_or_create_comments_part(doc: DocxDocument) -> etree._Element:
    if hasattr(doc, "_comments_element"):
        return doc._comments_element
    for rel in doc.part.rels.values():
        if "comments" in rel.reltype:
            doc._comments_element = etree.fromstring(rel.target_part.blob)
            return doc._comments_element
    root = etree.Element(f"{W}comments", nsmap={"w": WORD_NS})
    doc._comments_element = root
    return root


def _add_comment_to_part(comments_element: etree._Element, comment_id: int, author: str, timestamp: str, text: str) -> None:
    comment = etree.SubElement(comments_element, f"{W}comment", {
        f"{W}id": str(comment_id),
        f"{W}author": author,
        f"{W}date": timestamp,
        f"{W}initials": author[:3].upper()
    })
    p = etree.SubElement(comment, f"{W}p")
    r = etree.SubElement(p, f"{W}r")
    t = etree.SubElement(r, f"{W}t")
    t.text = text


def _save_comments_part(doc: DocxDocument) -> None:
    if not hasattr(doc, "_comments_element"):
        return
    from docx.opc.part import Part
    from docx.opc.packuri import PackURI
    blob = etree.tostring(doc._comments_element, encoding="utf-8", xml_declaration=True, standalone=True)
    for rel in doc.part.rels.values():
        if "comments" in rel.reltype:
            rel.target_part._blob = blob
            return
    part = Part(PackURI("/word/comments.xml"), COMMENTS_CONTENT_TYPE, blob, doc.part.package)
    doc.part.relate_to(part, COMMENTS_URI)
