# Changelog

All notable changes to this project will be documented in this file.

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
