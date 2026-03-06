# Requirements Analysis & Specification: MCP-Based Interactive Proofreading Server

This document details the requirements for the MCP-Based Interactive Proofreading Server for Langdock, as described in **[ADR-0001](docs/adr/ADR-0001-mcp-based-interactive-proofreading-server.md)**.

---

### 1. Detailed Requirements Specification

#### 1.1 Functional Requirements

##### FR-01: Document Ingestion & Formatting Preservation
The system must read `.docx` files and extract text content while preserving a complete representation of:
- Paragraph structure (headings, body text, lists)
- Character formatting (bold, italic, underline, font size, font family)
- Text color (especially red text used for editorial annotations)
- Tables, headers, footers
- Inline annotations in square brackets (e.g., `[Bild: Logo einfügen]`)
- Paragraph and character styles

The system must **not** modify, remove, or reorder any formatting that is not explicitly part of a proofreading correction.

##### FR-02: Proofreading — Spelling, Grammar, Punctuation
The system must detect and propose corrections for:
- German spelling errors (new and old orthography awareness, with neue Rechtschreibung as default)
- Grammatical errors (case, gender, verb conjugation, sentence structure)
- Punctuation errors (comma rules per Duden, period, colon, semicolon usage)
- Each proposed correction must include a category label and a short explanation.

