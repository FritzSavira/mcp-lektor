# DEV_TASKS-0007: Local Bible Knowledge Base

Implement a local-first Bible knowledge base for robust validation and rich citations in Word comments, replacing the previous scraping approach.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0007: Local Bible Knowledge Base](../../docs/adr/ADR-0007-local-bible-knowledge-base.md)
*   [DEV_SPEC-0007: Requirements Analysis](../../docs/tasks/DEV_SPEC-0007-local-bible-knowledge-base.md)
*   [DEV_TECH_DESIGN-0007: Technical Specification](../../docs/tasks/DEV_TECH_DESIGN-0007-local-bible-knowledge-base.md)

---

## Phase 1: Foundation & Sample Data
*Goal: Set up the local storage structure and create test data.*

- [x] **Step 1.1: Create Directory Structure**
    - [x] **Action:** Create the directory `data/bibles/` in the project root.
    - [x] **Action:** Add an empty `data/bibles/.gitkeep` file.
    - [x] **Verification:** Run `ls data/bibles/` (or `dir data/bibles/` on Windows) and report if it exists.

- [x] **Step 1.2: Create Mock Master Data (Menge)**
    - [x] **Action:** Create `data/bibles/menge.json` with basic content.
    - [x] **Verification:** Confirm the file is readable and contains valid JSON.

- [x] **Step 1.3: Create Mock Secondary Data (NeÜ)**
    - [x] **Action:** Create `data/bibles/neu.json`.
    - [x] **Verification:** Confirm both files exist in `data/bibles/`.

---

## Phase 2: BibleProvider Implementation
*Goal: Create the core service for local Bible access.*

- [x] **Step 2.1: Scaffold `bible_provider.py`**
    - [x] **Action:** Create `src/mcp_lektor/core/bible_provider.py`.
    - [x] **Action:** Implement basic structure and `normalize_book_name`.
    - [x] **Verification (Interactive Test):** "1. Mose" -> "GEN".

- [x] **Step 2.3: Implement Loading & Existence Check**
    - [x] **Action:** Implement `load_all()` and `exists(book, chapter, verse)`.
    - [x] **Verification (Interactive Test):** `exists('GEN', 1, 1)` -> True.

- [x] **Step 2.4: Implement Text Retrieval**
    - [x] **Action:** Implement `get_texts(book, chapter, verse_start, verse_end=None)`.
    - [x] **Verification:** Test with GEN 1:1 and confirm it returns both Menge and NeÜ texts.

---

## Phase 3: Workflow Integration
*Goal: Update the Engine to use local data for rich explanations.*

- [x] **Step 3.1: Update `BibleValidator`**
    - [x] **Action:** Refactor to use `BibleProvider`.
    - [x] **Action:** Remove `httpx` dependency from this module.
    - [x] **Verification:** Unit tests for extraction still pass.

- [x] **Step 3.2: Update `ProofreadingEngine` Explanation**
    - [x] **Action:** In `_convert_bible_results_to_corrections`, integrate the multi-translation text retrieval.
    - [x] **Action:** Format the `explanation` with citations and links.
    - [x] **Verification:** Check a sample `ProposedCorrection` for rich text content.

---

## Phase 4: Finalization
*Goal: Cleanup and real data preparation.*

- [x] **Step 4.1: Update Configuration**
    - [x] **Action:** Cleanup `config.yaml` and `models.py`.
    - [x] **Verification:** App starts without errors.

- [x] **Step 4.2: Full Verification**
    - [x] **Action:** Run `pytest`.
    - [x] **Verification:** All tests (unit + integration) pass.

---

## Phase 5: UI & Infrastructure Refinement
*Goal: Improve usability, formatting, and Docker stability.*

- [x] **Step 5.1: Fix GUI & Docker Integration**
    - [x] **Action:** Remove obsolete parameters from `gui.py`.
    - [x] **Action:** Update `docker-compose.yaml` to mount `data/` volume.
    - [x] **Verification:** GUI starts in Docker and loads Bible data correctly.

- [x] **Step 5.2: Enhanced Comment Formatting**
    - [x] **Action:** Update `OpenXMLWriter` to support bold text (`**...**`) and line breaks (`\n`).
    - [x] **Action:** Update `ProofreadingEngine` to generate structured, bolded Bible citations.
    - [x] **Verification:** Word comments show bold labels and distinct lines for translations.

- [x] **Step 5.3: Robust Reference Detection**
    - [x] **Action:** Improve `BibleProvider.normalize_book_name` for better tolerance (spaces, dots).
    - [x] **Action:** Add missing variants (singular "Psalm", "1. Chronik") to regex and mappings.
    - [x] **Verification:** Test document with all books and singular forms is processed correctly.

- [x] **Step 5.4: Configuration Options**
    - [x] **Action:** Implement `enable_bible_links` toggle in `config.yaml`.
    - [x] **Verification:** Setting to `false` removes external links from comments.
