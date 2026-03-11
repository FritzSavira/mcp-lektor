# DEV_TECH_DESIGN-0006: Bible Validation Integration

Detailed technical design for integrating Bible validation into the main proofreading pipeline.

## 1. Affected Components

| **Component** | **Change Description** |
|---------------|------------------------|
| `src/mcp_lektor/core/models.py` | Add `char_offset_start` and `char_offset_end` to `BibleReference`. |
| `src/mcp_lektor/core/bible_validator.py` | Populate offsets during extraction. |
| `src/mcp_lektor/core/proofreading_engine.py` | Call `BibleValidator.validate` and convert results to `ProposedCorrection`. |
| `tests/unit/test_proofreading_engine.py` | Add tests for Bible integration. |

## 2. Technical Details

### 2.1. Model Update (`models.py`)
```python
class BibleReference(BaseModel):
    paragraph_index: int
    raw_text: str
    book: str
    chapter: int
    verse_start: Optional[int] = None
    verse_end: Optional[int] = None
    char_offset_start: int = 0  # NEW
    char_offset_end: int = 0    # NEW
```

### 2.2. Validator Update (`bible_validator.py`)
In `extract_refs`, use the `start()` and `end()` methods of the regex match to populate the offsets.

### 2.3. Engine Integration (`proofreading_engine.py`)
In the `proofread` method:
1. Check if `CorrectionCategory.BIBLE_REFERENCE` is in the requested `checks`.
2. Instantiate `BibleValidator`.
3. Call `await validator.validate(structure)`.
4. Loop through `BibleValidationResult` objects:
    - Create a `ProposedCorrection`.
    - `paragraph_index` and offsets come from the `reference`.
    - `original_text = suggested_text = reference.raw_text`.
    - `explanation`:
        - If `is_valid`: "Bibelstelle verifiziert. Vergleichslinks: [LUT: url, EU: url...]"
        - If not `is_valid`: "FEHLER: [error_message]. Vergleichslinks: [Links]"
    - `run_index`: Needs to be determined based on the character offset (similar to how LLM corrections are mapped, although here we might just default to the run that contains the start offset).

### 2.4. Mapping to Runs
Since a Bible reference might span multiple runs (though unlikely if normalized), I will use a helper to find the `run_index` where the reference starts.

## 3. Risks & Considerations
- **Performance:** Bible validation involves network requests. If a document has 50 Bible references, it will perform 50 requests. The `BibleValidator` already uses `asyncio.gather` which helps, but we should ensure timeouts are reasonable.
- **Enabled Translations:** Only translations marked as `enabled: true` in `config.yaml` should be included in the explanation.
