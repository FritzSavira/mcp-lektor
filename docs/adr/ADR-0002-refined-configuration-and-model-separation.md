# ADR-0002: Refined Configuration and Model Separation

**Status:** Proposed
**Date:** 2026-03-09
**Author:** Gemini CLI

## Context
The initial implementation of MCP Lektor mixed configuration models with domain models in `src/mcp_lektor/core/models.py`. While a previous refactoring moved configuration to `src/mcp_lektor/config/models.py`, several architectural "smells" remain:
1. **Circular Dependency Risk:** `config/models.py` imports `CorrectionCategory` from `core/models.py`, creating a potential loop if domain models ever need configuration types.
2. **Inconsistent Config Usage:** The `FastMCP` server and `SessionManager` still use hardcoded defaults or separate environment variable lookups instead of the validated `AppConfig` from `config.yaml`.
3. **Langdock Compatibility:** Production deployment in the Langdock ecosystem requires flexible configuration via environment variables, which is currently only partially implemented.

## Decision
1. **Extract Shared Enums:** All pure enumerations (Enums) that are used by both configuration and domain logic will be moved to `src/mcp_lektor/core/enums.py`. This module will have zero internal dependencies.
2. **Unified AppConfig:** The `load_config()` function in `settings.py` will be supplemented by a `get_settings()` singleton or similar pattern that provides access to the full `AppConfig` (Server, Proofreading, and Session sections).
3. **Environment Overrides:** Pydantic's `SettingsConfigDict` or a manual merge logic will be implemented to allow environment variables (prefixed with `LEKTOR_`) to override `config.yaml` values.
4. **Dependency Injection:** The `SessionManager` and `FastMCP` initialization will be updated to accept configuration objects rather than relying on global defaults.

## Consequences
- **Positive:** Improved maintainability and testability.
- **Positive:** Standardized configuration for Docker/Production (Langdock).
- **Positive:** Elimination of circular import risks.
- **Neutral:** Requires updating imports across the entire codebase.
- **Negative:** Small overhead in initial setup of the configuration singleton.
