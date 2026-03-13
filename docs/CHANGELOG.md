# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-13] - UI and Robustness Refinement

### Added
- **Enhanced Comment Formatting**: `OpenXMLWriter` now supports multi-line comments and bold text. Bible validation results are now clearly structured with bold translation labels (e.g., **MENGE**) and clean line breaks for better readability.
- **Human-Readable Category Labels**: Comments in Word now use friendly German labels (e.g., `[Bibelstelle]`, `[Typografie]`) instead of technical enum names.
- **Configurable Bible Links**: Added `enable_bible_links` toggle in `config.yaml` to allow users to disable external `bibleserver.com` links while keeping local citations.
- **Robust Book Name Normalization**: Improved `BibleProvider` to handle case-insensitive lookups and variations with or without spaces/dots (e.g., "1. Mose", "1.Mose", "1 Mose").
- **Extended Bible Coverage**: Added missing book variants and singular forms (e.g., "Psalm", "Matthäus", "1. Chronik") to the detection regex and mapping tables.
- **Advanced Typography Rules**: Added new rules to `typography_rules.yaml` for professional German typesetting, including spaces in abbreviations (z. B.), units (10 kg), percentages (100 %), and correct en-dashes for ranges (10–12).

### Fixed
- **GUI Startup**: Resolved a `TypeError` in `gui.py` by removing the obsolete `use_online` parameter from `BibleValidator`.
- **Docker Data Access**: Updated `docker-compose.yaml` to correctly mount the `./data` directory, ensuring local Bible JSON files are accessible within the containers.
- **Redundant Bible Checks**: Removed duplicate Bible validation calls in the GUI to improve performance and reduce log clutter.
- **Path Stability**: Switched to absolute path resolution in `BibleProvider` to prevent "File Not Found" errors in containerized environments.

### Changed
- **Optimized UI Workflow**: Streamlined the `gui.py` processing loop to rely on the `ProofreadingEngine`'s integrated Bible validation.

## [2026-03-12] - Local Bible Knowledge Base

### Added
- **Local Bible Knowledge Base**: Implemented `BibleProvider` for sub-millisecond Bible reference validation and text lookup using local JSON data files (Menge, NeÜ, Elberfelder 1905, Luther 1912).
- **Rich Text Citations**: Bible references in Word comments now include the full text of the verse from up to four German translations, clearly labeled for easy comparison.
- **Offline Robustness**: The core Bible validation and citation functionality no longer requires an internet connection, fulfilling the project's requirement for a reliable and robust workflow (referencing ADR-0007).
- **New Data Model**: Extended `BibleValidationResult` to include `local_texts`, allowing the `ProofreadingEngine` to format rich explanations.

### Changed
- **Refactored Bible Validator**: Switched `BibleValidator` from fragile web scraping to a robust local-first architecture using the `BibleProvider`.
- **Improved Explanation Formatting**: Updated `ProofreadingEngine` to generate detailed, multi-translation explanations for all identified Bible references.
- **Regex Robustness**: Fixed a bug in `bible_patterns.py` where leading/trailing pipes in the book name regex could lead to incorrect empty matches.
- **Updated Configuration**: Added `local_bible_data_dir` to `ProofreadingConfig` and updated `config.yaml` to enable specific translations (LUT, ELB) for external comparison links.

### Removed
- **Scraping Logic**: Removed all `httpx`-based scraping and title-matching logic from `BibleValidator`, eliminating dependencies on `bibleserver.com`'s internal HTML structure.

## [2026-03-11] - Bible Validation Refinement
... [rest of file] ...
