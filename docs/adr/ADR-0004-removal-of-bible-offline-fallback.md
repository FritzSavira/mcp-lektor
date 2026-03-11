# ADR-0004: Removal of Bible Offline Fallback

## Status
Proposed

## Context
The `BibleValidator` currently implements an offline fallback mechanism (`_validate_offline`) that checks Bible references against a static table of chapter counts (`_FALLBACK_CHAPTER_COUNTS`) when the online API is unavailable. 

However:
1.  The project premises assume a functioning internet infrastructure for core features (e.g., LLM-based proofreading via Langdock/OpenAI).
2.  The offline fallback is limited: it can only verify chapter numbers, but not verse ranges, leading to "optimistic" but potentially incorrect validation results (e.g., "OK (nur Kapitel geprüft)").
3.  Maintaining the static chapter-count table is manual and error-prone.
4.  The dual logic (online/offline) increases code complexity and complicates testing.

## Decision
We will remove the offline fallback mechanism from the `BibleValidator` and the corresponding configuration settings.

1.  **Requirement Change:** Internet access is now a mandatory requirement for Bible validation.
2.  **Code Cleanup:** Remove `_FALLBACK_CHAPTER_COUNTS`, `_validate_offline`, and the `use_bible_offline_fallback` configuration parameter.
3.  **Error Handling:** If the Bible API is unreachable (e.g., network error, timeout), the validation for that reference will explicitly fail with a clear error message instead of falling back to a partial offline check.
4.  **Configuration Refinement:** The `ProofreadingConfig` will be cleaned up to remove the now-obsolete fallback toggle.

## Consequences
- **Positive:** Significant reduction in code complexity (~150 lines of static data and redundant logic removed).
- **Positive:** Improved validation quality by eliminating partial/optimistic results.
- **Positive:** Better maintainability as no manual updates to the Bible canon table are required.
- **Negative:** Bible validation will no longer work without an active internet connection, even for simple chapter-level checks. This is consistent with the project's overall infrastructure premises.
