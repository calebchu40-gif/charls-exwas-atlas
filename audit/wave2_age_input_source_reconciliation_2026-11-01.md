# Wave 2 age-input source reconciliation

**Status:** protected source reconciliation and provisional age-interval derivation completed; age estimand and association eligibility remain open.

## What was established

- The official Wave 2 Codebook lists `iyear` and `imonth` in the Weights module. The prepared respondent table had the birth-date routes but did not retain these interview-time fields, so the absence was a preparation omission rather than a missing official source.
- The official Wave 2 Weights archive was verified against the CHARLS-published release checksum. Its `iyear`/`imonth` fields were joined to the Wave 2 respondent spine by unique person ID in the protected server workspace.
- For Wave 2 records whose questionnaire confirms the preloaded birth date, the source-bound preparation links the corresponding Wave 1 respondent only through CHARLS's documented baseline-to-Wave-2 ID transformation. It assigns the Wave 1 calendar type only when all reported birth-date components agree exactly. Unmatched or discordant records remain explicitly unresolved.
- For records answering that the preloaded date is wrong, the preparation retains the Wave 2 date and its own Wave 2 calendar answer. Conditional self-reported age is preserved separately and is not treated as a universal age field.
- The protected age-input table and aggregate reconciliation QA are stored under the server's owner-only private directory. The public repository contains only this method note and the reproducible preparation script; it contains no IDs, dates, counts, hashes, or model outputs.
- A protected interval candidate was then generated using the already-pinned `python-lunardate` implementation after the project’s source-only comparison against both CHARLS Mata lookup matrices. It retains lower/upper completed-age bounds for unknown interview day and unresolved calendar routes, and leaves unsupported routes unresolved. The exact route QA and person-level interval table remain server-private.

## What remains

The interval table is a provisional age candidate, not a frozen adjustment variable or age-domain filter. It uses no assumed leap-month answer, does not use age to exclude respondents, and preserves unknown ages as unresolved. The project’s source-only converter comparison closes the lookup-table parity check; interview-day uncertainty, unresolved source routes, target-frame interpretation, and the age adjustment specification remain visible method choices. The Wave 2 association family still needs its wave-specific weight, target-frame, and community-cluster variance configuration documented before fitting. No Wave 2 association models were run in this preparation stage.

## Reproducibility

The implementations are [`scripts/prepare_wave2_age_inputs.py`](../scripts/prepare_wave2_age_inputs.py) and [`scripts/derive_wave2_age_intervals.py`](../scripts/derive_wave2_age_intervals.py). The first verifies the Weights archive and extracted member before reading values, uses unique-key joins, creates the minimal source-resolved age-input table only inside protected storage, and writes aggregate-only QA there. The second hash-checks the source-bound input and the pinned converter, checks parity against the official Mata lookup tables, and writes only a protected age-interval candidate plus private aggregate QA. A mismatch or unsupported route remains unresolved; neither script writes participant-level rows to the repository or public site.
