# DEV_TASKS-0001: MCP-Based Interactive Proofreading Server

**Version:** 1.0
**Date:** 2026-03-04
**Author:** Opus
**Related Documents:**
- [ADR-0001](docs/adr/ADR-0001-mcp-based-interactive-proofreading-server.md)
- [DEV_SPEC-0001](docs/tasks/DEV_SPEC-0001-mcp-based-interactive-proofreading-server.md)
- [DEV_TECH_DESIGN-0001](docs/tasks/DEV_TECH_DESIGN-0001-mcp-based-interactive-proofreading-server.md)
- [CODING_STYLE](CODING_STYLE.md)

---

## How to Use This Task List

- Work through phases **in order**. Each phase builds on the previous one.
- Each task has a **checkbox** `[ ]`. Mark it `[x]` when complete.
- Tasks marked with **INTERACTIVE TEST** require you to perform a manual action and verify the result before proceeding.
- Tasks marked with **CHECKPOINT** are verification gates — do not skip them.
- You can stop after any **completed phase**. The codebase will be in a stable, testable state.
- All code must comply with [CODING_STYLE.md](CODING_STYLE.md): English code/comments, `black` formatting, `ruff` linting, meaningful names, type hints, docstrings, <20-line functions.

---

## Phase Overview

| Phase | Title | Goal | Estimated Effort |
|-------|-------|------|-----------------|
| 0 | Project Scaffolding | Runnable project skeleton with CI tooling | 1-2 hours |
| 1 | Data Models | All Pydantic models passing unit tests | 2-3 hours |
| 2 | Document Ingestion | extract_document tool reads .docx with formatting | 3-4 hours |
| 3 | Rule-Based Checks | Typography, quotation marks, confused words | 3-4 hours |
| 4 | LLM-Based Proofreading | proofread_text tool with batched LLM calls | 4-5 hours |
| 5 | Bible Reference Validation | validate_bible_refs tool with API integration | 2-3 hours |
| 6 | OpenXML Track Changes & Comments | write_corrected_docx tool produces valid .docx | 5-6 hours |
| 7 | Session Management & Server Assembly | Full MCP server with all 4 tools | 2-3 hours |
| 8 | End-to-End Integration Tests | Complete pipeline tests with real documents | 3-4 hours |
| 9 | Langdock Agent System Prompt | Agent configuration and conversational flow | 1-2 hours |
| 10 | Dockerization & Deployment | Container build, compose, deployment docs | 1-2 hours |

**Total estimated effort: 27-38 hours**

---

## Phase 0: Project Scaffolding

**Goal:** A clean, runnable Python project with all tooling configured. No business logic yet.

**Prerequisites:** Python 3.12+, pip, git installed.

---

### Task 0.1: Initialize Git Repository and Project Structure

- [x] Create the project root directory `mcp-lektor/`
- [x] Run `git init` inside it
- [x] Create `.gitignore` with entries for: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, `.env`
- [x] Create the directory structure:

```bash
mkdir -p src/mcp_lektor/{tools,core,config,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p config
mkdir -p docs/{adr,tasks}
```

- [x] Create empty `__init__.py` files in every Python package:

```bash
touch src/mcp_lektor/__init__.py
touch src/mcp_lektor/tools/__init__.py
touch src/mcp_lektor/core/__init__.py
touch src/mcp_lektor/config/__init__.py
touch src/mcp_lektor/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

---

### Task 0.2: Create pyproject.toml

- [x] Create `pyproject.toml` with the following content:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mcp-lektor"
version = "0.1.0"
description = "MCP-based interactive proofreading server for German Word documents"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0",
    "python-docx>=1.1",
    "lxml>=5.0",
    "pydantic>=2.0",
    "httpx>=0.27",
    "openai>=1.0",
    "pyyaml>=6.0",
    "uvicorn>=0.30",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "black>=24.0",
    "ruff>=0.5",
]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

### Task 0.3: Set Up Virtual Environment and Install Dependencies

- [x] Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

- [x] Install the project in editable mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

---

### Task 0.4: Verify Tooling Works

- [ ] Create a minimal test file `tests/unit/test_smoke.py`:

```python
def test_project_imports():
    import mcp_lektor
    assert mcp_lektor is not None
