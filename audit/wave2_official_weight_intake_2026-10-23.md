# CHARLS 2013 official sample flags and weight intake

## Why this is a blocking item

The prepared local 2013 respondent table has 18,605 rows and contains several
weight variables, but it does not contain the official `crosssection` and
`longitudinal` sample-membership flags described for the Wave 2 `Weights.dta`
file. A positive or nonmissing weight is not a substitute for either flag.
Until the official file is merged and checked, 2013 results must not be assigned
to either target population and no pooled longitudinal model may use this wave.

## Safe intake

Download the official 2013 `Weights.dta` from the CHARLS account/release area
and place it in the access-controlled local folder:

```text
%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2013_weights\Weights.dta
```

Do not place the file in OneDrive, the project folder, GitHub, Pages, or a
shared server folder. The user must use their own authorized CHARLS account;
the project does not automate or bypass data access.

From the repository root, run:

```powershell
python scripts/merge_2013_official_weights.py `
  --weights "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2013_weights\Weights.dta"
```

The default output is a separate private DTA named
`CHARLS_wave2013_person_analytic_with_official_sample_flags.dta`. The merge
requires unique, nonmissing respondent IDs, both official sample flags, all
prepared respondents matched, unchanged respondent order, and agreement of
overlapping nonmissing weight values. It refuses collisions or incomplete
coverage and leaves the prepared source untouched. An aggregate-only QA JSON
records file hashes, row totals, match rate and sample-flag counts; it contains
no IDs or row-level records.

After reviewing the output, the existing protected replacement option may be
used to replace the standard prepared table while retaining a backup:

```powershell
python scripts/merge_2013_official_weights.py `
  --weights "$env:LOCALAPPDATA\CHARLS_ExWAS_Atlas\incoming_2013_weights\Weights.dta" `
  --replace-prepared
```

The replacement runs only after write/read-back checks and refuses to proceed
if its backup name already exists. Re-run `scripts/validate_prepared_wave_tables.py`
and the private core-concept coverage QA after the table is replaced. Confirm
that both flags are present in the validation output and independently inspect
official Wave 2 design guidance before selecting weights, strata, PSU, and
target population for an estimand. This merge only restores sample-membership
metadata and does not by itself establish a complete survey design.

## Evidence and status

The CHARLS Wave 2 release note describes `Weights.dta` as providing
cross-sectional and longitudinal sample identifiers. The project's local
official-source review is `audit/prepared_private_weight_sample_coverage_2026-10-23.md`;
the official release-note URL recorded there is
<https://charls.pku.edu.cn/en/data/Release2013.pdf>. At last local validation,
the original prepared table had no sample flags and no official `Weights.dta`
was found in the private data tree. The new merge utility has synthetic tests;
it has not yet been run on an official file.
