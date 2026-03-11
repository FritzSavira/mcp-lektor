# ADR-0005: Removal of bible-api.com Integration

## Status
Proposed

## Context
The `BibleValidator` currently uses `bible-api.com` to actively validate the existence of Bible references via HTTP requests. Additionally, it generates comparison links for `bibelserver.com`.

However:
1.  `bible-api.com` is a third-party dependency that can fail (timeouts, downtime).
2.  The API primarily supports English-based book identifiers, requiring a complex mapping (`_API_BOOK_MAP`).
3.  The project's primary value for Bible references lies in **identification** (Regex) and **manual verification** (Deep-Links to established German platforms like Bibelserver).
4.  The removal of the offline fallback (ADR-0004) already established that we prioritize simplicity over partial/unreliable validation.

## Decision
We will remove the `bible-api.com` integration (active online validation) from the `BibleValidator`. 

1.  **Functionality Shift:** The `BibleValidator` will focus exclusively on extracting Bible references and providing Deep-Links to `bibelserver.com` for manual verification by the user.
2.  **Code Cleanup:** Remove `_API_BOOK_MAP`, `_validate_online`, and the `bible_api_url`/`bible_api_timeout_seconds` configuration parameters.
3.  **Validation Logic:** References found via Regex will be considered "identified" and returned with their corresponding comparison links. The `is_valid` flag will be set to `True` optimistically (as it passed the structural Regex check).

## Consequences
- **Positive:** Significant reduction in code complexity and external dependencies.
- **Positive:** Improved performance and reliability (no network I/O needed for the "validation" step).
- **Positive:** Simplified configuration and testing (no more HTTP mocking required).
- **Negative:** Automated verification of whether a verse actually exists (e.g., catching "Genesis 60") is lost. Users must rely on the generated links for verification.
