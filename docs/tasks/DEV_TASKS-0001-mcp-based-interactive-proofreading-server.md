# DEV_TASKS-0001: MCP-Based Interactive Proofreading Server

**Status:** ALL PHASES COMPLETE (Sprint 3 Complete)
**Date:** 2026-03-06
**Author:** Gemini CLI

---

## Phase Overview

| Phase | Title | Status |
|-------|-------|--------|
| 0 | Project Scaffolding | [x] DONE |
| 1 | Data Models | [x] DONE |
| 2 | Document Ingestion | [x] DONE (with Run Normalization) |
| 3 | Rule-Based Checks | [x] DONE |
| 4 | LLM-Based Proofreading | [x] DONE (with Straico/Langdock support) |
| 5 | Bible Reference Validation | [x] DONE (with offline fallback) |
| 6 | OpenXML Track Changes & Comments | [x] DONE (with XML validation) |
| 7 | Session Management & Server Assembly | [x] DONE (Thread-safe, cleanup task) |
| 8 | End-to-End Integration Tests | [x] DONE (16/16 tests passing) |
| 9 | Langdock Agent System Prompt | [x] DONE (Prompts & User Guide created) |
| 10 | Dockerization & Deployment | [x] DONE (Dockerfile/Compose verified) |

---

## Sprint 2 & 3: Core Robustness & Production Grade

### Task S2.1: Run Normalization (Fragmentation Fix)
- [x] Implement `RunNormalizer` to merge identical adjacent runs.
- [x] Integrate normalization into `parse_docx`.
- [x] Add unit tests for merger logic.

### Task S2.2: XML Integrity Validation
- [x] Implement `validate_docx_structure` using `lxml`.
- [x] Add automated validation post-write in `document_io.py`.

### Task S3.1: Centralized Configuration
- [x] Expand `ProofreadingConfig` with logic-guiding parameters.
- [x] Update `config.yaml` with address-form, bible, and retry settings.

### Task S3.2: Bible API Fallback
- [x] Add Protestant canon chapter counts for offline validation.
- [x] Implement configurable API timeouts and fallback logic.

### Task S3.3: Address-Form Tie-Breaking
- [x] Implement counting logic for "Du" vs "Sie".
- [x] Use `default_address_form` from config for ties.

### Task S3.4: LLM Error Recovery
- [x] Implement exponential backoff retry loop in `llm_client.py`.

---

## Summary Checklist (Final Acceptance)

- [x] All 16 integration tests passing.
- [x] No `ruff` or `black` violations.
- [x] All MCP tools return JSON strings for protocol compliance.
- [x] XML Validation prevents corrupt .docx generation.
- [x] Run Fragmentation issue resolved.
- [x] Straico & Langdock providers tested.
- [x] Docker image builds and starts.
- [x] Agent system prompt and user guide documented.
