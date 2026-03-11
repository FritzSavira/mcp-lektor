# DEV_TECH_DESIGN-0004: Bible Validation Refinement

Detailed technical design for removing the Bible offline fallback.

## 1. Affected Components

| **Component** | **Change Description** |
|---------------|------------------------|
| `config/config.yaml` | Remove `use_bible_offline_fallback: true`. |
| `src/mcp_lektor/config/models.py` | Remove `use_bible_offline_fallback` from `ProofreadingConfig`. |
| `src/mcp_lektor/core/bible_validator.py` | Remove `_FALLBACK_CHAPTER_COUNTS` and `_validate_offline`. Refactor `_validate_online` and `BibleValidator.validate`. |
| `tests/unit/test_bible_validator.py` | Remove `TestOfflineValidation` and `TestBibleValidatorOffline`. Update other tests to avoid offline-only checks. |

## 2. Technical Details

### 2.1. `bible_validator.py` refactoring
- **Constant Removal:** Delete the large `_FALLBACK_CHAPTER_COUNTS` dictionary (~140 lines).
- **Function Removal:** Delete the `_validate_offline` helper function.
- **`_validate_online` simplification:**
    - If `_API_BOOK_MAP.get(book)` returns `None`, the reference is invalid (unknown book).
    - In the `except (httpx.HTTPError, httpx.TimeoutException)` block: Always return a failure result with `is_valid=False` and a descriptive error message (e.g., "Bibel-API nicht erreichbar").
- **`BibleValidator.validate` simplification:**
    - The condition `if not self._use_online` will still be respected, but it will now return a failure result for all references (since no offline validation is available anymore). Alternatively, `use_online=False` could disable the check entirely (returning an empty list or skipping).
    - The `use_fallback` parameter in the `_validate_online` call will be removed.

### 2.2. Configuration Cleanup
- Ensure `use_bible_offline_fallback` is removed from `ProofreadingConfig` (Pydantic model) and the YAML template.

### 2.3. Testing Strategy
- **Unit Tests:** Remove the class `TestOfflineValidation`.
- **Mocking:** For integration tests or remaining unit tests of `BibleValidator.validate`, use `pytest-httpx` or a similar mocking library to simulate API responses instead of relying on the offline fallback.

## 3. Risks & Considerations
- **Mocking complexity:** Some tests currently rely on the "instant" offline check. These must be replaced with mocked async calls, which might increase test setup complexity slightly.
- **Breaking API changes:** bible-api.com is a third-party service. By making it mandatory, the tool becomes strictly dependent on its uptime and API stability.
