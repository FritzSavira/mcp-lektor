"""Orchestrate rule-based and LLM-based proofreading."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from mcp_lektor.config.settings import (
    load_config,
    load_confused_words,
    load_typography_rules,
)
from mcp_lektor.core.confused_words_checker import scan_confused_words
from mcp_lektor.core.models import (
    ConfidenceLevel,
    CorrectionCategory,
    DocumentStructure,
    ProofreadingConfig,
    ProofreadingResult,
    ProposedCorrection,
)
from mcp_lektor.core.quotation_checker import check_quotation_marks
from mcp_lektor.core.typography_checker import check_typography

logger = logging.getLogger(__name__)

# Categories handled by the LLM (not rule-based)
_LLM_CATEGORIES = {
    CorrectionCategory.SPELLING,
    CorrectionCategory.GRAMMAR,
    CorrectionCategory.PUNCTUATION,
    CorrectionCategory.ADDRESS_FORM,
}

_BATCH_TOKEN_LIMIT = 2500


class ProofreadingEngine:
    """Main proofreading orchestrator."""

    def __init__(self, config: ProofreadingConfig | None = None) -> None:
        self.config = config or load_config()
        self.typography_rules = load_typography_rules()
        self.confused_words = load_confused_words()

    async def proofread(
        self,
        structure: DocumentStructure,
        checks: list[CorrectionCategory] | None = None,
    ) -> ProofreadingResult:
        """Run the full proofreading pipeline.

        1. Rule-based pre-scan (typography, confused words, quotation marks)
        2. LLM-based analysis (spelling, grammar, punctuation, address form)
        3. Deduplicate overlapping corrections
        4. Assign sequential IDs
        """
        start = time.time()
        if checks is None:
            checks = list(CorrectionCategory)

        all_corrections: list[ProposedCorrection] = []

        # --- Step 1: Rule-based checks ---
        if CorrectionCategory.TYPOGRAPHY in checks:
            all_corrections.extend(check_typography(structure, self.typography_rules))
        if CorrectionCategory.CONFUSED_WORD in checks:
            all_corrections.extend(scan_confused_words(structure, self.confused_words))
        if CorrectionCategory.QUOTATION_MARKS in checks:
            all_corrections.extend(check_quotation_marks(structure))

        # --- Step 2: LLM-based checks ---
        llm_checks = [c for c in checks if c in _LLM_CATEGORIES]
        if llm_checks:
            llm_corrections = await self._proofread_with_llm(structure, llm_checks)
            all_corrections.extend(llm_corrections)

        # --- Step 3: Deduplicate ---
        all_corrections = _deduplicate(all_corrections)

        # --- Step 4: Assign IDs ---
        for i, corr in enumerate(all_corrections, 1):
            corr.id = f"C-{i:03d}"

        elapsed = time.time() - start
        return ProofreadingResult(
            document_filename=structure.filename,
            total_corrections=len(all_corrections),
            corrections=all_corrections,
            processing_time_seconds=round(elapsed, 2),
        )

    async def _proofread_with_llm(
        self,
        structure: DocumentStructure,
        checks: list[CorrectionCategory],
    ) -> list[ProposedCorrection]:
        """Batch paragraphs and send to the LLM."""

        paragraphs = [
            p
            for p in structure.paragraphs
            if not p.is_placeholder_paragraph and p.proofreadable_text.strip()
        ]
        if not paragraphs:
            return []

        all_corrections: list[ProposedCorrection] = []
        batch: list[dict[str, Any]] = []
        batch_tokens = 0

        for para in paragraphs:
            para_dict = {
                "index": para.index,
                "text": para.proofreadable_text,
            }
            est_tokens = len(para.proofreadable_text) // 3
            if batch_tokens + est_tokens > _BATCH_TOKEN_LIMIT and batch:
                corrections = await self._process_batch(batch, checks)
                all_corrections.extend(corrections)
                batch = []
                batch_tokens = 0

            batch.append(para_dict)
            batch_tokens += est_tokens

        if batch:
            corrections = await self._process_batch(batch, checks)
            all_corrections.extend(corrections)

        return all_corrections

    async def _process_batch(
        self,
        batch: list[dict[str, Any]],
        checks: list[CorrectionCategory],
    ) -> list[ProposedCorrection]:
        """Send one batch to the LLM and parse results."""
        from mcp_lektor.core.llm_client import call_llm_for_proofreading

        check_names = [c.value for c in checks]
        raw = await call_llm_for_proofreading(
            json.dumps(batch, ensure_ascii=False),
            self.config,
            check_names,
        )

        corrections: list[ProposedCorrection] = []
        for item in raw:
            try:
                cat_str = item.get("category", "")
                category = _parse_category(cat_str)
                confidence = _parse_confidence(item.get("confidence", "medium"))

                corrections.append(
                    ProposedCorrection(
                        id="",
                        paragraph_index=item["paragraph_index"],
                        run_index=item.get("run_index", 0),
                        char_offset_start=item.get("char_offset_start", 0),
                        char_offset_end=item.get("char_offset_end", 0),
                        original_text=item.get("original_text", ""),
                        suggested_text=item.get("suggested_text", ""),
                        category=category,
                        confidence=confidence,
                        explanation=item.get("explanation", ""),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping invalid LLM correction: %s", exc)
        return corrections


def _deduplicate(
    corrections: list[ProposedCorrection],
) -> list[ProposedCorrection]:
    """Remove duplicate corrections at the same location.

    When two corrections target the exact same span, keep the one
    with higher confidence.
    """
    seen: dict[tuple[int, int, int, int], ProposedCorrection] = {}
    confidence_order = {
        ConfidenceLevel.HIGH: 3,
        ConfidenceLevel.MEDIUM: 2,
        ConfidenceLevel.LOW: 1,
    }

    for corr in corrections:
        key = (
            corr.paragraph_index,
            corr.run_index,
            corr.char_offset_start,
            corr.char_offset_end,
        )
        existing = seen.get(key)
        if existing is None:
            seen[key] = corr
        elif confidence_order.get(corr.confidence, 0) > confidence_order.get(
            existing.confidence, 0
        ):
            seen[key] = corr

    return list(seen.values())


def _parse_category(value: str) -> CorrectionCategory:
    """Best-effort mapping of LLM category strings to enum."""
    for member in CorrectionCategory:
        if member.value.lower() == value.lower():
            return member
    lower = value.lower()
    if "rechtschreib" in lower or "spelling" in lower:
        return CorrectionCategory.SPELLING
    if "grammatik" in lower or "grammar" in lower:
        return CorrectionCategory.GRAMMAR
    if "zeichensetzung" in lower or "punctuat" in lower:
        return CorrectionCategory.PUNCTUATION
    if "anrede" in lower or "address" in lower:
        return CorrectionCategory.ADDRESS_FORM
    return CorrectionCategory.SPELLING


def _parse_confidence(value: str) -> ConfidenceLevel:
    """Map a confidence string to the enum."""
    try:
        return ConfidenceLevel(value.lower())
    except ValueError:
        return ConfidenceLevel.MEDIUM
