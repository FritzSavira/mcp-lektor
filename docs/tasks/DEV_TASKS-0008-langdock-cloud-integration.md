# DEV_TASKS-0008: Langdock Cloud Integration

Implementation of Base64 file handling for the remote Langdock endpoint, as defined in the architectural design.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0008: Langdock Cloud Integration and File Handling](../../docs/adr/ADR-0008-langdock-cloud-integration-and-file-handling.md)
*   [DEV_SPEC-0008: Langdock Cloud Integration](../../docs/tasks/DEV_SPEC-0008-langdock-cloud-integration.md)
*   [DEV_TECH_DESIGN-0008: Technical Specification](../../docs/tasks/DEV_TECH_DESIGN-0008-langdock-cloud-integration.md)

---

## Phase 1: Session Manager Enhancements

*Goal: Implement file lifecycle management to prevent disk bloat from Base64 uploads.*

- [x] **Step 1.1: Track Temporary Files in Session**
    - [x] **Action:** Modify `src/mcp_lektor/core/session_manager.py` to include a logic that deletes files listed in a session when that session is pruned or deleted.
    - [x] **Verification:** Check that `prune_expired` now attempts to delete files if a `temp_files` list exists in the session data.

---

## Phase 2: Tool Update - extract_document (Input)

*Goal: Allow the agent to upload documents via Base64.*

- [x] **Step 2.1: Implement Base64 Decoding**
    - [x] **Action:** Update `src/mcp_lektor/tools/extract_document.py` to accept `file_content` (Base64 string) and `filename`.
    - [x] **Action:** If `file_content` is provided, decode it and save it to a temporary path.
    - [x] **Verification (Interactive Test):**
        1. Create a small Base64 string of a valid `.docx` file.
        2. Call `extract_document(file_content="...")` via a test script.
        3. **Expected Result:** A `session_id` and the document structure are returned.

---

## Phase 3: Tool Update - write_corrected_docx (Output)

*Goal: Return the corrected document as Base64 to the agent.*

- [x] **Step 3.1: Implement Base64 Encoding**
    - [x] **Action:** Update `src/mcp_lektor/tools/write_corrected_docx.py` to read the generated file and return it as a Base64 string in the JSON payload.
    - [x] **Verification (Interactive Test):**
        1. Run `write_corrected_docx` for an active session.
        2. **Expected Result:** The JSON response contains a `file_content` key with a long Base64 string.

---

## Phase 4: Final Integration and Cleanup

*Goal: Ensure everything works together and documentation is updated.*

- [x] **Step 4.1: Update Tool Docstrings**
    - [x] **Action:** Update all tool docstrings in `src/mcp_lektor/tools/` to reflect the new parameters and cloud-native usage.
    - [x] **Verification:** Run `ruff check src/mcp_lektor/tools/` to ensure docstrings are correctly formatted.

- [x] **Step 4.2: Final Integration Test**
    - [x] **Action:** Run the full suite: `pytest tests/integration/test_end_to_end.py`.
    - [x] **Verification:** All tests must pass.

- [x] **Step 4.3: Update Changelog**
    - [x] **Action:** Add a new entry to `docs/CHANGELOG.md` under "[Unreleased]".
    - [x] **Verification:** File is saved and formatted.
