### **ADR-0008: Langdock Cloud Integration and File Handling**

**Status:** Proposed

**Date:** 2026-03-17

#### **1. Context and Problem Statement**

The MCP-Lektor was originally developed in a local environment where the MCP server and the client (the Streamlit GUI) shared the same filesystem. Consequently, the existing MCP tools (`extract_document`, `write_corrected_docx`) rely on local absolute or relative file paths to read and write `.docx` files.

The project is now transitioning to a production-ready Langdock integration. The server is exposed via a public SSE endpoint (`https://lektor.smwh.de/sse`). In this cloud-based scenario:
1.  **Isolated Filesystems:** The Langdock agent (client) does not have direct access to the server's local filesystem.
2.  **Data Transfer:** The agent needs to send the document content to the server and receive the corrected document back.
3.  **Statelessness vs. Sessions:** While the server currently uses an in-memory `session_manager`, the initial "handshake" (sending the file) must support non-local data.
4.  **Security:** A public endpoint requires authentication to prevent unauthorized use of the LLM-powered proofreading engine.

#### **2. Decision**

To enable seamless Langdock integration, we will implement the following architectural changes:

1.  **Base64-encoded File Transfer:**
    *   Update `extract_document` to accept an optional `file_content` parameter (Base64 string).
    *   If `file_content` is provided, the server will decode it and save it to a temporary location in its local `/tmp` directory to maintain compatibility with existing `python-docx` logic.
    *   The tool will continue to return a `session_id` for subsequent atomic operations.

2.  **Flexible Output Retrieval:**
    *   Update `write_corrected_docx` to return not just the `output_path` (which is useless to a remote client), but also the `file_content` as a Base64 string.
    *   Optionally, if file sizes become an issue for MCP message limits, implement a temporary "download URL" mechanism (though Base64 is preferred for initial simplicity as most `.docx` files are < 5MB).

3.  **API Key Authentication:**
    *   Implement an API Key check in the FastMCP/SSE server setup.
    *   Clients must provide a valid `X-API-Key` header (supported by Langdock custom MCP headers).

4.  **Tool Metadata Optimization:**
    *   Refine the tool descriptions (docstrings) to explicitly guide the Langdock LLM on how to handle the file content vs. session IDs.

#### **3. Consequences of the Decision**

**Positive Consequences (Advantages):**
*   **Cloud Compatibility:** Enables the server to run in a containerized cloud environment without shared storage.
*   **Agent Autonomy:** Langdock agents can "read" files from their own context and "upload" them to the server via the tool call.
*   **Security:** Protects the endpoint from unauthorized API consumption.
*   **Backward Compatibility:** Existing local/GUI workflows can still use `file_path` if the server is configured for local access.

**Negative Consequences (Disadvantages):**
*   **Message Size Limits:** Base64 encoding adds ~33% overhead. Very large documents might hit MCP or SSE message size limits (typically 4MB-10MB).
*   **Memory Usage:** Processing large Base64 strings increases the memory footprint of the server process.
*   **Complexity:** The tools need to handle two modes of input (path vs. content).

#### **4. Alternatives Considered**

*   **Signed URLs (S3/Object Storage):** The agent uploads the file to a bucket and sends the URL to the MCP server. The server then uploads the result back to the bucket. 
    *   *Reason for Rejection:* Adds significant infrastructure complexity (S3 setup, bucket management, lifecycle policies) for a prototype stage.
*   **Permanent Database for Sessions:** Replacing the in-memory manager with Redis/PostgreSQL.
    *   *Decision:* Deferred to a later ADR (see `DEV_OPEN_QUESTIONS-0001`). For the Langdock integration, the data transfer logic is the immediate priority.
*   **Direct Streamlit integration in Langdock:**
    *   *Reason for Rejection:* Langdock is designed for MCP servers, not GUI embeds. The tool-based approach is the idiomatic way to build "Agents".
