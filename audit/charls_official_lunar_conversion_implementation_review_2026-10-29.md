# CHARLS official lunar-to-solar conversion: implementation review

Reviewed: 2026-10-29  
Pinned upstream: [`charls-data/lunar2solar`](https://github.com/charls-data/lunar2solar), commit `2284ccffdd74f057c234a446585ec32034b2d50d`  
Local source snapshot: [`references/charls_lunar2solar/`](../references/charls_lunar2solar/)

## What the official utility actually does

The CHARLS-maintained Stata command accepts an eight-character date string. It reads two precomputed lookup matrices from `lunar2solar.mmat`; the ordinary matrix covers 49,949 dates and the leap-month matrix covers 1,521 dates. The command matches the requested date against that table and writes the Gregorian conversion to a generated variable. The `leap` option selects the leap-month table. The official help file states the supported range is `19000101` through `20401128`, and says the date must be a string. The three files (`.ado`, `.mmat`, `.sthlp`) are installed together in Stata's PERSONAL directory.

The `.mmat` file is a Stata Mata matrix serialization, not a plain text date table. The `.ado` invokes Mata's `fgetmatrix()` and performs lookup/merge inside Stata. The help text describes the calendar conversion as based on the Python `lunardate` project, but the committed runnable interface is the Stata command and binary matrix snapshot. No separate, pinned Python runtime dependency or conversion API is included in this repository snapshot.

## Consequences for the CHARLS age pipeline

1. Keep the upstream three-file source and MIT notice together. Do not reimplement the date arithmetic from the `.mmat` binary by ad hoc parsing.
2. Convert only birth dates whose source questionnaire route explicitly establishes that the date is lunar. A missing or skipped calendar answer is not evidence that the date is solar.
3. Preserve the leap-month flag only when the source release identifies it. The upstream `leap` switch changes the lookup table; it is not a generic “try both and choose” option.
4. Validate date strings, calendar-type provenance, and year/month/day special codes before calling the command. Retain raw date fields, route/source fields, and conversion status in the protected preparation dataset.
5. The Stata executable is not available in the current local PATH. A Python-only production age implementation is therefore not approved by this review. The next valid options are to use a licensed Stata runtime in the protected environment or create an independent, documented implementation and validate it against the pinned official mapping on synthetic cases before any participant dates are processed.
6. Harmonized CHARLS age remains a comparison reference, not a substitute for release-specific raw-date routing or the official conversion.

## Status and scope

The initial source-code review read only the pinned program, help, license and binary file header; at that stage it did not inspect participant dates, derive ages, or fit models. The later controlled age-input preparation is documented below. It resolves how the official code works, but does not resolve which date/calendar route applies to each Wave 1/2 respondent, the exact fallback hierarchy, interview-month source, or age-domain definition. Those remain frozen-method and review gates.

## Wave 1 date-input metadata check (2026-10-29)

A metadata-only header review of the source-bound Wave 1 person table confirms the official labels for `ba002_1` (birth year), `ba002_2` (birth month), `ba002_3` (birth day), `ba003` (calendar type), and conditional `ba004` (self-reported age). It does **not** contain `iyear`/`imonth`. The separately verified official Wave 1 `Weight.dta` contains `ID`, `iyear` (interview year), and `imonth` (interview month); the interview-time fields therefore need an ID-validated private join before deriving age. The `bloodweight` field is absent from `Weight.dta` and remains in the separate official Blood release.

The official 2011 questionnaire says to enter month/day as `0` when the respondent does not remember them, and asks only whether the answer is solar or lunar. No separate leap-month response is documented for this birth-date item. The CHARLS converter's optional `leap` flag selects a different lookup table, so it must not be invoked without a source field or documented rule establishing a leap month. Ordinary lunar conversion is the tool default; incomplete dates, calendar status, and fallback to `ba004` still need an explicit age algorithm. The initial metadata-only review accessed no respondent values. A subsequent protected preparation step read only these official person-spine fields plus `iyear`/`imonth`, joined by unique respondent ID, and wrote a minimal age-input table to controlled local and server storage. No age conversion was performed. Row-level inputs and exact QA remain private; no DOB values or participant outputs entered Git, OneDrive, or Pages.

## Next action

**Historical note (written before the provisional interval candidate was generated):** The protected Wave 1 age-input table had been built from the source-reviewed person frame and Weight file. At that point, no age was calculated. Subsequent work generated an explicitly unapproved candidate interval table, documented below. The official CHARLS Stata runtime remains unavailable in checked environments, direct parity against the Mata lookup is not established, and no leap-month route may be inferred from the existing questionnaire fields. Do not release DOB-level data or exact DOB-derived diagnostics.

## Independent conversion reference candidate (2026-10-29)

The CHARLS-maintained Stata help file explicitly says `lunar2solar` is based on the [`lidaobing/python-lunardate` project](https://github.com/lidaobing/python-lunardate). The upstream project page identifies its current license as GPL-3.0 and documents fixed conversion examples; PyPI records `lunardate` 0.1.5 as released on 2014-09-09, shortly after the CHARLS Stata help's June 2014 version. This creates a plausible independently executable reference for synthetic validation, but not proof that a particular package release is byte-for-byte or date-for-date identical to CHARLS's `.mmat` lookup. The exact upstream revision used by CHARLS is not named, and the official Stata lookup remains the only direct parity target.

Next: acquire and pin a suitable upstream source revision in a protected scratch environment, inspect its license and date-range behavior, and validate synthetic examples. Keep it as a candidate only until parity evidence and independent methods review are sufficient. The subsequent Wave 1 run is documented below as provisional only; it does not approve the algorithm. Do not bundle GPL implementation code into the public project without a separate license review.
## 2026-10-29 retrieval correction

The official `lunar2solar.mmat` was retrieved from the CHARLS-maintained repository at the pinned commit already reviewed by this project, and separately from current upstream; the two files are byte-identical. The file is a Mata binary serialization. The present workstation and private server have no Stata executable, so direct matrix reading and date-by-date parity remain pending. Do not describe the file as unavailable; the limitation is the licensed reader/runtime.

## 2026-10-30 provisional age-candidate and route correction

The already-produced person-level age intervals remain an unreviewed, protected candidate, not an approved production age. Static review of the official 2011 questionnaire confirmed `ba003=1` solar, `ba003=2` lunar, and that conditional `ba004` is asked only when the complete `BA002` birth-date response is DK/RF. The candidate derivation previously fell back to `ba004` whenever the year was unavailable; this was too permissive for partial or invalid date inputs. It now uses `ba004` only when birth year, month, day, and calendar type are all missing. Partial/invalid DOBs remain unresolved. The age candidate was regenerated under the verified source manifest and its output hash rebound in private QA; the dependent exposure-coverage diagnostic was also regenerated. Direct equivalence to the official Mata lookup and independent methods review remain unresolved, so no age-based sample filtering or real-data association is authorized.
