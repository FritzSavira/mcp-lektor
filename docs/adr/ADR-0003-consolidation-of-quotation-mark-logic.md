# ADR-0003: Consolidation of Quotation Mark Logic

## Status
Proposed

## Context
The project currently uses two redundant modules for handling quotation marks:
1.  `quotation_checker.py`: A rule-based script that flags all straight double quotes (`"`) and suggests `„ oder “` without context.
2.  `typography_checker.py`: A regex-based engine that uses rules from `config/typography_rules.yaml`. It already has rules for distinguishing between opening (`„`) and closing (`“`) quotes based on word boundaries.

The redundant `quotation_checker.py` results in duplicate and low-quality suggestions, confusing the user and complicating the deduplication logic in the `ProofreadingEngine`. Furthermore, the user requirement specifies that corrections should be applied directly as track changes with correct typographic marks and an explanatory comment in the Word document.

## Decision
We will consolidate the quotation mark logic into the `TypographyChecker` and remove the redundant implementation from `quotation_checker.py`.

1.  **Single Source of Truth:** `config/typography_rules.yaml` will be the primary source for typographic rules, including quotation marks.
2.  **Refactor `quotation_checker.py`:** The existing simple check for `"` will be removed. The module will be kept as a placeholder or repurposed for future stateful/structural checks (e.g., balancing/pairing), but it will no longer issue simple replacement suggestions.
3.  **Direct Correction:** The `TypographyChecker` will provide specific corrections (either opening or closing) which will be processed by the `openxml_writer.py` to insert Track Changes and comments.
4.  **Explanatory Comments:** Every typographic correction will result in an explanatory comment in the Word document, as handled by the `openxml_writer.py` using the `explanation` field from the rule.

## Consequences
- **Positive:** Improved code maintainability (DRY), better user experience through context-aware suggestions, and a single point of configuration for typography.
- **Positive:** Reduced overhead in the `ProofreadingEngine` and simpler deduplication.
- **Negative:** Simple "balancing" checks (e.g., "is there an odd number of quotes?") are not covered by regex-based rules alone and would require a stateful implementation in the future.
