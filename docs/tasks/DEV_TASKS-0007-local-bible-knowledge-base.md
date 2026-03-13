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

- [ ] **Step 1.1: Create Directory Structure**
    - [ ] **Action:** Create the directory `data/bibles/` in the project root.
    - [ ] **Action:** Add an empty `data/bibles/.gitkeep` file.
    - [ ] **Verification:** Run `ls data/bibles/` (or `dir data/bibles/` on Windows) and report if it exists.

- [ ] **Step 1.2: Create Mock Master Data (Menge)**
    - [ ] **Action:** Create `data/bibles/menge.json` with basic content:
      ```json
      {
        "GEN": {
          "1": {
            "1": "Am Anfang schuf Gott den Himmel und die Erde.",
            "2": "Und die Erde war wüst und leer."
          }
        }
      }
      ```
    - [ ] **Verification:** Confirm the file is readable and contains valid JSON.

- [ ] **Step 1.3: Create Mock Secondary Data (NeÜ)**
    - [ ] **Action:** Create `data/bibles/neu.json`:
      ```json
      {
        "GEN": {
          "1": {
            "1": "Im Anfang schuf Gott Himmel und Erde.",
            "2": "Die Erde aber war wüst und öde."
          }
        }
      }
      ```
    - [ ] **Verification:** Confirm both files exist in `data/bibles/`.

---

## Phase 2: BibleProvider Implementation
*Goal: Create the core service for local Bible access.*

- [ ] **Step 2.1: Scaffold `bible_provider.py`**
    - [ ] **Action:** Create `src/mcp_lektor/core/bible_provider.py`.
    - [ ] **Action:** Implement basic structure and `normalize_book_name`.
    - [ ] **Verification (Interactive Test):** 
        1. Run `python -c "from mcp_lektor.core.bible_provider import BibleProvider; p = BibleProvider(); print(p.normalize_book_name('1. Mose'))"`.
        2. **Expected Result:** "GEN".

- [ ] **Step 2.3: Implement Loading & Existence Check**
    - [ ] **Action:** Implement `load_all()` and `exists(book, chapter, verse)`.
    - [ ] **Verification (Interactive Test):**
        1. Initialize provider, call `load_all()`.
        2. Call `exists('GEN', 1, 1)`.
        3. **Expected Result:** True.

- [ ] **Step 2.4: Implement Text Retrieval**
    - [ ] **Action:** Implement `get_texts(book, chapter, verse_start, verse_end=None)`.
    - [ ] **Verification:** Test with GEN 1:1 and confirm it returns both Menge and NeÜ texts.

---

## Phase 3: Workflow Integration
*Goal: Update the Engine to use local data for rich explanations.*

- [ ] **Step 3.1: Update `BibleValidator`**
    - [ ] **Action:** Refactor to use `BibleProvider`.
    - [ ] **Action:** Remove `httpx` dependency from this module.
    - [ ] **Verification:** Unit tests for extraction still pass.

- [ ] **Step 3.2: Update `ProofreadingEngine` Explanation**
    - [ ] **Action:** In `_convert_bible_results_to_corrections`, integrate the multi-translation text retrieval.
    - [ ] **Action:** Format the `explanation` with citations and links.
    - [ ] **Verification:** Check a sample `ProposedCorrection` for rich text content.

---

## Phase 4: Finalization
*Goal: Cleanup and real data preparation.*

- [ ] **Step 4.1: Update Configuration**
    - [ ] **Action:** Cleanup `config.yaml` and `models.py`.
    - [ ] **Verification:** App starts without errors.

- [ ] **Step 4.2: Full Verification**
    - [ ] **Action:** Run `pytest`.
    - [ ] **Verification:** All tests (unit + integration) must pass.
