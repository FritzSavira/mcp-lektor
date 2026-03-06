# DEV_OPEN_QUESTIONS-0001: Critical Implementation Challenges & Open Questions

**Version:** 1.0
**Date:** 2026-03-06
**Status:** Open
**Related Documents:**
- [ADR-0001](../adr/ADR-0001-mcp-based-interactive-proofreading-server.md)
- [DEV_SPEC-0001](DEV_SPEC-0001-mcp-based-interactive-proofreading-server.md)
- [DEV_TECH_DESIGN-0001](DEV_TECH_DESIGN-0001-mcp-based-interactive-proofreading-server.md)
- [DEV_TASKS-0001](DEV_TASKS-0001-mcp-based-interactive-proofreading-server.md)

---

## 1. Architecture & Scalability

### 1.1. Shared State vs. Multi-Worker
- **Problem:** The current design uses an in-memory `SESSION_STORE` (Python dict). If the MCP server is deployed with multiple Uvicorn workers (as recommended for performance), a request for `write_corrected_docx` might land on a different worker than the initial `extract_document` call, resulting in a "Session Not Found" error.
- **Proposed Solution:** Implement a shared session store (e.g., Redis) or a filesystem-based store with encrypted temporary files. Alternatively, restrict the initial deployment to a single worker.

### 1.2. Secure Session Cleanup
- **Problem:** If the server crashes or is forcibly restarted, the background cleanup task (`cleanup_expired_sessions`) will not run, leaving potentially sensitive `.docx` files in the temporary directory.
- **Proposed Solution:** Use a `tmpfs` mount in Docker for the temporary directory to ensure data is lost on container restart. Implement a startup "wipe" of the temporary directory.

---

## 2. OpenXML Manipulation Robustness

### 2.1. Run Fragmentation (Normalization)
- **Problem:** Word often splits a single word into multiple `<w:r>` elements (Runs) due to previous edits, spellcheck metadata, or formatting shifts. The current `apply_track_change` logic assumes corrections happen within a single Run.
- **Proposed Solution:** Implement a "Run Normalizer" that merges adjacent Runs with identical formatting before extraction and proofreading.

### 2.2. Automated XML Validation
- **Problem:** Manual verification in Word/LibreOffice is error-prone and cannot be part of a CI pipeline. Corrupting the XML structure renders the document unusable.
- **Proposed Solution:** Use `lxml` to validate the generated `.docx` against the official Office Open XML (OOXML) schemas during integration tests.

---

## 3. Proofreading & Logic

### 3.1. Definition of "Red Text" (FR-10)
- **Problem:** "Red" is ambiguous in Word. It can be a specific RGB value (e.g., `#FF0000`), a theme color (`accent1`), or a range of shades.
- **Required Decision:** Define the exact color detection logic (e.g., "any color where R > 200 and G < 100 and B < 100").

### 3.2. Bible API Source & Localization
- **Problem:** `bible-api.com` is primary English. German publications require specific translations (Luther 2017, Einheitsübersetzung, etc.) which often have restrictive licenses.
- **Required Decision:** Identify a reliable, legally compliant API source for German Bible translations.

### 3.3. Form-of-Address (Du/Sie) Tie-Breaking
- **Problem:** If a document contains an equal number of "Du" and "Sie" addresses, the "predominant" form is undefined.
- **Required Decision:** Define a fallback preference (e.g., default to formal "Sie") or a mechanism for the Agent to ask the user.

### 3.4. LLM Error Recovery
- **Problem:** For large documents (e.g., 50 batches), a single API failure in the middle of the process could cause the entire tool call to fail.
- **Proposed Solution:** Implement a "Partial Result" strategy where successfully processed batches are returned even if some fail, or implement a robust retry mechanism with exponential backoff.

---

## 5. Current Implementation Status (Status-Check 2026-03-06)

### 5.1. Missing Components from Planned Phases
- **Phase 0:** `.env.example` and `tests/unit/test_smoke.py` are missing.
- **Phase 7:** `src/mcp_lektor/server.py` is currently empty and needs to be implemented to register all tools (FastMCP).
- **Phase 8:** `tests/integration/test_end_to_end.py` is empty and requires implementation of full pipeline tests.
- **Phase 9:** `config/agent_system_prompt.md` and `docs/agent-setup-guide.md` are completely missing.

### 5.2. Technical Observations
- **Session Cleanup:** The `_session_store.py` has a `_cleanup_expired` function, but it is only called on-demand during `get_session` or `list_sessions`. It is not running as a background task as specified in the design.
- **Tool Return Types:** `write_corrected_docx` currently returns a `dict`, while `extract_document` and `proofread_text` return a `JSON string`. For consistency and MCP compliance, all tools should return a `str` (JSON formatted).
- **Text Differ:** `tests/unit/test_text_differ.py` is empty. If text diffing logic is needed (e.g., for `UserDecision` with `EDIT`), it should be implemented and tested.
