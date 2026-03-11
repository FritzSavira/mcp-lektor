# DEV_TASKS-0004: Bible Validation Refinement

Implement the removal of the Bible offline fallback mechanism.

## Phase 1: Preparation & Analysis
- [x] Verify that no other part of the system (e.g., UI, session manager) expects the `use_bible_offline_fallback` parameter.
- [x] Check existing tests for dependencies on the offline check.

## Phase 2: Refactoring
- [x] **Clean Configuration:**
    - [x] Update `src/mcp_lektor/config/models.py` by removing the parameter from `ProofreadingConfig`.
    - [x] Update `config/config.yaml` to remove the setting.
- [x] **Streamline `bible_validator.py`:**
    - [x] Remove `_FALLBACK_CHAPTER_COUNTS` dictionary.
    - [x] Remove `_validate_offline` helper function.
    - [x] Refactor `_validate_online` to return an explicit error on network failure.
    - [x] Update `BibleValidator.validate` and its `__init__` if necessary.

## Phase 3: Verification
- [x] **Cleanup Unit Tests:**
    - [x] Remove `TestOfflineValidation` and `TestBibleValidatorOffline` from `tests/unit/test_bible_validator.py`.
    - [x] Ensure remaining tests still pass (extraction, URL generation).
- [x] **Add Online Mock Tests:**
    - [x] Add a new test case that mocks the `bible-api.com` response to verify the async validation logic (Implemented as error handler test in unit tests).
- [x] **Check project-wide standards:**
    - [x] Run `black .`.
    - [x] Run `ruff check .`.
    - [x] Run `pytest tests/unit/test_bible_validator.py`.

## Phase 4: Finalization
- [x] Update `CHANGELOG.md` referencing ADR-0004.
- [x] Update `docs/tasks/DEV_TASKS-0004-bible-validation-refinement.md` to mark all tasks as completed.
