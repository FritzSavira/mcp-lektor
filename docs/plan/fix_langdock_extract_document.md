# Plan: Fix Langdock Document Extraction

## Objective
Enable the Langdock Agent to correctly upload and process documents by using Base64 encoding instead of local file paths.

## Key Files & Context
- `docs/agent/AGENT_SYSTEM_PROMPT.md`: Needs instructions for the Agent to use `file_content` (Base64).
- `src/mcp_lektor/tools/extract_document.py`: Docstring should prioritize `file_content` for cloud usage.
- `tests/integration/test_extract_document.py`: Missing test case for Base64 input.

## Implementation Steps

### 1. Update Agent System Prompt
Modify `docs/agent/AGENT_SYSTEM_PROMPT.md` to explicitly instruct the Agent on how to handle file uploads:
- Explain that `file_content` (Base64) MUST be used.
- Explain that `file_path` is only for local server files.
- Provide a clear instruction: "Extrahierte den Inhalt des Dokuments als Base64-String und rufe `extract_document` mit dem Parameter `file_content` auf."

### 2. Refine Tool Documentation
Update `src/mcp_lektor/tools/extract_document.py`:
- Move `file_content` to a more prominent position in the docstring.
- Explicitly state that `file_content` is the required parameter for remote/cloud environments like Langdock.

### 3. Add Integration Test
Update `tests/integration/test_extract_document.py`:
- Add a new test case `test_extract_via_base64` that simulates a Base64 upload (using a small dummy docx or an existing fixture).
- Verify that a `session_id` is returned and a temp file is created.

## Verification & Testing
- Run `pytest tests/integration/test_extract_document.py`.
- Run `scripts/test_base64_upload.py` to ensure end-to-end cloud flow works.
- (Manual) Verify the updated system prompt is clear and follows the `CODING_STYLE.md`.
