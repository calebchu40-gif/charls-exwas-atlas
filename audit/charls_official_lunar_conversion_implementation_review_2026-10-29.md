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

This review read only the pinned source code, help, license and binary file header. It did not install or execute the command, inspect participant date values, derive ages, or fit models. It resolves how the official code works, but does not resolve which date/calendar route applies to each Wave 1/2 respondent, the exact fallback hierarchy, interview-month source, or age-domain definition. Those remain frozen-method and review gates.

## Wave 1 date-input metadata check (2026-10-29)

A metadata-only header review of the source-bound Wave 1 person table confirms the official labels for `ba002_1` (birth year), `ba002_2` (birth month), `ba002_3` (birth day), `ba003` (calendar type), and conditional `ba004` (self-reported age). It does **not** contain `iyear`/`imonth`. The separately verified official Wave 1 `Weight.dta` contains `ID`, `iyear` (interview year), and `imonth` (interview month); the interview-time fields therefore need an ID-validated private join before deriving age. The `bloodweight` field is absent from `Weight.dta` and remains in the separate official Blood release.

The official 2011 questionnaire says to enter month/day as `0` when the respondent does not remember them, and asks only whether the answer is solar or lunar. No separate leap-month response is documented for this birth-date item. The CHARLS converter's optional `leap` flag selects a different lookup table, so it must not be invoked without a source field or documented rule establishing a leap month. Ordinary lunar conversion is the tool default; incomplete dates, calendar status, and fallback to `ba004` still need an explicit age algorithm. This metadata review accessed no respondent values and did not join or transform dates.

## Next action

The immediate preparation step is to bind the verified Weight `iyear`/`imonth` fields to the official birth-date fields by unique respondent ID inside protected storage. Then locate a Stata runtime already authorized for the protected workspace. Before processing participant dates, validate the conversion against the pinned official lookup using synthetic solar/lunar examples, explicit leap-month status only if an official input exists, incomplete/invalid dates, and conversion failures. Do not release DOB-level data or exact DOB-derived diagnostics.
