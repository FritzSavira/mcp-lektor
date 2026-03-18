# Requirements Analysis & Specification: Langdock Cloud Integration

This document details the requirements for enabling the MCP-Lektor to function as a remote Langdock integration, as described in **ADR-0008**.

---

### 1. Detailed Requirements Specification

The primary goal is to decouple the MCP tools from the local filesystem to allow a remote Langdock agent to interact with the server via a public SSE endpoint.

#### 1.1 Base64 Document Input
*   The `extract_document` tool must be extended to accept a `file_content` string (Base64 encoded).
*   If `file_content` is provided, the server must:
    *   Validate that it is a valid Base64 string.
    *   Save it as a temporary `.docx` file in a secure temporary directory (e.g., `/tmp/mcp_lektor/`).
    *   Process the file using the existing `parse_docx` logic.
*   The tool must still support the existing `file_path` parameter for backward compatibility with local testing and the Streamlit GUI.

#### 1.2 Base64 Document Output
*   The `write_corrected_docx` tool must be updated to return the corrected document's content as a Base64 string in its JSON response.
*   The response must include the `filename`, `content_type` (application/vnd.openxmlformats-officedocument.wordprocessingml.document), and the `file_content` (Base64).

#### 1.3 Tool Documentation (LLM Guidance)
*   Docstrings for all tools must be updated to clearly explain the transition from local paths to session-based interaction.
*   The LLM must be instructed to use the `session_id` returned by `extract_document` for all subsequent calls.

---

### 2. User Stories & Acceptance Criteria

**Epic: Cloud-Based Proofreading via Langdock**

*   **User Story 1: Upload Document via Base64**
    *   **As a Langdock Agent,** I want to send a Base64-encoded `.docx` file to the MCP server **so that** it can be parsed without requiring shared file access.
    *   **Acceptance Criteria:**
        *   `extract_document` accepts `file_content` (Base64).
        *   Server successfully decodes and parses the document structure.
        *   A valid `session_id` is returned.
        *   Invalid Base64 or non-docx content returns a clear error message.

*   **User Story 2: Download Corrected Document via Base64**
    *   **As a Langdock Agent,** I want to receive the final corrected document as a Base64 string **so that** I can provide it back to the user in the chat.
    *   **Acceptance Criteria:**
        *   `write_corrected_docx` includes the `file_content` (Base64) in its JSON output.
        *   The returned Base64 string can be decoded back into a valid, readable `.docx` file.
        *   The `filename` is preserved or correctly generated.

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   Base64 input for `extract_document`.
        *   Base64 output for `write_corrected_docx`.
    *   **Should-Have:**
        *   Automated cleanup of temporary files created from Base64 inputs.
        *   Improved error handling for large files.
    *   **Could-Have:**
        *   Temporary signed download URLs instead of large Base64 strings.
    *   **Won't-Have (in this increment):**
        *   Persistent database storage for documents (staying with `session_manager` for now).

*   **Dependencies:**
    1.  **Base64 Logic:** Depends on `python-docx` (already present) and standard library `base64`.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| BL-001 | Cloud Integration | Implement Base64 decoding in `extract_document` | Must |
| BL-002 | Cloud Integration | Implement Base64 encoding in `write_corrected_docx` | Must |
| BL-004 | Documentation | Update tool docstrings for Langdock compatibility | Should |

---

### 5. Definition of Done (DoD)

A Product Backlog Item is considered "Done" when all of the following criteria are met:

*   **Code Quality:** The code is written and formatted according to the guidelines in `docs/CODING_STYLE.md` (`black .`, `ruff check .`).
*   **Tests:**
    *   Unit tests for Base64 encoding/decoding logic.
    *   Integration test simulating a remote MCP call with Base64 data.
    *   All existing tests continue to pass.
*   **Acceptance Criteria:** All acceptance criteria defined for the story have been met.
*   **Documentation:** `CHANGELOG.md` is updated.
*   **Verification:** Verified via a manual test script (e.g., `scripts/interactive_e2e_test.py` updated for remote simulation).
