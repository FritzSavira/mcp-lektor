# DEV_TASKS-0006: Bible Validation Integration

Implement the integration of Bible reference validation into the main proofreading workflow.

## Phase 1: Model & Extraction Refinement
- [ ] **Update Models:**
    - [ ] Add `char_offset_start: int = 0` and `char_offset_end: int = 0` to `BibleReference` in `src/mcp_lektor/core/models.py`.
- [ ] **Update Extraction Logic:**
    - [ ] Update `src/mcp_lektor/utils/bible_patterns.py` to yield the start and end offsets of the match.
    - [ ] Update `src/mcp_lektor/core/bible_validator.py`'s `extract_refs` to populate these offsets.

## Phase 2: Engine Integration
- [ ] **Extend `ProofreadingEngine`:**
    - [ ] In `src/mcp_lektor/core/proofreading_engine.py`, import `BibleValidator`.
    - [ ] Update `proofread` method to include the Bible check if requested.
    - [ ] Implement a helper `_convert_bible_results_to_corrections` to map results to `ProposedCorrection`.
    - [ ] Implement a helper `_find_run_index_for_offset` to accurately place the correction.

## Phase 3: Verification & Testing
- [ ] **Unit Tests:**
    - [ ] Update `tests/unit/test_bible_validator.py` to check for offsets.
    - [ ] Add new tests in `tests/unit/test_proofreading_engine.py` to verify Bible integration.
- [ ] **Integration Test:**
    - [ ] Run an end-to-end check using a test document with valid and invalid Bible references.
- [ ] **Check project-wide standards:**
    - [ ] Run `black .`.
    - [ ] Run `ruff check .`.
    - [ ] Run `pytest`.

## Phase 4: Finalization
- [ ] Update `CHANGELOG.md` referencing ADR-0006.
- [ ] Update `docs/tasks/DEV_TASKS-0006-bible-validation-integration.md` to mark all tasks as completed.
