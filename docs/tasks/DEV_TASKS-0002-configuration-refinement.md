# DEV_TASKS-0002: Configuration and Model Refinement

**Status:** DONE
**Date:** 2026-03-09
**Author:** Gemini CLI
**Related ADR:** [ADR-0002](docs/adr/ADR-0002-refined-configuration-and-model-separation.md)

---

## Phase 1: Structural Preparation
- [x] Create `src/mcp_lektor/core/enums.py` and migrate shared enumerations.
- [x] Update `src/mcp_lektor/core/models.py` to import enums from the new module.
- [x] Update `src/mcp_lektor/config/models.py` to import enums from `core.enums`.
- [x] Verify that there are no circular imports.

## Phase 2: Configuration Enhancements
- [x] Update `src/mcp_lektor/config/settings.py` to provide access to the full `AppConfig`.
- [x] Implement environment variable override logic (prefix `LEKTOR_`) in `AppConfig` or the loader.
- [x] Add support for "Smart Reloading" by providing a singleton accessor for settings.

## Phase 3: Domain Integration
- [x] Update `src/mcp_lektor/server.py` to use `AppConfig.server`.
- [x] Update `src/mcp_lektor/core/session_manager.py` to use `AppConfig.session`.
- [x] Update `src/mcp_lektor/gui.py` to use the unified configuration logic (ensuring it remains a dev-only tool).

## Phase 4: Validation
- [x] Run all existing unit and integration tests.
- [x] Verify environment variable overrides manually or with a new test case.
- [x] Ensure `ruff` and `black` compliance.
