### **ADR-0001: MCP-Based Interactive Proofreading Server for Langdock**

**Status:** proposed

**Date:** 2026-03-04

#### **1. Context and Problem Statement**

The organization produces a variety of German-language publications — both print (brochures, flyers, periodicals) and digital (blog posts, web content). These documents are delivered as Microsoft Word (.docx) files that are already formatted with paragraph styles, bold/italic emphasis, headings, and inline editorial annotations (e.g., red text in square brackets marking placement instructions for graphics and design elements).

A professional-grade proofreading solution is needed that performs the following checks:
- **Spelling, grammar, and punctuation** (Rechtschreibung, Grammatik, Zeichensetzung)
- **Typography** (correct quotation marks, dashes, spacing conventions)
- **Bible reference validation** (online-verified, with source citation)
- **Quotation and quotation mark verification** (Zitat- und Anführungszeichenprüfung)
- **Form-of-address consistency** (Du/Sie/Ihr) across the entire document
- **Commonly confused words scan** (Verwechslungswörter)

Critical constraints:
1. All existing formatting in the Word document **must be preserved**. Loss of formatting renders the proofreading output useless.
2. Proposed changes must be written as **Track Changes** (revision marks) in the output .docx file.
3. Each change must include a **comment** at the affected location explaining the correction.
4. The solution must support **two interaction modes**:
   - **Fully automatic** (Stage 1): Upload → Proofread → Receive corrected .docx
   - **Interactive review** (Stage 2): Upload → Review each change in chat → Approve/reject/edit → Receive corrected .docx
5. The solution should operate **within the Langdock ecosystem** to avoid media breaks and additional tooling for end users.

The core challenge is: Langdock's native chat interface extracts plain text from uploaded Word files, losing all formatting. Therefore, a backend service is required that can manipulate .docx files at the OpenXML level while remaining seamlessly accessible from within Langdock.

#### **2. Decision**

We will build a **Model Context Protocol (MCP) server** in **Python** that exposes proofreading capabilities as discrete tools, integrated into Langdock as a custom integration. A Langdock Agent with a tailored system prompt will serve as the user-facing interface.

**Architecture Overview:**

The MCP server exposes four tools:

| Tool | Responsibility |
|------|---------------|
| `extract_document` | Reads the .docx file, preserves formatting metadata, identifies red-text placeholders, and returns structured text with positional references |
| `proofread_text` | Sends text paragraph-by-paragraph to the LLM with proofreading rules; returns a structured JSON list of proposed changes (original, suggestion, category, confidence level) |
| `validate_bible_refs` | Extracts all Bible references from the text and validates them against an external API; returns validation results per reference |
| `write_corrected_docx` | Accepts the original .docx and a list of approved changes; writes them as OpenXML Track Changes (`<w:ins>`, `<w:del>`) with inline comments; returns the modified .docx |

**Technology choices:**
- **Language: Python 3.11+** — chosen for its unique combination of mature .docx manipulation libraries (`python-docx` + `lxml` for low-level OpenXML access), an official MCP SDK, first-class LLM API support, and strong NLP/text-processing ecosystem.
- **Word manipulation: `python-docx` + `lxml`** — `python-docx` provides high-level document access; `lxml` enables direct OpenXML manipulation for Track Changes and comment insertion, which `python-docx` does not natively support.
- **MCP framework: Official Anthropic MCP Python SDK** — ensures protocol compliance and forward compatibility.
- **LLM access: Langdock API (OpenAI-compatible)** — used within `proofread_text` for the actual proofreading intelligence.
- **Bible reference validation: External REST API** — queried by `validate_bible_refs` for online verification with source citation.

**Interaction modes:**
- **Stage 1 (automatic):** The Agent calls all four tools sequentially and returns the corrected .docx.
- **Stage 2 (interactive):** The Agent calls `extract_document` and `proofread_text`, presents the change list in chat (grouped by confidence: obvious fixes batched, stylistic/content changes presented individually), waits for user decisions, then calls `write_corrected_docx` with only the approved changes.

The mode selection is controlled entirely via the Agent's system prompt and user intent detection — no code changes required.

**Deployment:** The MCP server runs as a lightweight service (e.g., Docker container) on the organization's infrastructure and is registered in Langdock as a custom MCP integration.

#### **3. Consequences of the Decision**

**Positive Consequences (Advantages):**

