# DEV_SPEC-0004: Bible Validation Refinement

Refine the `BibleValidator` by removing the offline fallback mechanism and streamlining the configuration.

## 1. Problem Description
The `BibleValidator` currently contains redundant offline logic for Bible reference verification. This fallback only verifies chapter counts and is outdated compared to the mandatory online requirement of the MCP Lektor project.

## 2. Functional Requirements
1.  **Mandatory Online Validation:** Remove the ability to perform offline Bible reference checks.
2.  **Explicit Error Handling:** If the Bible API (bible-api.com) is unavailable, the system must return a clear error message (e.g., "Bibel-API nicht erreichbar") instead of performing a partial offline check.
3.  **Clean Configuration:** The configuration setting `use_bible_offline_fallback` must be removed from all config files and models.
4.  **Preserve Core Functionality:** Extraction of Bible references and generation of `bibelserver.com` URLs must remain intact.

## 3. User Experience Impacts
- Users will no longer see "OK (nur Kapitel geprüft)" messages.
- If the internet is down or the API is offline, Bible validation results will be explicitly marked as failed for that reference.
- The overall application remains functional; only the specific Bible validation feature is affected by API outages.

## 4. Acceptance Criteria
- [ ] No static chapter-count table exists in `bible_validator.py`.
- [ ] The `_validate_offline` function is removed.
- [ ] The `use_bible_offline_fallback` parameter is removed from `ProofreadingConfig` and `config.yaml`.
- [ ] Unit tests for offline validation are removed or adapted to mock the online API.
- [ ] Bible references continue to be correctly extracted and linked to `bibelserver.com`.
