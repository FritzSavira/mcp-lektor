# DEV_SPEC-0005: Bibelserver-based Bible Validation

Implement active Bible reference validation by scraping `bibleserver.com`.

## 1. Problem Description
The `BibleValidator` currently uses two services for different purposes. `bible-api.com` is used for validation, but it is English-centric. `bibelserver.com` is used for links. We want to unify this and use `bibelserver.com` for both.

## 2. Functional Requirements
1.  **Uniform Mapping:** The existing `_BIBELSERVER_BOOK_MAP` must be used for all operations (validation and linking).
2.  **Web Scraping Validation:**
    *   Construct the URL for a reference using a default translation (e.g., `SLT` or `LUT`).
    *   Perform an HTTP GET request to this URL.
    *   Extract the content of the `<title>` tag from the response.
3.  **Validation Logic (Title Comparison):**
    *   A reference is considered **valid** if the `<title>` tag contains the requested book name, chapter, and (if specified) verse.
    *   Example: Requested `1-mose60` -> Redirected/Auto-corrected -> Title shows `1.Mose 50` -> **Invalid** (60 != 50).
    *   Example: Requested `Xyz1` -> Redirected -> Title shows `1.Mose 1` -> **Invalid** (Xyz != 1.Mose).
4.  **Error Handling:**
    *   Handle network timeouts and HTTP errors (403 Forbidden, 500 Internal Server Error) with appropriate error messages (e.g., "Bibelserver nicht erreichbar").
    *   Follow redirects automatically (301, 302).
5.  **Clean Configuration:** Remove all references to `bible-api.com` from configuration files and models.

## 3. User Experience Impacts
- More accurate validation for German book names (e.g., "Offenbarung", "Römer").
- Direct consistency between validation results and the provided links.
- No more "Unknown book" errors for books that Bibelserver supports but Bible API doesn't.

## 4. Acceptance Criteria
- [ ] No `_API_BOOK_MAP` dictionary exists in `bible_validator.py`.
- [ ] No HTTP requests are made to `bible-api.com`.
- [ ] `BibleValidator.validate` performs active validation by checking the page title on `bibleserver.com`.
- [ ] `SLT` (Schlachter 2000) or a configurable translation is used as the default validation translation.
- [ ] Unit tests for `BibleValidator.validate` are updated to mock Bibelserver HTML responses.