- **No media break:** Users stay entirely within Langdock (Chat, MS Teams integration, or Workflows). No additional application, no separate UI, no extra credentials.
- **Formatting integrity:** By operating on the .docx at the OpenXML/XML level, all formatting, styles, colors, and editorial annotations are preserved byte-perfectly.
- **Professional output:** Track Changes and comments are the industry-standard mechanism for editorial review in publishing workflows. The output integrates seamlessly into existing editorial processes.
- **Platform-wide reusability:** As an MCP tool, the proofreading capability is available to any Agent, any Workflow, and any API consumer in the Langdock workspace — not locked into a single assistant.
- **Flexible interaction:** Both fully automatic and interactive review modes are supported without architectural changes, purely through conversational flow.
- **Team-ready:** Sharing, permissions, and user management are handled by Langdock's existing workspace infrastructure.
- **Extensible:** New proofreading rules, languages, or checks can be added as additional MCP tools or by extending existing ones, without touching the frontend.

**Negative Consequences (Disadvantages):**

- **OpenXML complexity:** Implementing Track Changes at the XML level (`<w:ins>`, `<w:del>`, `<w:commentRangeStart>`) is non-trivial. `python-docx` does not provide a high-level API for this; manual XML construction via `lxml` is required. This increases initial development effort and demands deep OpenXML knowledge.
- **Infrastructure requirement:** The MCP server requires hosting (a server or container runtime). This introduces an operational dependency beyond the Langdock SaaS platform.
- **Stage 2 UX limitations:** The interactive review mode relies on chat-based text interaction. While functional, it lacks the richness of a dedicated UI (no inline diff highlighting, no click-to-approve buttons). For documents with 100+ changes, the chat-based review can become cumbersome despite confidence-based batching.
- **File transfer dependency:** The mechanism for passing binary .docx files between Langdock and the MCP server depends on Langdock's MCP file handling capabilities, which may impose size limits or require workarounds (e.g., temporary file storage with URL references).
- **LLM token costs:** Large documents processed paragraph-by-paragraph will consume significant tokens. A 20-page brochure could require multiple LLM calls, impacting cost and latency.

#### **4. Alternatives Considered**

**Alternative A: Langdock Agent with Knowledge Folder (No Code)**
- A pure no-code approach using a Langdock Agent with a proofreading system prompt and a Knowledge Folder containing style guides and word lists.
- **Rejected because:** Langdock extracts plain text from uploaded .docx files, destroying all formatting. The Agent cannot produce a modified .docx with Track Changes. This is a fundamental architectural limitation, not solvable through better prompting. The core requirements (preserve formatting, Track Changes, comments) are unachievable.

**Alternative B: Standalone API Application (Concept 4)**
- A self-contained web application (e.g., Python/Flask + Streamlit frontend) that uses the Langdock API for LLM access and `python-docx` for Word manipulation.
- **Rejected because:** This introduces a separate frontend, creating a media break. Users must leave Langdock, learn a new interface, and the organization must build and maintain its own UI, authentication, and hosting. The backend logic is identical to the MCP approach, but the UX is strictly worse for internal team use. This option remains viable only if the tool needs to be offered to external users without Langdock access.

**Alternative C: Python Backend with TypeScript**
- Using TypeScript/Node.js instead of Python for the MCP server, leveraging the TypeScript MCP SDK (which is the reference implementation).
- **Rejected because:** The Node.js `docx` library is optimized for document *creation*, not *manipulation* of existing files. Implementing Track Changes on existing .docx files in TypeScript would require low-level XML handling without the mature ecosystem that Python's `python-docx` + `lxml` combination provides. MCP support is equally strong in both languages, but the Word manipulation gap is decisive.

**Alternative D: C# / .NET with OpenXML SDK**
- Using Microsoft's own OpenXML SDK, which provides the most complete and officially supported API for Word document manipulation, including native Track Changes support.
- **Rejected because:** There is no official MCP SDK for C#/.NET. Implementing the MCP protocol from scratch adds significant effort and maintenance risk. The LLM API ecosystem is also less mature in .NET compared to Python. While C# would be superior for the Word manipulation aspect in isolation, the combined requirements favor Python.

**Alternative E: Langdock Workflow (No Custom Backend)**
- Using Langdock's built-in Workflow feature to chain multiple Agent steps (extract → proofread → validate → output).
- **Rejected because:** Workflows operate on the same text-extraction layer as Agents. They cannot access or produce binary .docx files with formatting preserved. The same fundamental limitation as Alternative A applies.
