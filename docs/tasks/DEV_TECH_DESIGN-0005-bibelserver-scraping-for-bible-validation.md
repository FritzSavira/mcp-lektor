# DEV_TECH_DESIGN-0005: Bibelserver Scraping for Bible Validation

Detailed technical design for replacing `bible-api.com` with `bibleserver.com`.

## 1. Affected Components

| **Component** | **Change Description** |
|---------------|------------------------|
| `config/config.yaml` | Remove `bible_api_url` and `bible_api_timeout_seconds`. Add `bible_validation_translation: SLT`. |
| `src/mcp_lektor/config/models.py` | Update `ProofreadingConfig` to remove API settings and add validation settings. |
| `src/mcp_lektor/core/bible_validator.py` | Remove `_API_BOOK_MAP` and `_validate_online`. Implement `_validate_via_bibleserver`. |
| `tests/unit/test_bible_validator.py` | Update tests to mock Bibelserver HTML responses instead of Bible API JSON. |

## 2. Technical Details

### 2.1. `bible_validator.py` refactoring
- **Removal:** Delete the `_API_BOOK_MAP` dictionary.
- **New Helper `_validate_via_bibleserver`:**
    - Input: `BibleReference`, `client`, `api_base`, `timeout`, `translation`.
    - URL Construction: Use the `get_bibelserver_url` logic (e.g., `https://www.bibleserver.com/SLT/1-mose1,1`).
    - Response Analysis:
        - Extract the `<title>` tag using a simple regex: `re.search(r"<title>(.*?)</title>", resp.text, re.I | re.S)`.
        - **Normalization for Comparison:**
            - Convert the requested book slug (e.g., `1-mose`) to a comparable form (e.g., `1.Mose`).
            - Check if the title contains the book name, chapter number, and verse (if applicable).
            - Example: `1-mose60` -> Title `1.Mose 50 | ...` -> 60 != 50 -> **Invalid**.
            - Example: `1-mose1,200` -> Title `1.Mose 1,31 | ...` -> 200 != 31 -> **Invalid**.

### 2.2. Configuration Cleanup
- `ProofreadingConfig` will now have:
    - `bible_validation_translation: str = "SLT"` (default).
    - `bible_validation_base_url: str = "https://www.bibleserver.com"`.

### 2.3. Testing Strategy
- **Mocking:** Use `pytest-httpx` to provide HTML strings with specific `<title>` tags to simulate valid/invalid Bibelserver responses.
- **Normalization Test:** Create a specific test case for the "Auto-Correction Detection" (e.g., ensuring `1-mose60` is correctly identified as invalid).

## 3. Risks & Considerations
- **Rate-Limiting:** If too many parallel requests are sent, Bibelserver might block the IP. We should use a moderate timeout and consider sequential processing if needed (though parallel is faster).
- **Title Structure Change:** If Bibelserver changes their title format (e.g., removing the chapter number), the validation will break. This is a risk of scraping.
