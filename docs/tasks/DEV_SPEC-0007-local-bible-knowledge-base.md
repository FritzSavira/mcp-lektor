# Requirements Analysis & Specification: Local Bible Knowledge Base

This document details the requirements for implementing a local Bible knowledge base for validation and rich citations, as described in **ADR-0007**.

---

### 1. Detailed Requirements Specification

The system must transition from fragile external web scraping to a robust, local-first Bible processing architecture. This involves:

#### 1.1. Data Ingestion & Storage
- **Local Storage**: The system shall store Bible translations in a structured JSON format within the `data/bibles/` directory.
- **Translations**: The primary translations to be stored locally are:
    - **Menge-Bibel (1939)** (Used as the structural master for validation)
    - **NeÜ (Neue evangelistische Übersetzung)**
    - **Elberfelder (1905)**
    - **Luther (1912)**
- **Schema**: The JSON structure must allow efficient lookup: `Book -> Chapter -> Verse -> Text`.

#### 1.2. BibleProvider Service
- **Memory Management**: The service shall load the configured JSON files into memory during application startup to ensure sub-millisecond response times.
- **Normalization**: The service must handle various German book name variants and abbreviations (e.g., "1. Mose", "Genesis", "Gen") and map them to standard internal IDs.
- **Validation Logic**: A reference is valid if the book, chapter, and verse(s) exist in the local master dataset (Menge).
- **Text Retrieval**: The service must provide a method to retrieve the text of a specific verse (or range) from all available local translations.

#### 1.3. Workflow Integration
- **Rich ProposedCorrection**: Every detected Bible reference shall result in a `ProposedCorrection` of category `BIBLE_REFERENCE`.
- **Explanation Formatting**: The `explanation` field must contain:
    - Status (Verified or Error).
    - The actual text from the local translations (Menge, NeÜ, etc.), clearly labeled.
    - Deep-links to `bibleserver.com` for modern translations (Luther 1984, current Elberfelder).
- **Comment-Only Mode**: Bible references shall not change the document text automatically but provide the rich information as a Word comment.

---

### 2. User Stories & Acceptance Criteria

**Epic: Enhanced Bible Reference Proofreading**

*   **User Story 1: Direct Bible Citation in Word**
    *   **As a user,** I want to see the actual text of a Bible reference in the Word comments, **so that** I don't have to look it up manually on a website.
    *   **Acceptance Criteria:**
        *   Word comments for Bible references contain the text of at least the Menge and NeÜ translations.
        *   The text is correctly attributed to the translation name.
        *   Formatting inside the comment is readable (newlines between translations).

*   **User Story 2: Offline Validation**
    *   **As a user,** I want the Bible validation to work even when I have no internet connection, **so that** my proofreading workflow is never interrupted.
    *   **Acceptance Criteria:**
        *   Validation against Menge, Elberfelder 1905, and Luther 1912 works without any network requests.
        *   Incorrect chapters or verses are identified correctly (e.g., "Genesis 60").
        *   The processing speed is significantly faster compared to the previous API-based approach.

*   **User Story 3: Mixed Local/Online Reference Links**
    *   **As a user,** I want to have links to modern translations (like Luther 1984) alongside the local texts, **so that** I can still perform manual comparisons with copyright-protected versions.
    *   **Acceptance Criteria:**
        *   The comment contains functional links to `bibleserver.com` for Luther 1984 and the current Elberfelder.
        *   These links are generated correctly based on the extracted reference.

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   Integration of **Menge-Bibel** as local JSON.
        *   New `BibleProvider` service with local lookup.
        *   Conversion of Bible results to rich `ProposedCorrection` with text.
        *   Basic book name normalization.
    *   **Should-Have:**
        *   Integration of **NeÜ**, **Elberfelder 1905**, and **Luther 1912**.
        *   Handling of verse ranges (e.g., "Gen 1,1-5").
    *   **Could-Have:**
        *   Data acquisition script to automatically fetch/convert JSONs from public repositories.
        *   Caching mechanism for the memory-loaded bibles.
    *   **Won't-Have (in this increment):**
        *   Validation against Apocryphal books (unless included in Zefania PD modules).

*   **Dependencies:**
    1.  **Topic: Data Acquisition**: We need the actual JSON files before the `BibleProvider` can be fully implemented.
    2.  **Topic: BibleReference Model**: Must support offsets (implemented in previous task) to anchor the rich comments correctly.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| T7.1 | Infrastructure | Set up `data/bibles/` directory and acquire JSON files. | Must |
| T7.2 | Logic | Implement `BibleProvider` with local loading and lookup. | Must |
| T7.3 | Integration | Update `ProofreadingEngine` to use `BibleProvider` for rich explanations. | Must |
| T7.4 | Logic | Add support for NeÜ and other translations in citation loop. | Should |
| T7.5 | Verification | Create integration tests for local validation and citation. | Must |

---

### 5. Definition of Done (DoD)

A Product Backlog Item (e.g., a User Story or a Task) is considered "Done" when all of the following criteria are met:

*   **Code Quality:** The code is written and formatted according to the guidelines in `docs/CODING_STYLE.md` (`black .`, `ruff check .`).
*   **Tests:**
    *   All new backend functions are covered by unit tests.
    *   The end-to-end functionality is verified by an integration test (simulating Word comment generation).
    *   All existing tests continue to pass (no regressions).
*   **Acceptance Criteria:** All acceptance criteria defined for the story have been met and verified.
*   **Documentation:** `CHANGELOG.md` is updated and references ADR-0007.