```

- [ ] Run the verification commands:

```bash
pytest tests/unit/test_smoke.py -v
black --check src/ tests/
ruff check src/ tests/
```

#### INTERACTIVE TEST 0.4

> **Action:** Run the three commands above.
> **Expected result:**
> - pytest: 1 test passed
> - black: no reformatting needed
> - ruff: no errors
>
> **Report:** Paste the output. Do NOT proceed if any command fails.

---

### Task 0.5: Create Configuration Files

- [x] Create `config/config.yaml` with server, proofreading, session, and document settings (see DEV_TECH_DESIGN-0001 Section 8.2 for reference values)
- [x] Create `config/confused_words.yaml` with at least 8 German confused-word pairs (seid/seit, dass/das, wider/wieder, Weise/Waise, Saite/Seite, Lid/Lied, Lehre/Leere, mahlen/malen)
- [x] Create `config/typography_rules.yaml` with rules for: German quotation marks, en-dash vs hyphen, ellipsis character, double spaces

---

### Task 0.6: Create .env.example

- [ ] Create `.env.example` with: `LANGDOCK_API_KEY`, `BIBLE_API_URL`, `LOG_LEVEL`

---

### CHECKPOINT Phase 0

> **Verify before proceeding:**
> 1. `pytest tests/unit/test_smoke.py -v` passes
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. Directory structure matches DEV_TECH_DESIGN-0001 Section 2.3
> 5. All three YAML config files exist and are valid
> 6. `git add -A && git commit -m "Phase 0: Project scaffolding"`

---

## Phase 1: Data Models

**Goal:** All Pydantic models from DEV_TECH_DESIGN-0001 Section 3 implemented and covered by unit tests.

**Prerequisites:** Phase 0 complete.

---

### Task 1.1: Implement Core Data Models - Part A (Document Structure)

- [x] Create `src/mcp_lektor/core/models.py`
- [x] Implement these models exactly as specified in DEV_TECH_DESIGN-0001 Section 3.1:
  - `TextColor` with r, g, b fields (0-255) and `is_red` property
  - `RunFormatting` with bold, italic, underline, strike, font_name, font_size, color, highlight, style_name
  - `TextRun` with text, formatting, is_placeholder, `is_red_text` property
  - `ParagraphType` enum: HEADING, BODY, LIST_ITEM, TABLE_CELL, HEADER, FOOTER
  - `DocumentParagraph` with index, paragraph_type, style_name, heading_level, runs, is_placeholder_paragraph, `plain_text` and `proofreadable_text` properties
  - `DocumentStructure` with filename, paragraphs, total_paragraphs, total_words, placeholder_count, placeholder_locations

**Coding style reminders:** All docstrings in English. Type hints on every field. Use `Field(default_factory=...)` for mutable defaults.

---

### Task 1.2: Write Unit Tests for Document Structure Models

- [x] Create `tests/unit/test_models_document.py` with tests for:
  - `TextColor`: red detection for pure red, dark red, blue, black, boundary values, out-of-range rejection
  - `TextRun`: plain run, red text run, empty run
  - `DocumentParagraph`: plain_text concatenation, proofreadable_text excludes placeholders, empty paragraph
  - `DocumentStructure`: basic construction, default empty lists

- [x] Run: `pytest tests/unit/test_models_document.py -v`

#### INTERACTIVE TEST 1.2

> **Action:** Run `pytest tests/unit/test_models_document.py -v`
> **Expected:** All tests pass (at least 10 tests).
> **Report:** Paste the test output.

---

### Task 1.3: Implement Core Data Models - Part B (Proofreading Results)

- [x] Add to `src/mcp_lektor/core/models.py`:
  - `CorrectionCategory` enum with 8 values (Rechtschreibung, Grammatik, Zeichensetzung, Typografie, Anfuehrungszeichen, Anrede-Konsistenz, Verwechslungswort, Bibelstelle)
  - `ConfidenceLevel` enum: HIGH, MEDIUM, LOW
  - `ProposedCorrection` with id, paragraph_index, run_index, char_offset_start/end, original_text, suggested_text, category, confidence, explanation, rule_reference
  - `ProofreadingResult` with document_filename, total_corrections, corrections, predominant_address_form, address_form_deviations, placeholder_summary, processing_time_seconds, plus `high_confidence`/`medium_confidence`/`low_confidence` properties

---

### Task 1.4: Write Unit Tests for Proofreading Result Models

- [x] Create `tests/unit/test_models_proofreading.py` with tests for:
  - `ProposedCorrection`: basic creation, optional rule_reference
  - `ProofreadingResult`: confidence-level filtering, empty result defaults

- [x] Run: `pytest tests/unit/test_models_proofreading.py -v`

#### INTERACTIVE TEST 1.4

> **Action:** Run `pytest tests/unit/test_models_proofreading.py -v`
> **Expected:** All tests pass.

---

### Task 1.5: Implement Core Data Models - Part C (Bible, Decisions, Config)

- [x] Add to `src/mcp_lektor/core/models.py`:
  - `BibleReference` with paragraph_index, raw_text, book, chapter, verse_start, verse_end
  - `BibleValidationResult` with reference, is_valid, error_message, suggested_correction, source_url
  - `CorrectionDecision` enum: ACCEPT, REJECT, EDIT
  - `UserDecision` with correction_id, decision, edited_text
  - `WriteRequest` with document_session_id, decisions list, apply_all flag

- [x] Create `src/mcp_lektor/config/settings.py` with:
  - `ProofreadingConfig` model
  - `ConfusedWordEntry` model
  - `TypographyRule` model

---

### Task 1.6: Write Unit Tests for Bible & Decision Models

- [x] Create `tests/unit/test_models_bible_decisions.py` with tests for:
  - `BibleReference`: basic reference, chapter-only reference
  - `BibleValidationResult`: valid and invalid results
  - `UserDecision`: accept, edit with custom text
  - `WriteRequest`: apply_all flag, empty decisions

- [x] Run: `pytest tests/unit/ -v`

#### INTERACTIVE TEST 1.6

> **Action:** Run `pytest tests/unit/ -v`
> **Expected:** All tests pass (at least 20 total).

---

### Task 1.7: Configuration Loader

- [x] Implement in `src/mcp_lektor/config/settings.py`:
  - `load_config()` function that reads `config/config.yaml` and returns `ProofreadingConfig`
  - `load_confused_words()` function that reads `config/confused_words.yaml` and returns `list[ConfusedWordEntry]`
  - `load_typography_rules()` function that reads `config/typography_rules.yaml` and returns `list[TypographyRule]`
  - Use `os.environ.get("LANGDOCK_API_KEY", "")` for the API key

- [x] Create `tests/unit/test_config_loader.py` with tests verifying all three loaders return correct data from the YAML files

#### INTERACTIVE TEST 1.7

> **Action:** Run `pytest tests/unit/test_config_loader.py -v`
> **Expected:** 3 tests pass.

---

### CHECKPOINT Phase 1

> **Verify before proceeding:**
> 1. `pytest tests/unit/ -v` passes all tests (23+)
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. All models serialize correctly with `.model_dump()` / `.model_validate()`
> 5. `git add -A && git commit -m "Phase 1: Data models complete"`

---

## Phase 2: Document Ingestion

**Goal:** The `extract_document` tool reads .docx files, extracts text with full formatting metadata, and correctly identifies red-text placeholders.

**Prerequisites:** Phase 1 complete.

---

### Task 2.1: Create Test Fixture Documents

- [x] Create a Python script `tests/fixtures/create_test_docs.py` that programmatically generates three test .docx files using `python-docx`:

**File 1: `sample_formatted.docx`**
- Heading 1: "Test Document"
- Normal paragraph with bold, italic, underlined text
- A bullet list with 3 items
- A paragraph with mixed font sizes

**File 2: `sample_with_errors.docx`**
- Paragraph with German spelling errors: "Der Hund leuft uber die Strasse."
- Paragraph with wrong quotation marks: '"Hallo" sagte er.'
- Paragraph with hyphen instead of en-dash: "Berlin - Hamburg"
- Paragraph with confused word: "Seid wann bist du hier?"
- Paragraph with address form mix: "Du kannst das Formular ausfuellen. Bitte senden Sie es zurueck."

**File 3: `sample_with_placeholders.docx`**
- Normal paragraph: "Dies ist ein normaler Text."
- Red-colored paragraph: "[Bild: Logo einfuegen]"
- Mixed paragraph: normal text + red text run + normal text
- Normal paragraph with Bible reference: "Siehe Mt 5,3-12 und Ps 23."

- [x] Run the script to generate the files: `python tests/fixtures/create_test_docs.py`

#### INTERACTIVE TEST 2.1

> **Action:** Open each generated .docx file in Word/LibreOffice.
> **Verify:**
> - `sample_formatted.docx`: Heading, bold/italic text visible
> - `sample_with_errors.docx`: Text with deliberate errors present
> - `sample_with_placeholders.docx`: Red text is visibly red, Bible reference present
>
> **Report:** Confirm each file opens correctly and contains the expected content.

---

### Task 2.2: Implement document_io - Run Formatting Extraction

- [x] Create `src/mcp_lektor/core/document_io.py`
- [x] Implement `extract_run_formatting(run) -> RunFormatting`:
  - Reads bold, italic, underline, strikethrough from the run
  - Reads font name and font size
  - Reads text color as RGB (handling the `python-docx` `RGBColor` type)
  - Reads highlight color
  - Reads character style name
  - Returns a `RunFormatting` model instance
- [x] Implement `is_placeholder(run_text: str, formatting: RunFormatting) -> bool`:
  - Returns True if color is red (via `TextColor.is_red`)
  - Returns True if text is wrapped in `[...]` AND color is red
  - Returns False otherwise

**Coding style:** Each function < 20 lines. Use early returns. Add docstrings.

---

### Task 2.3: Write Unit Tests for Formatting Extraction

- [x] Create `tests/unit/test_document_io.py` with tests using the `sample_formatted.docx` and `sample_with_placeholders.docx` fixtures
- [x] Test cases:
  - Extract bold run -> formatting.bold is True
  - Extract italic run -> formatting.italic is True
  - Extract red color run -> formatting.color.is_red is True
  - Extract normal run -> is_placeholder returns False
  - Extract red text run -> is_placeholder returns True

#### INTERACTIVE TEST 2.3

> **Action:** Run `pytest tests/unit/test_document_io.py -v`
> **Expected:** All tests pass (at least 5 tests).

---

### Task 2.4: Implement document_io - Full Document Parsing

- [x] Implement `parse_document(file_path: str) -> DocumentStructure`:
  - Opens the .docx file with `python-docx`
  - Iterates over all paragraphs
  - Classifies each paragraph type (heading, body, list_item) based on style name
  - For headings, extracts the heading level (1-6)
  - For each run in each paragraph, calls `extract_run_formatting()` and `is_placeholder()`
  - Determines `is_placeholder_paragraph` (True if ALL non-whitespace runs are placeholders)
  - Counts total words (from non-placeholder text)
  - Returns a complete `DocumentStructure`

- [x] Implement `classify_paragraph(paragraph) -> ParagraphType`:
  - "Heading 1" through "Heading 9" -> HEADING
  - "List Paragraph", "List Bullet", "List Number" -> LIST_ITEM
  - Everything else -> BODY

- [x] Implement `get_heading_level(paragraph) -> int | None`:
  - Extracts the numeric level from heading style names
  - Returns None for non-heading paragraphs

---

### Task 2.5: Write Unit Tests for Full Document Parsing

- [x] Add tests to `tests/unit/test_document_io.py`:
  - Parse `sample_formatted.docx`: correct paragraph count, heading detected, body paragraphs present
  - Parse `sample_with_placeholders.docx`: placeholder paragraph detected, mixed paragraph has both placeholder and non-placeholder runs, word count excludes placeholder text
  - Parse `sample_with_errors.docx`: all text extracted correctly, no paragraphs wrongly marked as placeholder

#### INTERACTIVE TEST 2.5

> **Action:** Run `pytest tests/unit/test_document_io.py -v`
> **Expected:** All tests pass (at least 10 tests).

---

### Task 2.6: Implement the extract_document MCP Tool

- [x] Create `src/mcp_lektor/tools/extract_document.py`
- [x] Implement the `extract_document(file_path: str) -> str` async function:
  - Validates that `file_path` ends with `.docx`
  - Validates that the file exists and is <= 50 MB
  - Calls `parse_document()` from `document_io`
  - Generates a UUID4 session ID
  - Stores the session data (file_path, structure) in the session store
  - Returns a JSON string containing `session_id` and the `DocumentStructure`
  - Raises clear error messages for invalid inputs

- [x] Use the in-memory `SESSION_STORE` dict (will be formalized in Phase 7)

---

### Task 2.7: Write Integration Test for extract_document Tool

- [x] Create `tests/integration/test_extract_document.py`:
  - Test with `sample_formatted.docx`: returns valid JSON, contains session_id, paragraph count matches
  - Test with `sample_with_placeholders.docx`: placeholders detected, placeholder_count > 0
  - Test with non-existent file: raises appropriate error
  - Test with non-.docx file: raises appropriate error

#### INTERACTIVE TEST 2.7

> **Action:** Run `pytest tests/integration/test_extract_document.py -v`
> **Expected:** All tests pass (at least 4 tests).

---

### CHECKPOINT Phase 2

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes all tests
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. Manually run `extract_document` on each fixture file and verify the JSON output is sensible
> 5. `git add -A && git commit -m "Phase 2: Document ingestion complete"`

---

## Phase 3: Rule-Based Checks

**Goal:** Typography rules, quotation mark detection, and confused-word scanning work without LLM calls.

**Prerequisites:** Phase 2 complete.

---

### Task 3.1: Implement Typography Rule Scanner

- [x] Create `src/mcp_lektor/core/proofreading_engine.py` (initial version)
- [x] Implement `apply_typography_rules(structure: DocumentStructure, rules: list[TypographyRule]) -> list[ProposedCorrection]`:
  - Iterates over non-placeholder paragraphs
  - For each run, applies each typography rule regex
  - For each match, creates a `ProposedCorrection` with category=TYPOGRAPHY, confidence=HIGH
  - Returns the list of corrections

**Important:** Only scan `proofreadable_text`. Never modify placeholder runs.

---

### Task 3.2: Write Unit Tests for Typography Scanner

- [x] Create `tests/unit/test_typography_scanner.py`:
  - Test straight double quotes detection: `"Hallo"` -> suggests `„Hallo“`
  - Test hyphen-as-dash detection: `"A - B"` -> suggests `"A – B"`
  - Test triple-dot detection: `"Hmm..."` -> suggests `"Hmm…"`
  - Test double-space detection: `"A  B"` -> suggests `"A B"`
  - Test clean text produces no corrections
  - Test placeholder text is skipped

#### INTERACTIVE TEST 3.2

> **Action:** Run `pytest tests/unit/test_typography_scanner.py -v`
> **Expected:** All tests pass (at least 6 tests).

---

### Task 3.3: Implement Quotation Mark Checker

- [x] Implement `check_quotation_marks(structure: DocumentStructure) -> list[ProposedCorrection]`:
  - Detects straight single and double quotes in non-placeholder text
  - Proposes German typographic replacements
  - Checks for unbalanced quotation marks (odd number of quotes in a paragraph)
  - Category: QUOTATION_MARKS, Confidence: HIGH for straight quotes, MEDIUM for potentially unbalanced

---

### Task 3.4: Implement Confused Words Scanner

- [x] Implement `scan_confused_words(structure: DocumentStructure, words: list[ConfusedWordEntry]) -> list[ProposedCorrection]`:
  - For each confused word entry, searches non-placeholder text using word-boundary regex
  - Creates a correction with category=CONFUSED_WORD, confidence=LOW (context-dependent)
  - Includes the explanation from the confused-word entry

**Important:** These are LOW confidence because they require human judgment. The scanner flags potential issues, not definitive errors.

---

### Task 3.5: Write Unit Tests for Quotation Marks and Confused Words

- [x] Add tests to `tests/unit/test_quotation_marks.py`:
  - Straight double quotes detected
  - German quotes not flagged
  - Mixed quotes in one paragraph

- [x] Add tests to `tests/unit/test_confused_words.py`:
  - "seid" flagged when it might be "seit" (e.g., "Seid wann")
  - "dass" not flagged in correct usage
  - Placeholder text not scanned

#### INTERACTIVE TEST 3.5

> **Action:** Run `pytest tests/unit/test_quotation_marks.py tests/unit/test_confused_words.py -v`
> **Expected:** All tests pass.

---

### Task 3.6: Integration Test - Rule-Based Checks on Error Document

- [x] Create `tests/integration/test_rule_based_checks.py`:
  - Parse `sample_with_errors.docx`
  - Run all three rule-based scanners
  - Verify that typography issues are found (straight quotes, hyphen as dash)
  - Verify that confused word "Seid" is flagged
  - Verify that no corrections target placeholder text
  - Verify correction IDs are unique

#### INTERACTIVE TEST 3.6

> **Action:** Run `pytest tests/integration/test_rule_based_checks.py -v`
> **Expected:** All tests pass. Review the found corrections and verify they make sense.

---

### CHECKPOINT Phase 3

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes all tests
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. Rule-based checks correctly identify errors in `sample_with_errors.docx` without false positives on clean text
> 5. `git add -A && git commit -m "Phase 3: Rule-based checks complete"`

---

## Phase 4: LLM-Based Proofreading

**Goal:** The `proofread_text` tool sends document text to the Langdock API for spelling, grammar, punctuation, and address-form analysis.

**Prerequisites:** Phase 3 complete. `LANGDOCK_API_KEY` set in `.env`.

---

### Task 4.1: Implement LLM Client Wrapper

- [x] Add to `src/mcp_lektor/core/proofreading_engine.py`:
- [x] Implement `ProofreadingEngine` class with:
  - `__init__(self, config: ProofreadingConfig)`: initializes the AsyncOpenAI client with Langdock API base URL and key
  - Private method `_build_system_prompt(checks: list[CorrectionCategory]) -> str`: builds the proofreading system prompt with the enabled checks listed
  - Private method `_build_user_prompt(paragraphs: list[DocumentParagraph]) -> str`: formats the paragraphs as numbered text for the LLM, marking placeholder text as `[PLACEHOLDER - DO NOT MODIFY]`

---

### Task 4.2: Implement LLM Batch Processing

- [x] Implement `_proofread_batch(self, paragraphs: list[DocumentParagraph], checks: list[CorrectionCategory]) -> list[ProposedCorrection]`:
  - Calls the LLM API with the system and user prompts
  - Parses the JSON response into `ProposedCorrection` objects
  - Handles malformed LLM responses gracefully (log warning, skip unparseable corrections)
  - Sets appropriate timeout (60 seconds per batch)

- [x] Implement `_chunk_paragraphs(self, paragraphs: list[DocumentParagraph]) -> list[list[DocumentParagraph]]`:
  - Groups paragraphs into batches of ~2500 estimated tokens
  - Skips placeholder-only paragraphs
  - Skips empty paragraphs

- [x] Implement `proofread(self, structure: DocumentStructure, checks: list[CorrectionCategory]) -> ProofreadingResult`:
  - Runs rule-based checks first (typography, quotation marks, confused words)
  - Chunks non-placeholder paragraphs
  - Runs LLM batches (sequentially to respect rate limits)
  - Deduplicates corrections (same paragraph + overlapping offsets)
  - Assigns sequential IDs (C-001, C-002, ...)
  - Returns complete `ProofreadingResult`

---

### Task 4.3: Write Unit Tests with Mocked LLM

- [x] Create `tests/unit/test_proofreading_engine.py`:
  - Mock the AsyncOpenAI client to return predefined JSON responses
  - Test system prompt contains enabled check categories
  - Test user prompt formats paragraphs correctly
  - Test placeholder paragraphs are excluded from LLM input
  - Test chunking: 10 short paragraphs -> 1 batch; 50 long paragraphs -> multiple batches
  - Test deduplication: overlapping corrections merged
  - Test malformed LLM response handled without crash

#### INTERACTIVE TEST 4.3

> **Action:** Run `pytest tests/unit/test_proofreading_engine.py -v`
> **Expected:** All tests pass (at least 7 tests).

---

### Task 4.4: Implement the proofread_text MCP Tool

- [x] Create `src/mcp_lektor/tools/proofread_text.py`
- [x] Implement `proofread_text(session_id: str, checks: list[str] | None = None) -> str`:
  - Retrieves the session from `SESSION_STORE`
  - Validates session exists
  - Converts check strings to `CorrectionCategory` enums (defaults to all)
  - Creates `ProofreadingEngine` with loaded config
  - Calls `engine.proofread()`
  - Stores the result in the session
  - Returns JSON string of `ProofreadingResult`

---

### Task 4.5: Integration Test with Real LLM (Optional - requires API key)

- [x] Create `tests/integration/test_proofread_text.py`:
  - Mark tests with `@pytest.mark.skipif(not os.environ.get("LANGDOCK_API_KEY"), reason="No API key")`
  - Extract `sample_with_errors.docx`
  - Run `proofread_text` on the session
  - Verify that corrections are returned
  - Verify that "Hund leuft" is flagged as a spelling error
  - Verify that address form inconsistency is detected
  - Print the full correction list for manual review

#### INTERACTIVE TEST 4.5

> **Action:** Set `LANGDOCK_API_KEY` in your environment, then run `pytest tests/integration/test_proofread_text.py -v -s`
> **Expected:** Tests pass. Review printed corrections for accuracy.
> **If no API key:** Skip this test; it will be covered in Phase 8 end-to-end tests.

---

### CHECKPOINT Phase 4

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes all tests (mocked LLM tests always pass, real LLM tests may be skipped)
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. `git add -A && git commit -m "Phase 4: LLM-based proofreading complete"`

---

## Phase 5: Bible Reference Validation

**Goal:** Detect Bible references in document text and validate them against an online API.

**Prerequisites:** Phase 2 complete (document structure available).

---

### Task 5.1: Implement Bible Reference Pattern Matching

- [x] Create `src/mcp_lektor/utils/bible_patterns.py`
- [x] Define `BIBLE_REF_PATTERN` regex that matches German Bible reference formats:
  - Standard: `Mt 5,3` or `Mt 5,3-12`
  - With book number: `1. Mose 3,15` or `2. Kor 5,17`
  - Chapter only: `Ps 23`
  - With en-dash: `Joh 3,16-18`
  - All common German abbreviations (see DEV_TECH_DESIGN-0001 Section 4.2, Tool 3)

- [x] Implement `extract_bible_references(structure: DocumentStructure) -> list[BibleReference]`:
  - Scans non-placeholder paragraphs
  - Applies regex to find all matches
  - Returns list of `BibleReference` objects with book, chapter, verse_start, verse_end

---

### Task 5.2: Write Unit Tests for Bible Reference Extraction

- [x] Create `tests/unit/test_bible_patterns.py`:
  - "Mt 5,3" -> book=Mt, chapter=5, verse_start=3
  - "1. Mose 3,15" -> book=Mose (with prefix 1.), chapter=3, verse_start=15
  - "Ps 23" -> book=Ps, chapter=23, verse_start=None
  - "Joh 3,16-18" -> verse_start=16, verse_end=18
  - "Offb 21,1-4" -> correctly parsed
  - No match in normal German text without references
  - Placeholder paragraphs are skipped

#### INTERACTIVE TEST 5.2

> **Action:** Run `pytest tests/unit/test_bible_patterns.py -v`
> **Expected:** All tests pass (at least 7 tests).

---

### Task 5.3: Implement Bible API Validator

- [x] Create `src/mcp_lektor/core/bible_validator.py`
- [x] Implement `BibleValidator` class:
  - `__init__(self, api_base_url: str)`: stores the Bible API URL
  - `async validate_reference(self, ref: BibleReference) -> BibleValidationResult`: calls the API, checks if the reference exists, returns result with is_valid flag
  - `async validate_all(self, refs: list[BibleReference]) -> list[BibleValidationResult]`: validates all references concurrently with `asyncio.gather()`
  - Handle HTTP errors gracefully (timeout, 404, etc.)
  - Include the API URL as `source_url` in successful validations

---

### Task 5.4: Write Unit Tests for Bible Validator (Mocked API)

- [x] Create `tests/unit/test_bible_validator.py`:
  - Mock httpx responses
  - Valid reference returns is_valid=True
  - Invalid chapter returns is_valid=False with error message
  - API timeout handled gracefully (returns is_valid with error_message)
  - Concurrent validation of 3 references

#### INTERACTIVE TEST 5.4

> **Action:** Run `pytest tests/unit/test_bible_validator.py -v`
> **Expected:** All tests pass (at least 4 tests).

---

### Task 5.5: Implement the validate_bible_refs MCP Tool

- [x] Create `src/mcp_lektor/tools/validate_bible_refs.py`
- [x] Implement `validate_bible_refs(session_id: str) -> str`:
  - Retrieves the session
  - Extracts Bible references from the document structure
  - Validates them via the Bible API
  - For invalid references, creates `ProposedCorrection` entries with category=BIBLE_REFERENCE, confidence=LOW
  - Merges Bible corrections into the session's proofreading result (if exists)
  - Returns JSON string of validation results

---

### Task 5.6: Integration Test for Bible Validation

- [x] Create `tests/integration/test_bible_validation.py`:
  - Extract `sample_with_placeholders.docx` (contains "Mt 5,3-12" and "Ps 23")
  - Run `validate_bible_refs`
  - Verify that both references are detected
  - Verify that valid references return is_valid=True (if API is reachable)
  - Verify that results include source_url

#### INTERACTIVE TEST 5.6

> **Action:** Run `pytest tests/integration/test_bible_validation.py -v -s`
> **Expected:** Tests pass. Bible references detected and validated.

---

### CHECKPOINT Phase 5

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes all tests
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. `git add -A && git commit -m "Phase 5: Bible reference validation complete"`

---

## Phase 6: OpenXML Track Changes & Comments

**Goal:** The `write_corrected_docx` tool produces valid .docx files with Track Changes and comments. This is the most technically complex phase.

**Prerequisites:** Phase 2 complete (document_io). Phase 4 complete (proofreading results exist).

---

### Task 6.1: Implement Run Splitting for Track Changes

- [x] Create `src/mcp_lektor/core/openxml_writer.py`
- [x] Implement helper `make_run(text: str, rpr_element=None, is_delete: bool=False) -> lxml.etree.Element`:
  - Creates a `<w:r>` element with `<w:t>` (or `<w:delText>` for deletions)
  - Copies run properties (rpr) if provided
  - Sets `xml:space="preserve"` on the text element

- [x] Implement `apply_track_change(paragraph_element, run_index, char_start, char_end, original_text, replacement_text, author, timestamp, revision_id)`:
  - Splits the target run at char_start and char_end
  - Inserts before-text run (unchanged)
  - Inserts `<w:del>` element wrapping the original text
  - Inserts `<w:ins>` element wrapping the replacement text
  - Inserts after-text run (unchanged)
  - Preserves all original run formatting

**Reference:** DEV_TECH_DESIGN-0001 Section 4.2, Tool 4 for the exact XML structure.

---

### Task 6.2: Write Unit Tests for Track Changes XML

- [x] Create `tests/unit/test_openxml_writer.py`:
  - Test `make_run`: creates valid XML element with text
  - Test `make_run` with delete flag: uses `<w:delText>` instead of `<w:t>`
  - Test `make_run` with formatting: preserves bold/italic properties
  - Test `apply_track_change` on a simple run: produces correct `<w:del>` + `<w:ins>` structure
  - Test `apply_track_change` mid-word: splits before/after text correctly
  - Test `apply_track_change` at start of run: no before-text run created
  - Test `apply_track_change` at end of run: no after-text run created

#### INTERACTIVE TEST 6.2

> **Action:** Run `pytest tests/unit/test_openxml_writer.py -v`
> **Expected:** All tests pass (at least 7 tests).

---

### Task 6.3: Implement Comment Insertion

- [x] Add to `src/mcp_lektor/core/openxml_writer.py`:
- [x] Implement `get_or_create_comments_part(document) -> CommentsPart`:
  - Checks if the document already has a comments part
  - If not, creates one and adds the relationship

- [x] Implement `add_comment(document, paragraph_element, run_index, comment_text, author, timestamp, comment_id)`:
  - Inserts `<w:commentRangeStart>` before the target run
  - Inserts `<w:commentRangeEnd>` after the target run
  - Inserts `<w:r><w:commentReference>` after the range end
  - Adds the comment content to the comments part

---

### Task 6.4: Write Unit Tests for Comment Insertion

- [x] Add to `tests/unit/test_openxml_writer.py`:
  - Test comment insertion on a simple paragraph
  - Test comment has correct author and text
  - Test multiple comments on different runs in the same paragraph
  - Test that the comments.xml part is created if it does not exist

#### INTERACTIVE TEST 6.4

> **Action:** Run `pytest tests/unit/test_openxml_writer.py -v`
> **Expected:** All tests pass (at least 11 tests).

---

### Task 6.5: Implement the Document Writer (Applying Multiple Corrections)

- [x] Implement `write_corrections_to_docx(source_path: str, output_path: str, corrections: list[ProposedCorrection], author: str) -> str`:
  - Opens the source document
  - Sorts corrections by paragraph_index, then by char_offset_start (descending) to avoid offset shifting
  - For each correction:
    - Applies track change at the specified location
    - Adds a comment with the explanation
  - Saves the modified document to output_path
  - Returns output_path

**Critical implementation detail:** Apply corrections in reverse order (last offset first) within each paragraph to avoid offset invalidation.

---

### Task 6.6: Integration Test - Write Corrected Document

- [x] Create `tests/integration/test_write_corrected_docx.py`:
  - Create a test document with known errors
  - Create a list of `ProposedCorrection` objects targeting those errors
  - Call `write_corrections_to_docx`
  - Open the output file and verify:
    - File is a valid .docx (can be opened by python-docx)
    - Track changes are present in the XML (search for `<w:ins>` and `<w:del>`)
    - Comments are present (search for comment elements)
    - Original formatting is preserved on unchanged text

#### INTERACTIVE TEST 6.6a (Automated)

> **Action:** Run `pytest tests/integration/test_write_corrected_docx.py -v`
> **Expected:** All tests pass.

#### INTERACTIVE TEST 6.6b (Manual - Critical)

> **Action:** Open the generated output .docx file in Microsoft Word (or LibreOffice Writer).
> **Verify:**
> 1. Track Changes are visible (enable "All Markup" view)
> 2. Deleted text is shown with strikethrough
> 3. Inserted text is shown with underline or different color
> 4. Comments appear in the margin with the correct author name
> 5. Accepting all changes produces the corrected text
> 6. Original formatting (bold, italic, etc.) is preserved
>
> **Report:** Describe what you see. Take a screenshot if possible. This is the most critical manual test.

---

### Task 6.7: Implement the write_corrected_docx MCP Tool

- [x] Create `src/mcp_lektor/tools/write_corrected_docx.py`
- [x] Implement `write_corrected_docx(session_id: str, decisions: str) -> str`:
  - Retrieves the session
  - Parses the decisions JSON into `WriteRequest`
  - If `apply_all=True`: applies all corrections
  - If `apply_all=False`: filters corrections based on user decisions (ACCEPT, REJECT, EDIT)
  - For EDIT decisions: uses the user's edited_text instead of the suggested_text
  - Calls `write_corrections_to_docx` with the filtered corrections
  - Returns the path to the output file

---

### Task 6.8: Write Integration Test for write_corrected_docx Tool

- [x] Add to `tests/integration/test_write_corrected_docx.py`:
  - Test apply_all=True: all corrections applied
  - Test selective decisions: only accepted corrections applied, rejected ones skipped
  - Test edit decision: user's custom text used instead of suggestion
  - Test invalid session_id: clear error message

#### INTERACTIVE TEST 6.8

> **Action:** Run `pytest tests/integration/test_write_corrected_docx.py -v`
> **Expected:** All tests pass.

---

### CHECKPOINT Phase 6

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes all tests
> 2. `black --check src/ tests/` is clean
> 3. `ruff check src/ tests/` has no errors
> 4. Manually open at least one generated .docx in Word and verify Track Changes and comments look correct
> 5. `git add -A && git commit -m "Phase 6: OpenXML Track Changes & Comments complete"`

---

## Phase 7: Session Management & Server Assembly

**Goal:** All four MCP tools connected through a proper session manager, running as a complete MCP server.

**Prerequisites:** Phases 2-6 complete.

---

### Task 7.1: Formalize Session Manager

- [x] Create `src/mcp_lektor/core/session_manager.py`:
  - Implement `SessionManager` class with:
    - `create_session(file_path: str, structure: DocumentStructure) -> str`: creates session, returns ID
    - `get_session(session_id: str) -> dict`: retrieves session, raises `KeyError` if not found
    - `update_session(session_id: str, key: str, value: Any)`: updates session data
    - `delete_session(session_id: str)`: removes session and cleans up temp files
    - `cleanup_expired()`: removes sessions older than TTL
  - Use `datetime.utcnow()` for timestamps
  - TTL from config (default 30 minutes)

- [x] Update all four tools to use `SessionManager` instead of raw `SESSION_STORE` dict

---

### Task 7.2: Write Unit Tests for Session Manager

- [x] Create `tests/unit/test_session_manager.py`:
  - Create session -> returns UUID string
  - Get existing session -> returns data
  - Get non-existent session -> raises KeyError
  - Update session -> data persisted
  - Delete session -> no longer retrievable
  - Cleanup expired -> old sessions removed, fresh sessions kept

#### INTERACTIVE TEST 7.2

> **Action:** Run `pytest tests/unit/test_session_manager.py -v`
> **Expected:** All tests pass (at least 6 tests).

---

### Task 7.3: Assemble the MCP Server

- [ ] Create `src/mcp_lektor/server.py`:
  - Import FastMCP from `mcp.server.fastmcp`
  - Create the MCP server instance with name and description
  - Register all four tools
  - Start the session cleanup background task on server startup
  - Add error handling middleware / logging

```python
# Minimal structure (expand per DEV_TECH_DESIGN-0001 Section 4.1):
from mcp.server.fastmcp import FastMCP
from mcp_lektor.tools.extract_document import extract_document
from mcp_lektor.tools.proofread_text import proofread_text
from mcp_lektor.tools.validate_bible_refs import validate_bible_refs
from mcp_lektor.tools.write_corrected_docx import write_corrected_docx

