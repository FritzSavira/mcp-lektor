# DEV_TASKS-0006: Bible Validation Integration

Implement the integration of Bible reference validation into the main proofreading workflow.

## Phase 1: Model & Extraction Refinement
- [x] **Update Models:**
    - [x] Add `char_offset_start: int = 0` and `char_offset_end: int = 0` to `BibleReference` in `src/mcp_lektor/core/models.py`.
- [x] **Update Extraction Logic:**
    - [x] Update `src/mcp_lektor/utils/bible_patterns.py` to yield the start and end offsets of the match.
    - [x] Update `src/mcp_lektor/core/bible_validator.py`'s `extract_refs` to populate these offsets.

## Phase 2: Engine Integration
- [x] **Extend `ProofreadingEngine`:**
    - [x] In `src/mcp_lektor/core/proofreading_engine.py`, import `BibleValidator`.
    - [x] Update `proofread` method to include the Bible check if requested.
    - [x] Implement a helper `_convert_bible_results_to_corrections` to map results to `ProposedCorrection`.
    - [x] Implement a helper `_find_run_index_for_offset` to accurately place the correction.

## Phase 3: Verification & Testing
- [x] **Unit Tests:**
    - [x] Update `tests/unit/test_bible_validator.py` to check for offsets.
    - [x] Add new tests in `tests/unit/test_proofreading_engine_bible.py` to verify Bible integration.
- [x] **Integration Test:**
    - [x] Run an end-to-end check using a test document with valid and invalid Bible references.
- [x] **Check project-wide standards:**
    - [x] Run `black .`.
    - [x] Run `ruff check .`.
    - [x] Run `pytest`.

## Phase 4: Finalization
- [x] Update `CHANGELOG.md` referencing ADR-0006.
- [x] Update `docs/tasks/DEV_TASKS-0006-bible-validation-integration.md` to mark all tasks as completed.
