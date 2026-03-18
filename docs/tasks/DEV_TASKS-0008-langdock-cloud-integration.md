# DEV_TASKS-0008: Langdock Cloud Integration

Implementation of Base64 file handling and API Key authentication for the remote Langdock endpoint, as defined in the architectural design.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0008: Langdock Cloud Integration and File Handling](../../docs/adr/ADR-0008-langdock-cloud-integration-and-file-handling.md)
*   [DEV_SPEC-0008: Langdock Cloud Integration](../../docs/tasks/DEV_SPEC-0008-langdock-cloud-integration.md)
*   [DEV_TECH_DESIGN-0008: Technical Specification](../../docs/tasks/DEV_TECH_DESIGN-0008-langdock-cloud-integration.md)

---

## Phase 1: Configuration and Environment

*Goal: Add the `LEKTOR_API_KEY` to the configuration system and environment variables.*

- [ ] **Step 1.1: Update Config Models**
    - [ ] **Action:** Add `api_key: Optional[str] = None` to the `ServerConfig` class in `src/mcp_lektor/config/models.py`.
    - [ ] **Verification:** Run `ruff check src/mcp_lektor/config/models.py` to ensure no syntax or linting errors.

- [ ] **Step 1.2: Update .env.example**
    - [ ] **Action:** Add `LEKTOR_API_KEY=your_secret_key_here` to `.env.example`.
    - [ ] **Verification:** Confirm the file contains the new variable.

- [ ] **Step 1.3: Update Local .env**
    - [ ] **Action:** Add a test API key to your local `.env` file: `LEKTOR_API_KEY=test-key-123`.
    - [ ] **Verification (Interactive Test):**
        1. Open a python shell.
        2. Run: `from mcp_lektor.config.settings import get_settings; print(get_settings().server.api_key)`
        3. **Expected Result:** `test-key-123` is printed.

---

## Phase 2: Session Manager Enhancements

*Goal: Implement file lifecycle management to prevent disk bloat from Base64 uploads.*

- [ ] **Step 2.1: Track Temporary Files in Session**
    - [ ] **Action:** Modify `src/mcp_lektor/core/session_manager.py` to include a logic that deletes files listed in a session when that session is pruned or deleted.
    - [ ] **Verification:** Check that `prune_expired` now attempts to delete files if a `temp_files` list exists in the session data.

---

## Phase 3: Tool Update - extract_document (Input)

*Goal: Allow the agent to upload documents via Base64.*

- [ ] **Step 3.1: Implement Base64 Decoding**
    - [ ] **Action:** Update `src/mcp_lektor/tools/extract_document.py` to accept `file_content` (Base64 string) and `filename`.
    - [ ] **Action:** If `file_content` is provided, decode it and save it to a temporary path.
    - [ ] **Verification (Interactive Test):**
        1. Create a small Base64 string of a valid `.docx` file.
        2. Call `extract_document(file_content="...")` via a test script.
        3. **Expected Result:** A `session_id` and the document structure are returned.

---

## Phase 4: Tool Update - write_corrected_docx (Output)

*Goal: Return the corrected document as Base64 to the agent.*

- [ ] **Step 4.1: Implement Base64 Encoding**
    - [ ] **Action:** Update `src/mcp_lektor/tools/write_corrected_docx.py` to read the generated file and return it as a Base64 string in the JSON payload.
    - [ ] **Verification (Interactive Test):**
        1. Run `write_corrected_docx` for an active session.
        2. **Expected Result:** The JSON response contains a `file_content` key with a long Base64 string.

---

## Phase 5: Security Layer (API Key Middleware)

*Goal: Protect the SSE endpoint from unauthorized access.*

- [ ] **Step 5.1: Create Middleware**
    - [ ] **Action:** Implement the `APIKeyMiddleware` in `src/mcp_lektor/server.py` as described in the Technical Design.
    - [ ] **Action:** Add the middleware to the `mcp.app`.
    - [ ] **Verification (Interactive Test):**
        1. Start the server: `python -m mcp_lektor.server`.
        2. Try to access `http://localhost:8080/sse` without the header.
        3. **Expected Result:** 401 Unauthorized.
        4. Try with `X-API-Key: test-key-123`.
        5. **Expected Result:** 200 OK (or SSE stream starts).

---

## Phase 6: Final Integration and Cleanup

*Goal: Ensure everything works together and documentation is updated.*

- [ ] **Step 6.1: Update Tool Docstrings**
    - [ ] **Action:** Update all tool docstrings in `src/mcp_lektor/tools/` to reflect the new parameters and cloud-native usage.
    - [ ] **Verification:** Run `ruff check src/mcp_lektor/tools/` to ensure docstrings are correctly formatted.

- [ ] **Step 6.2: Final Integration Test**
    - [ ] **Action:** Run the full suite: `pytest tests/integration/test_end_to_end.py`.
    - [ ] **Verification:** All tests must pass.

- [ ] **Step 6.3: Update Changelog**
    - [ ] **Action:** Add a new entry to `docs/CHANGELOG.md` under "[Unreleased]".
    - [ ] **Verification:** File is saved and formatted.