mcp = FastMCP(
    "MCP Lektor",
    description="Professional German-language proofreading server"
)

mcp.tool()(extract_document)
mcp.tool()(proofread_text)
mcp.tool()(validate_bible_refs)
mcp.tool()(write_corrected_docx)

if __name__ == "__main__":
    mcp.run(transport="sse")
```

---

### Task 7.4: Server Smoke Test

- [ ] Start the server locally:

```bash
python -m mcp_lektor.server
```

- [ ] Verify server starts without errors
- [ ] Verify MCP tool discovery works (the server should log the registered tools)

#### INTERACTIVE TEST 7.4

> **Action:** Start the server and observe the console output.
> **Expected:**
> - No import errors
> - Server starts on port 8080 (or configured port)
> - Log shows 4 registered tools
>
> **Report:** Paste the startup log. Stop the server with Ctrl+C after verification.

---

### CHECKPOINT Phase 7

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes all tests
> 2. Server starts and stops cleanly
> 3. `black --check src/ tests/` is clean
> 4. `ruff check src/ tests/` has no errors
> 5. `git add -A && git commit -m "Phase 7: Session management & server assembly complete"`

---

## Phase 8: End-to-End Integration Tests

**Goal:** Complete pipeline tests from document upload to corrected .docx output.

**Prerequisites:** Phase 7 complete. `LANGDOCK_API_KEY` available.

---

### Task 8.1: Create Comprehensive Test Document

- [ ] Create `tests/fixtures/create_e2e_test_doc.py` that generates `tests/fixtures/e2e_test_document.docx`:
  - Heading 1: "Gemeindebrief Fruehjahr 2026"
  - Normal paragraph with correct German text (control — should produce no corrections)
  - Paragraph with spelling error: "Die Gemeinde feirt ein grosses Fest."
  - Paragraph with grammar error: "Der Kinder spielen im Garten."
  - Paragraph with wrong quotes: '"Kommt alle!" rief der Pfarrer.'
  - Paragraph with hyphen as dash: "Sonntag - ein Tag der Ruhe"
  - Paragraph with confused word: "Seid gestern regnet es."
  - Paragraph with address form Du: "Lieber Freund, Du bist eingeladen."
  - Paragraph with address form Sie: "Bitte melden Sie sich an."
  - Red placeholder: "[Bild: Gemeindezentrum einfuegen]"
  - Paragraph with Bible references: "Lies dazu Mt 5,1-12 und Ps 23."
  - Paragraph with invalid Bible reference: "Siehe Mt 99,1."

- [ ] Run the script to generate the file

#### INTERACTIVE TEST 8.1

> **Action:** Open `e2e_test_document.docx` in Word. Verify all content is present, red text is red, and formatting is correct.

---

### Task 8.2: End-to-End Test - Stage 1 (Automatic Mode)

- [ ] Create `tests/integration/test_end_to_end.py`:
- [ ] Test `test_e2e_stage1_automatic`:
  1. Call `extract_document` with the e2e test doc
  2. Verify session_id returned, placeholder detected
  3. Call `proofread_text` with session_id, all checks enabled
  4. Verify corrections found: spelling, grammar, typography, confused word, address form
  5. Verify placeholder paragraph NOT modified
  6. Call `validate_bible_refs` with session_id
  7. Verify "Mt 5,1-12" is valid, "Mt 99,1" is invalid
  8. Call `write_corrected_docx` with apply_all=True
  9. Verify output file exists and is valid .docx
  10. Open output with python-docx and verify Track Changes XML elements present

#### INTERACTIVE TEST 8.2a (Automated)

> **Action:** Run `pytest tests/integration/test_end_to_end.py::test_e2e_stage1_automatic -v -s`
> **Expected:** Test passes. Corrections printed to console for review.

#### INTERACTIVE TEST 8.2b (Manual - Critical)

> **Action:** Open the generated output .docx in Microsoft Word.
> **Verify:**
> 1. Track Changes show all corrections
> 2. Comments explain each correction
> 3. Red placeholder text `[Bild: Gemeindezentrum einfuegen]` is UNCHANGED
> 4. Accepting all changes produces correctly proofread text
> 5. Author is "MCP Lektor"
>
> **Report:** Describe what you see. This is the acceptance test for Stage 1.

---

### Task 8.3: End-to-End Test - Stage 2 (Interactive Mode Simulation)

- [ ] Add test `test_e2e_stage2_interactive` to `tests/integration/test_end_to_end.py`:
  1. Call `extract_document` + `proofread_text` (same as Stage 1)
  2. From the returned corrections, create decisions:
     - Accept all HIGH confidence corrections
     - Reject one MEDIUM confidence correction
     - Edit one LOW confidence correction with custom text
  3. Call `write_corrected_docx` with the decisions
  4. Verify output file: accepted changes are present as Track Changes, rejected ones are absent, edited one uses custom text

#### INTERACTIVE TEST 8.3

> **Action:** Run `pytest tests/integration/test_end_to_end.py::test_e2e_stage2_interactive -v -s`
> **Expected:** Test passes.

---

### Task 8.4: Edge Case Tests

- [ ] Add edge case tests to `tests/integration/test_end_to_end.py`:
  - `test_empty_document`: empty .docx produces 0 corrections
  - `test_all_placeholder_document`: document with only red text produces 0 corrections
  - `test_no_bible_references`: document without Bible refs returns empty list
  - `test_large_document`: generate a 50-paragraph document, verify processing completes without timeout (< 120 seconds)

#### INTERACTIVE TEST 8.4

> **Action:** Run `pytest tests/integration/test_end_to_end.py -v`
> **Expected:** All end-to-end tests pass.

---

### CHECKPOINT Phase 8

> **Verify before proceeding:**
> 1. `pytest tests/ -v` passes ALL tests
> 2. `pytest tests/ --cov=mcp_lektor --cov-report=term-missing` shows > 80% coverage
> 3. `black --check src/ tests/` is clean
> 4. `ruff check src/ tests/` has no errors
> 5. Manual verification of generated .docx files in Word completed
> 6. `git add -A && git commit -m "Phase 8: End-to-end integration tests complete"`

---

## Phase 9: Langdock Agent System Prompt

**Goal:** Create and document the Agent system prompt for the Langdock platform.

**Prerequisites:** Phase 7 complete (server running). Phase 8 recommended for confidence.

---

### Task 9.1: Write the Agent System Prompt

- [ ] Create `config/agent_system_prompt.md` with the full system prompt as specified in DEV_TECH_DESIGN-0001 Section 5.1
- [ ] The prompt must include:
  - Role definition (professional German Lektor)
  - Workflow steps (extract -> proofread -> validate bible -> write)
  - Mode detection rules (automatic vs. interactive vs. selective)
  - Result presentation format (tables grouped by confidence with colored indicators)
  - Decision parsing instructions (accept, reject, edit syntax)
  - Rules: never modify red text/placeholders, always respond in German

---

### Task 9.2: Write Agent Configuration Documentation

- [ ] Create `docs/agent-setup-guide.md` with step-by-step instructions:
  1. How to create the Agent in Langdock
  2. How to paste the system prompt
  3. How to attach the MCP integration
  4. How to test the Agent with a sample document
  5. Recommended Agent settings (model, temperature)

---

### Task 9.3: Test the Agent (Manual)

#### INTERACTIVE TEST 9.3

> **Action:** If you have access to a Langdock workspace:
> 1. Create a new Agent with the system prompt
> 2. Attach the MCP integration (pointing to your running server)
> 3. Upload `e2e_test_document.docx` and type "Lektoriere das komplett"
> 4. Verify the Agent calls the MCP tools in order
> 5. Verify you receive a corrected .docx download
>
> **If no Langdock access:** Skip this test. Document the expected behavior instead.

---

### CHECKPOINT Phase 9

> **Verify before proceeding:**
> 1. System prompt file exists at `config/agent_system_prompt.md`
> 2. Setup guide exists at `docs/agent-setup-guide.md`
> 3. `git add -A && git commit -m "Phase 9: Langdock Agent system prompt complete"`

---

## Phase 10: Dockerization & Deployment

**Goal:** The server runs in a Docker container and can be deployed to production.

**Prerequisites:** Phase 7 complete.

---

### Task 10.1: Create Dockerfile

- [x] Create `Dockerfile` as specified in DEV_TECH_DESIGN-0001 Section 8.1:
  - Base image: `python:3.12-slim`
  - Working directory: `/app`
  - Copy and install dependencies
  - Copy source code and config
  - Expose port 8080
  - CMD: uvicorn with host 0.0.0.0

---

### Task 10.2: Create docker-compose.yaml

- [x] Create `docker-compose.yaml` as specified in DEV_TECH_DESIGN-0001 Section 8.2:
  - Service: mcp-lektor
  - Environment variables from .env
  - Config volume (read-only)
  - Resource limits: 2G memory, 2.0 CPUs
  - Restart policy: unless-stopped

---

### Task 10.3: Build and Test Docker Image

- [x] Build the Docker image:

```bash
docker build -t mcp-lektor:latest .
```

- [x] Run the container:

```bash
docker run --rm -p 8080:8080 --env-file .env mcp-lektor:latest
```

#### INTERACTIVE TEST 10.3

> **Action:** Build and start the Docker container.
> **Expected:**
> - Build completes without errors
> - Container starts, server logs show "4 tools registered"
> - Server is accessible on http://localhost:8080
>
> **Report:** Paste the build log (last 10 lines) and the startup log.

---

### Task 10.4: Docker Compose Test

- [x] Create `.env` file (copy from `.env.example`, fill in values)
- [x] Run:

```bash
docker compose up -d
docker compose logs -f mcp-lektor
```

#### INTERACTIVE TEST 10.4

> **Action:** Start with docker compose and verify logs.
> **Expected:** Container starts, no errors in logs, server ready.
> **Cleanup:** `docker compose down`

---

### Task 10.5: Create Deployment Documentation

- [ ] Create `docs/deployment-guide.md` with:
  - Prerequisites (Docker, API keys)
  - Build instructions
  - Environment variable reference
  - docker compose instructions
  - Langdock MCP registration steps (from DEV_TECH_DESIGN-0001 Section 8.3)
  - Monitoring and troubleshooting tips
  - Resource sizing recommendations (from DEV_TECH_DESIGN-0001 Section 7)

---

### CHECKPOINT Phase 10 (Final)

> **Verify:**
> 1. `docker build` completes without errors
> 2. `docker compose up` starts the server correctly
> 3. All documentation files exist and are complete
> 4. `pytest tests/ -v` still passes (run outside Docker to confirm)
> 5. `git add -A && git commit -m "Phase 10: Dockerization & deployment complete"`
> 6. `git tag v0.1.0`

---

## Summary Checklist

| Phase | Status | Commit |
|-------|--------|--------|
| 0 - Project Scaffolding | [ ] | |
| 1 - Data Models | [x] | |
| 2 - Document Ingestion | [x] | |
| 3 - Rule-Based Checks | [x] | |
| 4 - LLM-Based Proofreading | [x] | |
| 5 - Bible Reference Validation | [x] | |
| 6 - OpenXML Track Changes & Comments | [x] | |
| 7 - Session Management & Server Assembly | [ ] | |
| 8 - End-to-End Integration Tests | [ ] | |
| 9 - Langdock Agent System Prompt | [ ] | |
| 10 - Dockerization & Deployment | [ ] | |

---

## Coding Style Reminders (from CODING_STYLE.md)

Apply these rules to EVERY file you create or modify:

1. **Language:** All code, comments, and docstrings in **English**
2. **Formatting:** Run `black .` before each commit
3. **Linting:** Run `ruff check .` before each commit — zero errors required
4. **Naming:** snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE_CASE for constants
5. **Functions:** Single responsibility, < 20 lines, max 3 arguments
6. **Comments:** Explain *why*, not *what*. Use docstrings for public API.
7. **DRY:** No code duplication — extract shared logic into utility functions
8. **Error Handling:** Use exceptions, not return codes or None
9. **Type Hints:** Required on all function signatures
10. **Context-Aware Refactoring:** When renaming, search all references project-wide first
