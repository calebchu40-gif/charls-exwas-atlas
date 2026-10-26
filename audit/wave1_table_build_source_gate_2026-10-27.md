# Wave 1 source gate on table construction (2026-10-27)

## Change

The Wave 1 table builder now verifies its private intake manifest before opening or extracting participant-level data. It requires all four separately reviewed inputs: the all-data archive, PSU, Weight, and Blood release files. Each received filename and locally computed SHA-256 must match the human-reviewed manifest and the official document/source-page identifiers already enforced by the intake audit. A missing, unresolved, renamed, or byte-changed source stops construction.

The builder records the resulting source-review status in the private prepared-data manifest. This is provenance evidence only; it does not pass age/eligibility, sample-frame, weight, PSU/strata, estimand, variance, or disclosure gates.

## Tests

Added synthetic-only tests for a missing release file, unresolved human source review, and a hash mismatch. No CHARLS participant records are included in tests. Focused tests passed (13); the full project suite passed (573 tests, 2026-10-27), with Python compilation and `git diff --check` passing.

## Current gate status

The protected intake directory still contains only the manifest and intake instructions; the four official release files are absent. Therefore the updated builder cannot run Wave 1 yet, and no formal model or association results were produced. Once authorized files are present, next actions remain: metadata-only intake preflight, source-identity review and hash pinning, wave-table preparation, published denominator/sample-frame reconciliation by respondent ID, official target-population/age-domain and blood-substudy eligibility review, PSU/strata/weight assessment, then frozen 105-hypothesis pilot reproduction. Only if all source/design/estimability checks pass does the staged expansion proceed; if not, document the specific redesign or stop reason without reporting confirmatory estimates.

## Privacy

Only code and synthetic tests are stored in this repository. Input files, prepared tables, intake hashes, sample counts, and estimates remain in protected local storage.
