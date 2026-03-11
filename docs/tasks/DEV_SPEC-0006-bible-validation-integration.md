# DEV_SPEC-0006: Bible Validation Integration into Workflow

Integrate the `BibleValidator` into the `ProofreadingEngine` to provide automated checks and comparison links within the main proofreading pipeline.

## 1. Problem Description
Bible references are currently validated separately. To provide better UX, these findings should appear as "ProposedCorrections" in the main result, categorized as `BIBLE_REFERENCE`.

## 2. Functional Requirements
1.  **Engine Integration:** The `ProofreadingEngine` must call `BibleValidator.validate()` if `CorrectionCategory.BIBLE_REFERENCE` is requested.
2.  **Mapping Bible results to Corrections:**
    *   For **every** identified Bible reference, a `ProposedCorrection` must be created.
    *   **Case: Valid reference**
        - `original_text` == `suggested_text` (No change in text).
        - `category`: `BIBLE_REFERENCE`.
        - `explanation`: "Bibelstelle verifiziert. Vergleichslinks: [Links]".
        - `confidence`: `HIGH`.
    *   **Case: Invalid reference**
        - `original_text` == `suggested_text` (No change in text, we don't automatically "fix" the reference, as it's often a typo that requires human judgment).
        - `category`: `BIBLE_REFERENCE`.
        - `explanation`: "FEHLER: [ErrorMessage]. Vergleichslinks: [Links]".
        - `confidence`: `HIGH`.
3.  **Bibelserver Links formatting:** The explanation must contain a user-friendly list of the enabled Bibelserver translations and their URLs.
4.  **Offset Matching:** The `BibleValidator` provides `paragraph_index` and `raw_text`. The `ProofreadingEngine` must ensure that the `char_offset_start` and `char_offset_end` are correctly calculated by finding the `raw_text` within the paragraph's text.

## 3. User Experience Impacts
- Users see a "Comment" in Word for every Bible reference found.
- The comment contains clickable URLs to Bibelserver.
- If a reference is invalid (e.g. "Genesis 60"), the comment starts with a clear error warning.

## 4. Acceptance Criteria
- [ ] `ProofreadingEngine.proofread` calls the Bible validator.
- [ ] Valid and invalid Bible references appear as `ProposedCorrection` objects in the result.
- [ ] The `explanation` field contains the Bibelserver links.
- [ ] Offsets in `ProposedCorrection` correctly point to the Bible reference in the text.
- [ ] Unit tests for `ProofreadingEngine` verify the integration.
