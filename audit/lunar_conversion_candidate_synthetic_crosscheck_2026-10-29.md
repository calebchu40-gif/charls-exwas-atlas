# Lunar conversion candidate: synthetic cross-version check (2026-10-29)

## Purpose and boundary

The CHARLS Wave 1 birth-date field can be solar or lunar, while the current official lunar conversion utility is distributed as a Stata ado plus a Mata matrix. This check evaluates whether two locally pinned `python-lunardate` source releases behave consistently on synthetic dates. It does **not** establish equivalence to CHARLS's `.mmat` tables and does not authorize conversion of participant dates.

No CHARLS observations or DOB values were read. Only examples embedded in the package source and synthetic calendar inputs were evaluated. No association model was run.

## Reproducible synthetic cases

Both `python-lunardate` 0.1.4 and 0.1.5 returned the same solar date for each input:

| Synthetic lunar input | Solar output |
|---|---|
| 1900-01-01, ordinary month | 1900-01-31 |
| 1976-08-08, leap month | 1976-10-01 |
| 2008-09-04, ordinary month | 2008-10-02 |
| 2017-01-01, ordinary month | 2017-01-28 |
| 2020-01-01, ordinary month | 2020-01-25 |
| 2024-01-01, ordinary month | 2024-02-10 |
| 2049-12-29, ordinary month | 2050-01-22 |

The two package releases expose identical `yearInfos` conversion tables in this comparison. The leap-month case confirms that the API requires an explicit leap-month flag when that date is a leap month; the reviewed CHARLS Wave 1 DOB fields do not provide a separate documented leap-month indicator.

## Interpretation and remaining gates

This is an implementation consistency check, not an independent ground-truth validation: both package versions share the same lineage, and the outputs were not compared with the official CHARLS Mata `.mmat` conversion. CHARLS's official Stata program remains the preferred reference implementation. The official utility's date range and calendar handling must be verified against its actual table before using any alternative for participant data.

Age remains unconstructed and the age-source/derivation gate remains closed. Before using an alternative converter, obtain a valid comparison against official Stata output for a sufficiently broad synthetic grid covering ordinary/leap months, month-end/day-zero handling, calendar boundaries, and errors; preserve the source version, checksum, and exact validation code. If the official runtime remains unavailable, an independent reviewer must approve the documented alternative and its limits. Then reconcile solar/lunar response coding, unknown month/day values, interview date, spouse eligibility, and the 45+ target-domain definition before deriving age.

## Reproduction

The comparison used the `LunarDate(year, month, day, isLeapMonth).toSolarDate()` API from the locally stored source files for releases 0.1.4 and 0.1.5. Inputs and outputs are listed above; no package was installed into the project runtime.

## Exhaustive documented-domain audit (2026-10-29)

The CHARLS-maintained [`lunar2solar` help](https://github.com/charls-data/lunar2solar/blob/main/src/lunar2solar.sthlp) explicitly says its conversion is based on `lidaobing/python-lunardate`; the official ado constructs lookup matrices with 49,949 ordinary-date rows and 1,521 leap-date rows over its documented numeric input range. A new metadata-only audit script, [`scripts/audit_lunardate_release_domain.py`](../scripts/audit_lunardate_release_domain.py), exhaustively enumerates valid synthetic dates in that range using the locally pinned source files for `python-lunardate` 0.1.4 and 0.1.5.

Both releases produced 49,949 ordinary and 1,521 leap mappings (51,470 total), exactly matching the two official matrix dimensions. Their valid input-key coverage was identical and there were zero output mismatches across shared keys. Source SHA-256 values are recorded in the protected aggregate report at `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\lunardate_exhaustive_sweep_20261029.json`; the report contains no date mappings or CHARLS values.

This materially strengthens the converter's lineage and domain evidence, but still is not a direct cell-by-cell comparison to `lunar2solar.mmat`, and both Python releases share a code lineage. The official CHARLS command defaults to the ordinary-month table unless the `leap` option is supplied. Wave 1 records calendar type but the questionnaire does not document a leap-month indicator, so the conversion route must preserve that uncertainty and must not infer a leap flag. No respondent date was converted in this audit; the age derivation and survey-design/model gates remain closed pending a frozen route and methods review.

The reusable audit accepts caller-supplied source paths and emits only aggregate counts. It does not bundle, install, or redistribute the GPL-licensed package source.
