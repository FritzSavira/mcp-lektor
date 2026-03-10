# DEV_TASKS-0003: Consolidation of Quotation Mark Logic

Implement the architectural decision to consolidate quotation mark checks into the `TypographyChecker` and ensure direct corrections with track changes and comments in the Word export.

## Phase 1: Preparation & Analysis
- [x] Review `config/typography_rules.yaml` for completeness (ensure both opening and closing rules cover typical scenarios).
- [x] Identify all locations in `src/mcp_lektor/core/proofreading_engine.py` where `check_quotation_marks` is called.

## Phase 2: Refactoring
- [x] **Clear `quotation_checker.py`:** Remove the redundant `check_quotation_marks` implementation (keep an empty function or return `[]` to avoid breaking references temporarily).
- [x] **Update `typography_rules.yaml`:**
    - [x] Refine regex for "Anführungszeichen öffnend" to include common scenarios (e.g., after space, at start of paragraph).
    - [x] Refine regex for "Anführungszeichen schließend" to include common scenarios (e.g., after word, before punctuation).
- [x] **Update `ProofreadingEngine`:**
    - [x] Remove call to `check_quotation_marks` or handle its empty result.
    - [x] Ensure `CorrectionCategory.QUOTATION_MARKS` is correctly mapped for typography rules.

## Phase 3: Verification
- [x] **Unit Tests:** Add or update tests in `tests/unit/test_proofreading_engine.py` to cover opening and closing quotation marks.
- [x] **Integration Test:** Run a test with a sample document containing straight quotes to verify:
    - [x] Correct typographic marks (opening/closing) are suggested.
    - [x] The Word export (`openxml_writer.py`) contains Track Changes with the correct replacement.
    - [x] The Word export contains explanatory comments for the quotation mark changes.

## Phase 4: Finalization
- [x] Update `CHANGELOG.md` referencing ADR-0003.
- [x] Final code cleanup and `ruff` / `black` check.
