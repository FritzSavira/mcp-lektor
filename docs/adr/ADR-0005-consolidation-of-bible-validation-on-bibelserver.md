# ADR-0005: Consolidation of Bible Validation on Bibelserver.com

## Status
Proposed

## Context
The project currently uses `bible-api.com` for active online validation and `bibelserver.com` for generating comparison links. 
Maintaining two different Bible services:
1.  Increases code complexity (two different book name mappings).
2.  Creates inconsistencies (one service might validate a reference that the other doesn't support).
3.  `bible-api.com` is English-centric and requires an extra mapping step.

`bibelserver.com` is the primary reference for the target audience (German Protestant/Einheitsübersetzung). However, it does not provide a public JSON API for validation.

## Decision
We will replace `bible-api.com` with active validation against `bibelserver.com`.

1.  **Technique:** We will use Web Scraping (analyzing HTTP responses and HTML titles) to verify if a reference exists.
2.  **Validation Logic:** Since Bibelserver auto-corrects invalid references to the nearest valid one (e.g., "Gen 60" -> "Gen 50"), we will validate by comparing the requested reference with the resulting page title (`<title>` tag).
3.  **Unified Mapping:** We will use the existing `_BIBELSERVER_BOOK_MAP` for both validation and link generation, removing the `_API_BOOK_MAP`.
4.  **Configuration:** Remove `bible_api_url` and replace it with a configurable `bible_validation_base_url` (defaulting to `https://www.bibleserver.com`).

## Consequences
- **Positive:** Single source of truth for validation and linking.
- **Positive:** Native support for German book names and abbreviations without intermediate translation to English IDs.
- **Positive:** Reduced code complexity by removing redundant mapping and API-specific error handling.
- **Negative:** Increased dependency on the HTML structure of Bibelserver (specifically the `<title>` tag).
- **Negative:** Risk of rate-limiting by Bibelserver (mitigated by using a single translation for validation).
- **Negative:** Slightly slower validation as full HTML pages are loaded instead of small JSON fragments.
