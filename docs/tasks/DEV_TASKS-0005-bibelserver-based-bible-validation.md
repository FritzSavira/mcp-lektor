# DEV_TASKS-0005: Bibelserver-based Bible Validation

Implement active validation against `bibleserver.com`.

## Phase 1: Refactoring & Cleanup
- [x] **Clean Configuration:**
    - [x] Update `src/mcp_lektor/config/models.py`: Remove `bible_api_` parameters, add `bible_validation_translation` and `bible_validation_base_url`.
    - [x] Update `config/config.yaml`: Remove `bible_api_` settings and add new ones.
- [x] **Streamline `bible_validator.py`:**
    - [x] Remove `_API_BOOK_MAP` dictionary.
    - [x] Implement `_extract_title(html: str)` helper.
    - [x] Implement `_validate_via_bibleserver(ref: BibleReference, ...)` based on title comparison.
    - [x] Update `BibleValidator.validate` to use the new scraping logic.

## Phase 2: Verification & Testing
- [x] **Cleanup Unit Tests:**
    - [x] Remove tests for `bible-api.com` in `tests/unit/test_bible_validator.py`.
- [x] **Add Scraper Mock Tests:**
    - [x] Add a test case for a valid reference (mocked title matches).
    - [x] Add a test case for an auto-corrected reference (title mismatch -> invalid).
    - [x] Add a test case for an unknown book (redirect to default -> invalid).
    - [x] Add a test case for network failure (HTTP 500 or timeout).
- [x] **Check project-wide standards:**
    - [x] Run `black src/mcp_lektor/core/bible_validator.py`.
    - [x] Run `ruff check src/mcp_lektor/core/bible_validator.py`.
    - [x] Run `pytest tests/unit/test_bible_validator.py`.

## Phase 3: Finalization
- [x] Update `CHANGELOG.md` referencing ADR-0005.
- [x] Update `docs/tasks/DEV_TASKS-0005-bibelserver-based-bible-validation.md` to mark all tasks as completed.
