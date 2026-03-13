# ADR-0007: Local Bible Knowledge Base for Validation and Citation

## Status
Proposed

## Context
The previous attempts to validate Bible references relied on external services:
1.  `bible-api.com`: English-centric, required complex mapping, and introduced network dependency.
2.  `bibleserver.com` (Scraping): Fragile due to HTML structure changes and actively protected against automated queries (rate limiting/bot protection).

Furthermore, users require not just validation (is the reference correct?) but also **citation** (what does the text say?). Providing the actual Bible text directly within the Word document comments significantly improves the proofreading experience.

Research has identified several Public Domain (PD) and Creative Commons (CC) German Bible translations available in structured formats (JSON/XML), such as:
- Menge-Bibel (1939) - Public Domain
- Luther (1912) - Public Domain
- Elberfelder (1905) - Public Domain
- NeÜ (Neue evangelistische Übersetzung) - Generous license for non-commercial use/digital distribution.

## Decision
We will implement a **Local Bible Knowledge Base** integrated into the `ProofreadingEngine`.

1.  **Local Data Storage**: Bible texts for Menge, NeÜ, Elberfelder 1905, and Luther 1912 will be stored locally within the project (e.g., in `data/bibles/` as JSON files).
2.  **BibleProvider Service**: A new service will load these JSON files into memory at startup for near-instant validation and text retrieval.
3.  **Validation Logic**: A reference is considered valid if the requested book, chapter, and verse exist in the local datasets (using the Menge-Bibel as the primary structural reference).
4.  **Rich Citation**: For every identified Bible reference, the `ProofreadingEngine` will generate a `ProposedCorrection` that includes:
    - The actual text of the verse from the local translations (Menge, NeÜ, etc.).
    - Deep-links to `bibleserver.com` for modern protected translations (Luther 1984, current Elberfelder).
5.  **Offline Capability**: Core validation and citation will function without internet access, fulfilling the robustness requirement.

## Consequences
- **Positive**: **Extreme Robustness**. No more "API unreachable" errors or "Bot protection" blocks.
- **Positive**: **Performance**. Validation and text lookup happen in milliseconds.
- **Positive**: **User Value**. Direct visibility of Bible text in Word comments avoids switching between applications.
- **Negative**: **Storage**. Local JSON files will increase the project's footprint (approx. 5-10 MB per translation).
- **Negative**: **Maintenance**. If local data files are corrupted or need updates, a manual process is required (mitigated by the static nature of Bible texts).

## Alternatives Considered
- **Commercial Bible APIs**: Rejected due to cost, registration requirements, and privacy concerns.
- **Hybrid Scraping**: Rejected as it remains fragile and inconsistent across different internet environments.
- **On-demand Download**: Loading Bible data only when needed. Rejected in favor of a local data folder for better stability and simplicity.
