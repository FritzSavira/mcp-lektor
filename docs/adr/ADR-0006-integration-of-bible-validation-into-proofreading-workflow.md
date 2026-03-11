# ADR-0006: Integration of Bible Validation into Proofreading Workflow

## Status
Proposed

## Context
Currently, Bible reference validation is a standalone MCP tool (`validate_bible_refs`). Users have to trigger it manually, and the results are not integrated into the main `proofread_text` output or the final Word document export (unless the user manually processes the JSON output).

To provide a seamless experience, Bible validation should be part of the regular proofreading pipeline.

## Decision
We will integrate the `BibleValidator` into the `ProofreadingEngine`.

1.  **Pipeline Integration:** The `ProofreadingEngine` will call the `BibleValidator` during its rule-based check phase.
2.  **Result Conversion:** `BibleValidationResult` objects will be converted into `ProposedCorrection` objects.
    - If a reference is **valid**, no correction is generated (unless we want to provide the comparison links as a comment anyway). 
    - If a reference is **invalid** (as determined by Bibelserver scraping or unknown book), a `ProposedCorrection` with `CorrectionCategory.BIBLE_REFERENCE` will be created.
3.  **Information Richness:** The `explanation` field of the correction will include the error message and the generated `bibelserver.com` comparison links, making them visible in the Word document's comments.
4.  **Control:** The Bible check will be tied to the `CorrectionCategory.BIBLE_REFERENCE` in the `checks` list, allowing users to enable/disable it.

## Consequences
- **Positive:** Unified workflow. All findings (spelling, grammar, Bible refs) appear in a single report and one exported document.
- **Positive:** Comparison links are directly accessible via Word comments.
- **Negative:** The main proofreading task might take longer due to the synchronous (though batched) network requests to Bibelserver.
- **Neutral:** Valid Bible references will no longer appear as "findings" in the correction list unless we decide to include them as informational comments.
