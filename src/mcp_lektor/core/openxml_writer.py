"""Insert Track Changes and comments into .docx files via OpenXML."""

from __future__ import annotations

import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional

from docx import Document as DocxDocument
from lxml import etree

logger = logging.getLogger(__name__)

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "http://www.w3.org/XML/1998/namespace"
COMMENTS_URI = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
)
COMMENTS_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
)


# ------------------------------------------------------------------ #
# Public API                                                          #
# ------------------------------------------------------------------ #


def apply_track_change(
    paragraph_element: etree._Element,
    run_index: int,
    char_start: int,
    char_end: int,
    original_text: str,
    replacement_text: str,
    author: str,
    timestamp: str,
    revision_id: int,
) -> None:
    """Insert <w:del> and <w:ins> elements around a text replacement.

    Args:
        paragraph_element: The lxml element of the <w:p> paragraph.
        run_index: Index of the target <w:r> run within the paragraph.
        char_start: Character offset where the original text begins.
        char_end: Character offset where the original text ends.
        original_text: The text being replaced (for the deletion).
        replacement_text: The new text (for the insertion).
        author: Revision author name.
        timestamp: ISO-8601 timestamp for the revision.
        revision_id: Unique numeric revision identifier.
    """
    runs = paragraph_element.findall(f".//{{{WORD_NS}}}r")
    if run_index >= len(runs):
        logger.warning(
            "run_index %d out of range (paragraph has %d runs)",
            run_index,
            len(runs),
        )
        return

    target_run = runs[run_index]
    text_elem = target_run.find(f"{{{WORD_NS}}}t")
    if text_elem is None or text_elem.text is None:
        logger.warning("Target run has no text element")
        return

    full_text = text_elem.text
    rpr = target_run.find(f"{{{WORD_NS}}}rPr")
    rpr_copy = deepcopy(rpr) if rpr is not None else None

    parent = target_run.getparent()
    run_position = list(parent).index(target_run)

    before_text = full_text[:char_start]
    after_text = full_text[char_end:]

    parent.remove(target_run)
    insert_pos = run_position

    # 1. Insert before-text run
    if before_text:
        before_run = _make_run(before_text, rpr_copy)
        parent.insert(insert_pos, before_run)
        insert_pos += 1

    # 2. Insert <w:del> element
    del_elem = etree.Element(
        f"{{{WORD_NS}}}del",
        {
            f"{{{WORD_NS}}}id": str(revision_id),
            f"{{{WORD_NS}}}author": author,
            f"{{{WORD_NS}}}date": timestamp,
        },
    )
    del_run = _make_run(original_text, rpr_copy, is_delete=True)
    del_elem.append(del_run)
    parent.insert(insert_pos, del_elem)
    insert_pos += 1

    # 3. Insert <w:ins> element
    ins_elem = etree.Element(
        f"{{{WORD_NS}}}ins",
        {
            f"{{{WORD_NS}}}id": str(revision_id + 1),
            f"{{{WORD_NS}}}author": author,
            f"{{{WORD_NS}}}date": timestamp,
        },
    )
    ins_run = _make_run(replacement_text, rpr_copy)
    ins_elem.append(ins_run)
    parent.insert(insert_pos, ins_elem)
    insert_pos += 1

    # 4. Insert after-text run
    if after_text:
        after_run = _make_run(after_text, rpr_copy)
        parent.insert(insert_pos, after_run)


def add_comment(
    document: DocxDocument,
    paragraph_element: etree._Element,
    run_index: int,
    comment_text: str,
    author: str,
    timestamp: str,
    comment_id: int,
) -> None:
    """Insert a Word comment anchored to a specific run.

    Args:
        document: The python-docx Document object.
        paragraph_element: The lxml element of the <w:p> paragraph.
        run_index: Index of the target <w:r> run.
        comment_text: The comment body text.
        author: Comment author name.
        timestamp: ISO-8601 timestamp.
        comment_id: Unique numeric comment identifier.
    """
    comments_part = _get_or_create_comments_part(document)

    runs = paragraph_element.findall(f".//{{{WORD_NS}}}r")
    if run_index >= len(runs):
        logger.warning(
            "run_index %d out of range for comment (paragraph has %d runs)",
            run_index,
            len(runs),
        )
        return

    target_run = runs[run_index]
    parent = target_run.getparent()
    run_pos = list(parent).index(target_run)

    # commentRangeStart before the run
    range_start = etree.Element(f"{{{WORD_NS}}}commentRangeStart")
    range_start.set(f"{{{WORD_NS}}}id", str(comment_id))
    parent.insert(run_pos, range_start)

    # commentRangeEnd after the run
    range_end = etree.Element(f"{{{WORD_NS}}}commentRangeEnd")
    range_end.set(f"{{{WORD_NS}}}id", str(comment_id))
    parent.insert(run_pos + 2, range_end)

    # commentReference run after rangeEnd
    ref_run = etree.Element(f"{{{WORD_NS}}}r")
    ref_rpr = etree.SubElement(ref_run, f"{{{WORD_NS}}}rPr")
    ref_style = etree.SubElement(ref_rpr, f"{{{WORD_NS}}}rStyle")
    ref_style.set(f"{{{WORD_NS}}}val", "CommentReference")
    comment_ref = etree.SubElement(ref_run, f"{{{WORD_NS}}}commentReference")
    comment_ref.set(f"{{{WORD_NS}}}id", str(comment_id))
    parent.insert(run_pos + 3, ref_run)

    # Add the actual comment content to the comments part
    _add_comment_to_part(comments_part, comment_id, author, timestamp, comment_text)