##### FR-03: Proofreading — Typography
The system must detect and propose corrections for:
- Incorrect quotation marks (e.g., "..." instead of „..." for German)
- Incorrect dashes (hyphen vs. en-dash vs. em-dash)
- Incorrect spacing (e.g., before punctuation, non-breaking spaces)
- Incorrect apostrophes (e.g., ' vs. ')
- Ellipsis usage (... vs. …)

##### FR-04: Bible Reference Validation
The system must:
- Detect all Bible references in the text (e.g., Mt 5,3–12; 1. Kor 13,4-7; Gen 1,1)
- Validate each reference against an authoritative online source
- Report whether the reference is valid (book, chapter, verse exist)
- Flag incorrect or ambiguous references with a suggested correction
- Include the validation source in the comment

##### FR-05: Quotation and Quotation Mark Verification
The system must:
- Detect all quoted passages
- Verify that opening and closing quotation marks are correctly paired
- Verify that German typographic quotation marks are used consistently („..." and ‚...' for nested quotes)
- Flag mismatched, missing, or stylistically incorrect quotation marks

##### FR-06: Form-of-Address Consistency
The system must:
- Detect all forms of address in the document (Du/du, Sie, Ihr/ihr, Euch/euch)
- Determine the predominant form of address
- Flag all deviations from the predominant form
- Propose corrections to achieve consistency
- Handle edge cases: "Sie" as third-person plural vs. formal address; "ihr" as possessive pronoun vs. address form

##### FR-07: Commonly Confused Words Scan (Verwechslungswörter)
The system must detect and flag commonly confused German words, including but not limited to:
- scheinbar / anscheinend
- seid / seit
- das / dass
- wider / wieder
- weise / Weise / -weise
- Tod / tot
- Standard / Standarte
- Each flag must include a short explanation of the correct usage in context.

##### FR-08: Track Changes Output
The system must write all accepted corrections to the output `.docx` as OpenXML Track Changes:
- Deletions as `<w:del>` elements
- Insertions as `<w:ins>` elements
- Each revision must include an author name (e.g., "MCP Lektor") and a timestamp
- The resulting file must open correctly in Microsoft Word, LibreOffice Writer, and Google Docs with revisions visible

##### FR-09: Comment Insertion
The system must insert a Word comment at each corrected location containing:
- The category of the correction (e.g., "Rechtschreibung", "Typografie", "Bibelstelle")
- A brief explanation of why the change was made
- For Bible references: the validation source URL or name

##### FR-10: Red-Text / Placeholder Preservation
The system must:
- Detect text formatted in red color and/or contained in square brackets
- Treat such text as editorial/design annotations
- **Never modify, correct, or flag** this text
- Preserve its exact formatting and position in the output file

##### FR-11: Automatic Mode (Stage 1)
The system must support a fully automatic workflow:
1. Receive a `.docx` file
2. Perform all proofreading checks (FR-02 through FR-07)
3. Write all corrections as Track Changes with comments (FR-08, FR-09)
4. Return the corrected `.docx` file
No user interaction is required between input and output.

##### FR-12: Interactive Mode (Stage 2)
The system must support an interactive review workflow:
1. Receive a `.docx` file
2. Perform all proofreading checks (FR-02 through FR-07)
3. Return a structured list of proposed changes to the Agent (not yet written to the file)
4. The Agent presents changes to the user, grouped by confidence level:
   - **High confidence** (obvious errors): presented as a batch for bulk approval
   - **Medium confidence** (stylistic suggestions): presented individually
   - **Low confidence / content-sensitive** (Bible refs, confused words): presented individually with detailed explanation
5. The user responds with approvals, rejections, and edits per change
6. The Agent calls the write tool with only the approved/edited changes
7. Return the corrected `.docx` file

##### FR-13: Selective Proofreading
The system must allow the user to request only specific checks (e.g., "only check Bible references", "only spelling, no style"). The Agent's system prompt must support intent detection for partial proofreading requests.

#### 1.2 Non-Functional Requirements

##### NFR-01: Performance
- Documents up to 20 pages must be processed within 120 seconds (Stage 1).
- The change list for Stage 2 must be returned within 90 seconds.

##### NFR-02: Accuracy
- Zero false modifications to formatting, colors, or placeholder text.
- Proofreading precision target: ≥ 90% of proposed changes should be genuinely correct.

##### NFR-03: Compatibility
- Output `.docx` files must open correctly with Track Changes visible in:
  - Microsoft Word 2016+
  - LibreOffice Writer 7+
  - Google Docs (import)

##### NFR-04: Security
- The MCP server must not persist uploaded documents beyond the processing session.
- All communication between Langdock and the MCP server must use HTTPS/TLS.
- No document content may be logged or stored permanently.

##### NFR-05: Reliability
- The MCP server must handle malformed `.docx` files gracefully with a clear error message.
- If the Bible reference API is unavailable, the system must skip validation (not fail) and inform the user.

##### NFR-06: Maintainability
- Proofreading rules (confused words list, typography rules) must be configurable without code changes (e.g., via JSON/YAML config files).
- The system must support adding new proofreading categories without architectural changes.

---

### 2. User Stories & Acceptance Criteria

**Epic 1: Document Processing & Formatting Preservation**

*   **US-01: Upload and Process a Word Document**
    *   **As a** Langdock user, **I want to** upload a formatted `.docx` file to the Lektor Agent, **so that** I can have it proofread without leaving Langdock.
    *   **Acceptance Criteria:**
        *   The Agent accepts `.docx` files via the Langdock chat file upload.
        *   The MCP `extract_document` tool is invoked automatically upon upload.
        *   The user receives confirmation that the document has been received and processing has started.
        *   Files larger than 50 MB are rejected with a clear error message.

*   **US-02: Preserve All Formatting**
    *   **As a** user, **I want** the corrected document to retain all original formatting, **so that** I can use it directly in my publishing workflow.
    *   **Acceptance Criteria:**
        *   Bold, italic, underline, font sizes, font families are identical in input and output.
        *   Paragraph styles (Heading 1–6, Body Text, List, etc.) are preserved.
        *   Tables, headers, and footers are unchanged.
        *   No empty paragraphs are added or removed.

*   **US-03: Preserve Red-Text Placeholders**
    *   **As a** layout editor, **I want** all red-colored text and square-bracket annotations to remain untouched, **so that** design placement instructions survive the proofreading process.
    *   **Acceptance Criteria:**
        *   Text with red font color (RGB or theme color) is never modified.
        *   Text enclosed in square brackets `[...]` that is red-colored is never flagged or altered.
        *   A summary of detected placeholders is shown to the user (count and locations).

**Epic 2: Proofreading Checks**

*   **US-04: Spelling and Grammar Check**
    *   **As a** user, **I want** the system to find and correct spelling and grammar errors, **so that** my publication is error-free.
    *   **Acceptance Criteria:**
        *   Misspelled words are detected and a correction is proposed.
        *   Grammatical errors (case, gender, conjugation) are detected.
        *   Each correction includes a brief explanation.
        *   Proper nouns and technical terms are not falsely flagged (best effort).

*   **US-05: Punctuation Check**
    *   **As a** user, **I want** punctuation errors to be corrected, **so that** my text follows Duden rules.
    *   **Acceptance Criteria:**
        *   Missing and incorrect commas are detected.
        *   Incorrect period, colon, and semicolon usage is flagged.
        *   Explanations reference the applicable rule where possible.

*   **US-06: Typography Check**
    *   **As a** user, **I want** typographic errors to be corrected, **so that** my publication meets professional print/web standards.
    *   **Acceptance Criteria:**
        *   Straight quotation marks ("...") are flagged and German typographic marks („...") are proposed.
        *   Hyphens used as en-dashes are detected (e.g., "S. 5-12" → "S. 5–12").
        *   Incorrect apostrophes and ellipses are flagged.

*   **US-07: Bible Reference Validation**
    *   **As a** user, **I want** all Bible references in my text to be verified, **so that** I can be sure they are accurate before publication.
    *   **Acceptance Criteria:**
        *   All Bible reference patterns are detected (e.g., "Mt 5,3–12", "1. Mose 1,1", "Ps 23").
        *   Each reference is validated against an online source.
        *   Invalid references are flagged with a comment that includes the source.
        *   If the online source is unavailable, the user is informed and validation is skipped (not failed).

*   **US-08: Quotation Mark Verification**
    *   **As a** user, **I want** quotation marks to be checked for correctness and consistency, **so that** my text is typographically clean.
    *   **Acceptance Criteria:**
        *   Unpaired quotation marks are detected.
        *   Non-German quotation mark styles are flagged.
        *   Nested quotes are checked for correct „outer" and ‚inner' usage.

*   **US-09: Form-of-Address Consistency**
    *   **As a** user, **I want** the system to ensure consistent use of Du/Sie/Ihr throughout my document, **so that** the text does not mix formal and informal address.
    *   **Acceptance Criteria:**
        *   The predominant form of address is detected and reported.
        *   All deviations are flagged with a proposed correction.
        *   Ambiguous cases (e.g., "Sie" as third-person plural) are handled with context awareness.

*   **US-10: Commonly Confused Words**
    *   **As a** user, **I want** commonly confused German words to be flagged, **so that** I avoid embarrassing semantic errors.
    *   **Acceptance Criteria:**
        *   Words from the configured confused-words list are checked in context.
        *   Each flag includes an explanation of the correct usage.
        *   Context-sensitive analysis distinguishes correct from incorrect usage (not just pattern matching).

**Epic 3: Output & Revision Workflow**

*   **US-11: Track Changes in Output File**
    *   **As a** user, **I want** corrections to appear as Track Changes in the Word document, **so that** I can review them using Word's built-in revision tools.
    *   **Acceptance Criteria:**
        *   Deletions appear as struck-through red text in Word's revision view.
        *   Insertions appear as underlined colored text.
        *   Each revision has an author ("MCP Lektor") and a timestamp.
        *   The file opens correctly in MS Word, LibreOffice, and Google Docs.

*   **US-12: Comments per Correction**
    *   **As a** user, **I want** each correction to include a Word comment, **so that** I understand why a change was made.
    *   **Acceptance Criteria:**
        *   Each Track Change has an associated comment.
        *   The comment includes the correction category and explanation.
        *   Comments are positioned at the exact text location of the change.

**Epic 4: Interaction Modes**

*   **US-13: Fully Automatic Proofreading (Stage 1)**
    *   **As a** user, **I want to** upload a document and receive the fully corrected version without further interaction, **so that** I save time on routine checks.
    *   **Acceptance Criteria:**
        *   The user uploads a file and says something like "Lektoriere das komplett."
        *   All checks are performed automatically.
        *   The corrected `.docx` is returned as a downloadable file in the chat.
        *   Processing time ≤ 120 seconds for documents up to 20 pages.

*   **US-14: Interactive Review (Stage 2)**
    *   **As a** user, **I want to** review each proposed change before it is applied, **so that** I maintain full editorial control.
    *   **Acceptance Criteria:**
        *   The user uploads a file and says something like "Lektoriere das, ich will jede Änderung freigeben."
        *   Changes are presented in a structured table in the chat, grouped by confidence.
        *   The user can approve, reject, or edit individual changes using natural language.
        *   Only approved changes are written to the output file.
        *   The user can approve high-confidence changes as a batch.

*   **US-15: Selective Check Request**
    *   **As a** user, **I want to** request only specific types of checks, **so that** I can focus on what matters for a given document.
    *   **Acceptance Criteria:**
        *   The user can say "Prüfe nur die Bibelstellen" or "Nur Rechtschreibung, kein Stil."
        *   Only the requested checks are performed.
        *   The output file contains only changes from the requested categories.

**Epic 5: MCP Server & Infrastructure**

*   **US-16: MCP Server Registration**
    *   **As a** workspace admin, **I want to** register the proofreading MCP server as a Langdock custom integration, **so that** it is available to all team members.
    *   **Acceptance Criteria:**
        *   The MCP server URL is configurable in Langdock's integration settings.
        *   All four MCP tools are discovered and listed by Langdock.
        *   The integration can be enabled/disabled by the admin.

*   **US-17: Error Handling**
    *   **As a** user, **I want** clear error messages when something goes wrong, **so that** I know what to do next.
    *   **Acceptance Criteria:**
        *   Malformed `.docx` files produce a message like "The uploaded file could not be read. Please ensure it is a valid .docx file."
        *   Bible API unavailability produces: "Bible reference validation is currently unavailable. All other checks were performed."
        *   Timeout is communicated: "The document is too large for processing in a single pass. Consider splitting it."

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   US-01: Upload and process Word document
        *   US-02: Preserve all formatting
        *   US-03: Preserve red-text placeholders
        *   US-04: Spelling and grammar check
        *   US-05: Punctuation check
        *   US-11: Track Changes in output
        *   US-12: Comments per correction
        *   US-13: Fully automatic mode (Stage 1)
        *   US-16: MCP server registration
        *   US-17: Error handling
    *   **Should-Have:**
        *   US-06: Typography check
        *   US-08: Quotation mark verification
        *   US-09: Form-of-address consistency
        *   US-10: Commonly confused words
        *   US-14: Interactive review mode (Stage 2)
    *   **Could-Have:**
        *   US-07: Bible reference validation (depends on external API availability)
        *   US-15: Selective check requests
    *   **Won't-Have (in this increment):**
        *   Multi-language support (English, French, etc.)
        *   PDF input support
        *   Automated style guide enforcement beyond the defined checks
        *   Real-time collaborative editing

*   **Dependencies:**
    1.  **US-01 → ALL:** Document ingestion is the foundation. No other story can function without it.
    2.  **US-02, US-03 → US-11, US-12:** Formatting preservation must work before Track Changes can be safely written.
    3.  **US-04, US-05 → US-11:** Proofreading results must exist before they can be materialized as revisions.
    4.  **US-11, US-12 → US-13:** The automatic mode requires working Track Changes output.
    5.  **US-13 → US-14:** Interactive mode builds on the automatic pipeline, adding the review loop between analysis and writing.
    6.  **US-16 → US-01:** The MCP server must be registered before any tool can be invoked.
    7.  **US-06, US-08, US-09, US-10 → US-04:** Additional checks extend the same proofreading pipeline; the core pipeline (US-04) must work first.

    **Dependency Graph (Build Order):**

    ```
    Phase 1: US-16 (MCP Server) → US-01 (Document Ingestion)
    Phase 2: US-02, US-03 (Formatting Preservation)
    Phase 3: US-04, US-05 (Core Proofreading)
    Phase 4: US-11, US-12 (Track Changes & Comments Output)
    Phase 5: US-13, US-17 (Automatic Mode & Error Handling) → MVP Complete
    Phase 6: US-06, US-08, US-09, US-10 (Extended Checks)
    Phase 7: US-14 (Interactive Mode)
    Phase 8: US-07, US-15 (Bible Validation, Selective Checks)
    ```

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority | Phase |
| :-- | :--- | :--- | :--- | :--- |
| PBI-01 | Epic 5 | US-16: MCP Server scaffold & Langdock registration | Must | 1 |
| PBI-02 | Epic 1 | US-01: Document ingestion (`extract_document` tool) | Must | 1 |
| PBI-03 | Epic 1 | US-02: Formatting preservation (read & roundtrip) | Must | 2 |
| PBI-04 | Epic 1 | US-03: Red-text / placeholder detection & preservation | Must | 2 |
| PBI-05 | Epic 2 | US-04: Spelling & grammar check (`proofread_text` tool) | Must | 3 |
| PBI-06 | Epic 2 | US-05: Punctuation check (integrated into `proofread_text`) | Must | 3 |
| PBI-07 | Epic 3 | US-11: Track Changes output (`write_corrected_docx` tool) | Must | 4 |
| PBI-08 | Epic 3 | US-12: Comment insertion (integrated into `write_corrected_docx`) | Must | 4 |
| PBI-09 | Epic 4 | US-13: Automatic mode (Stage 1 end-to-end) | Must | 5 |
| PBI-10 | Epic 5 | US-17: Error handling (malformed files, API failures, timeouts) | Must | 5 |
| PBI-11 | Epic 2 | US-06: Typography check | Should | 6 |
| PBI-12 | Epic 2 | US-08: Quotation mark verification | Should | 6 |
| PBI-13 | Epic 2 | US-09: Form-of-address consistency | Should | 6 |
| PBI-14 | Epic 2 | US-10: Commonly confused words scan | Should | 6 |
| PBI-15 | Epic 4 | US-14: Interactive review mode (Stage 2) | Should | 7 |
| PBI-16 | Epic 2 | US-07: Bible reference validation (`validate_bible_refs` tool) | Could | 8 |
| PBI-17 | Epic 4 | US-15: Selective check requests | Could | 8 |
| PBI-18 | — | Agent system prompt: design & testing | Must | 5 |
| PBI-19 | — | Confused-words configuration file (YAML/JSON) | Should | 6 |
| PBI-20 | — | Typography rules configuration file (YAML/JSON) | Should | 6 |

---

### 5. Definition of Done (DoD)

A Product Backlog Item (e.g., a User Story or a Task) is considered "Done" when all of the following criteria are met:

*   **Code Quality:** The code is written and formatted according to the guidelines in `docs/CODING_STYLE.md` (`black .`, `ruff check .`).
*   **Tests:**
    *   All new backend functions are covered by unit tests.
    *   The end-to-end functionality is verified by an integration test.
    *   All existing tests continue to pass (no regressions).
    *   For document-manipulation functions: a roundtrip test confirms that an unmodified document is byte-identical (or structurally equivalent) after read → write.
    *   For proofreading functions: test cases with known errors verify detection accuracy.
*   **Acceptance Criteria:** All acceptance criteria defined for the story have been met and manually verified.
*   **Track Changes Verification:** For output-related stories, the generated `.docx` has been opened and verified in Microsoft Word and LibreOffice Writer.
*   **Code Review:** The code has been reviewed by at least one other team member (or is in a reviewable state in a pull request).
*   **Merge:** The code has been successfully merged into the main development branch (e.g., `main` or `develop`).
*   **Documentation:** Necessary changes to technical documentation (e.g., new ADRs, README updates, configuration docs) have been made.
*   **Configuration:** Any new configurable parameters (word lists, rules) are documented in the configuration reference.
