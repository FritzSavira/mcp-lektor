# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-10] - Consolidation of Quotation Mark Logic

### Added
- **Anchored Comments**: Enhanced `OpenXMLWriter` to position comments precisely at the occurrence instead of the paragraph end.
- **Comment-Only Corrections**: Implemented support in `OpenXMLWriter` for corrections that only provide a hint without changing the text (where `original_text == suggested_text`).

### Changed
- **Typography Checker Consolidation**: Moved all quotation mark detection and correction logic into `src/mcp_lektor/core/typography_checker.py`, using rules from `config/typography_rules.yaml`.
- **Refined Typographic Rules**: Updated `config/typography_rules.yaml` with context-aware regex to distinguish between opening („) and closing (“) German quotation marks (referencing ADR-0003).
- **Proofreading Engine Update**: Simplified `ProofreadingEngine` to call `check_typography` for both general typography and quotation marks, ensuring a single source of truth for these rules.
- **Confused Words Refinement**: Switched `ConfusedWordsChecker` to "comment-only" mode to provide hints (e.g., "Prüfen: Gemeinde/Kirche") without distracting track changes in the text.

### Removed
- **Redundant Quotation Checker**: Deprecated the simple rule-based implementation in `src/mcp_lektor/core/quotation_checker.py` to prevent duplicate and low-quality suggestions.

### Fixed
- **Word Export Integrity**: Ensured that quotation mark corrections result in correct typographic marks (unten/oben) and that the `openxml_writer.py` correctly inserts these as Track Changes with explanatory comments.

## [2026-03-09] - Architectural Refinement

### Added
- **Dedicated Enum Module**: Created `src/mcp_lektor/core/enums.py` to house shared enumerations, eliminating circular dependencies between domain and configuration models.
- **Environment Overrides**: Implemented `LEKTOR_` prefix support for all configuration settings, enabling easy environment-based configuration for Docker and Langdock deployments.
- **Smart Settings Accessor**: Introduced `get_settings()` with optional `reload=True` to support live-reloading of configuration files in development tools like Streamlit.

### Changed
- **Unified Configuration**: Refactored `src/mcp_lektor/config/settings.py` to use a validated `AppConfig` root model for all application sections (Server, Proofreading, Session).
- **Session Manager Integration**: Updated `SessionManager` to use settings from `config.yaml` for TTL and cleanup intervals.
- **Server Integration**: Updated `server.py` to utilize centralized server configuration (host, port, log level).
- **Refined Data Models**: strictly separated domain models in `core/models.py` from configuration models in `config/models.py`.

### Fixed
- **Circular Import Risk**: Resolved implicit loop where configuration models depended on domain models containing enums.
- **Inconsistent Config Loading**: Eliminated hardcoded defaults in server and session management modules.

## [2026-03-06] - Sprint 1-3 Summary

### Added
- **MCP Server Architecture**: Fully implemented FastMCP server with SSE transport.
- **Run Normalization**: Added logic to merge fragmented Word runs with identical formatting to improve correction accuracy.
- **XML Validation**: Integrated `lxml`-based structural validation for generated .docx files.
- **Bible API Robustness**: Added offline fallback for Protestant canon (chapter counts) and configurable API timeouts.
- **Centralized Configuration**: Moved logic parameters (address form, thresholds, retries) to `config.yaml`.
- **LLM Robustness**: Implemented exponential backoff for LLM API calls.
- **Straico Integration**: Added support for Straico API as a development LLM provider.
- **Session Management**: Thread-safe, centralized session manager with background cleanup.
- **End-to-End Tests**: Full pipeline integration tests (Extract -> Proofread -> Validate -> Write).

### Changed
- Refactored all MCP tools to return JSON strings instead of dicts for protocol compliance.
- Harmonized session metadata to prevent `KeyError` during tool handovers.
- Updated `is_red` detection to use configurable thresholds.

### Fixed
- Fixed run fragmentation breaking character offsets in OpenXML writer.
- Resolved `pytest-asyncio` environment issues for async integration tests.
- Fixed `python-docx` session persistence in multi-worker scenarios.

## [2026-03-04] - Initial Setup

### Added
- Project scaffolding and CI configuration.
- Core data models for document structure and proofreading results.
- Basic document ingestion for .docx files.
- Rule-based checkers for typography and confused words.