def apply_corrections_to_document(
    doc: DocxDocument,
    corrections: list[dict],
    author: str = "MCP-Lektor",
    decisions: Optional[dict[int, str]] = None,
) -> DocxDocument:
    """Apply a list of corrections as Track Changes with comments.

    Args:
        doc: The python-docx Document to modify.
        corrections: List of correction dicts with keys:
            paragraph_index, run_index, char_start, char_end,
            original_text, replacement_text, category, explanation.
        author: Revision author name.
        decisions: Optional mapping of correction_index → "accept"/"reject"/"edit".
            If None, all corrections are applied.

    Returns:
        The modified Document (same object, mutated in place).
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    revision_id = 1000
    comment_id = 0

    # Sort corrections in reverse order (by paragraph_index desc, then
    # char_start desc) so that earlier indices remain valid after mutations.
    sorted_corrections = sorted(
        enumerate(corrections),
        key=lambda ic: (
            ic[1].get("paragraph_index", 0),
            ic[1].get("char_start", 0),
        ),
        reverse=True,
    )

    paragraphs = doc.element.body.findall(f".//{{{WORD_NS}}}p")

    for original_idx, correction in sorted_corrections:
        # Check decision filter
        if decisions is not None:
            decision = decisions.get(original_idx, "reject")
            if decision == "reject":
                continue

        para_idx = correction.get("paragraph_index", 0)
        if para_idx >= len(paragraphs):
            logger.warning(
                "paragraph_index %d out of range (document has %d paragraphs)",
                para_idx,
                len(paragraphs),
            )
            continue

        para_elem = paragraphs[para_idx]

        # Apply track change
        apply_track_change(
            paragraph_element=para_elem,
            run_index=correction.get("run_index", 0),
            char_start=correction.get("char_start", 0),
            char_end=correction.get("char_end", 0),
            original_text=correction.get("original_text", ""),
            replacement_text=correction.get("replacement_text", ""),
            author=author,
            timestamp=timestamp,
            revision_id=revision_id,
        )
        revision_id += 2  # Each change uses 2 IDs (del + ins)

        # Add comment
        category = correction.get("category", "Korrektur")
        explanation = correction.get("explanation", "")
        comment_body = f"[{category}] {explanation}"

        # Re-fetch runs after mutation for comment placement
        add_comment(
            document=doc,
            paragraph_element=para_elem,
            run_index=correction.get("run_index", 0),
            comment_text=comment_body,
            author=author,
            timestamp=timestamp,
            comment_id=comment_id,
        )
        comment_id += 1

    logger.info("Applied %d corrections to document", comment_id)
    return doc


# ------------------------------------------------------------------ #
# Internal helpers                                                    #
# ------------------------------------------------------------------ #


def _make_run(
    text: str,
    rpr: Optional[etree._Element] = None,
    is_delete: bool = False,
) -> etree._Element:
    """Create a <w:r> element with text and optional formatting."""
    run = etree.Element(f"{{{WORD_NS}}}r")
    if rpr is not None:
        run.append(deepcopy(rpr))
    if is_delete:
        dt = etree.SubElement(run, f"{{{WORD_NS}}}delText")
        dt.set(f"{{{XML_SPACE}}}space", "preserve")
        dt.text = text
    else:
        t = etree.SubElement(run, f"{{{WORD_NS}}}t")
        t.set(f"{{{XML_SPACE}}}space", "preserve")
        t.text = text
    return run


def _get_or_create_comments_part(doc: DocxDocument) -> etree._Element:
    """Get or create the comments.xml part in the document."""
    # Try to find existing comments part
    for rel in doc.part.rels.values():
        if "comments" in rel.reltype:
            return etree.fromstring(rel.target_part.blob)

    # Create new comments.xml
    comments_xml = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:comments xmlns:w="{WORD_NS}"'
        f' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        f"/>"
    )
    comments_element = etree.fromstring(comments_xml.encode("utf-8"))

    # Store as attribute on the document for later retrieval
    doc._comments_element = comments_element
    return comments_element


def _add_comment_to_part(
    comments_element: etree._Element,
    comment_id: int,
    author: str,
    timestamp: str,
    text: str,
) -> None:
    """Add a comment entry to the comments XML element."""
    comment = etree.SubElement(
        comments_element,
        f"{{{WORD_NS}}}comment",
        {
            f"{{{WORD_NS}}}id": str(comment_id),
            f"{{{WORD_NS}}}author": author,
            f"{{{WORD_NS}}}date": timestamp,
            f"{{{WORD_NS}}}initials": author[:2].upper(),
        },
    )
    p = etree.SubElement(comment, f"{{{WORD_NS}}}p")
    r = etree.SubElement(p, f"{{{WORD_NS}}}r")
    t = etree.SubElement(r, f"{{{WORD_NS}}}t")
    t.text = text


def _save_comments_part(doc: DocxDocument) -> None:
    """Persist the comments element back into the .docx package."""
    if not hasattr(doc, "_comments_element"):
        return

    comments_element = doc._comments_element
    comments_blob = etree.tostring(
        comments_element, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    # Check if relationship already exists
    for rel in doc.part.rels.values():
        if "comments" in rel.reltype:
            rel.target_part._blob = comments_blob
            return

    # Create new part
    from docx.opc.packuri import PackURI
    from docx.opc.part import Part as OpcPart

    comments_part = OpcPart(
        PackURI("/word/comments.xml"),
        COMMENTS_CONTENT_TYPE,
        comments_blob,
        doc.part.package,
    )
    doc.part.relate_to(comments_part, COMMENTS_URI)
