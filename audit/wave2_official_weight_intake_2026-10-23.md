# CHARLS 2013 official sample flags and weight intake

> **Current correction (2026-10-29):** The official SHA-1 listed by CHARLS is for the downloaded `2013_318_Weights.zip`, not the extracted `Weights.dta`. The older instructions below incorrectly treated it as a DTA checksum and described the official file as unavailable. The archive is now present in the protected local intake and passes the official ZIP checksum plus metadata-only inspection of its unique `Weights.dta` member. The extraction is temporary and protected; no merge was performed in this update. Use `audit/wave2_weights_metadata_intake_gate_2026-10-25.md` for the corrected command and current status. `merge_2013_official_weights.py` now requires both `--weights` and `--weights-archive`, then confirms the supplied DTA bytes match the checked ZIP member before reading values.

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

The official Wave 2 release page lists the 2015-11-18 `Weights.dta` package
with SHA1 `22c4fc89df2e55fa8faf051e88830eebe0e035c0`. The intake script checks
this release hash before reading or merging the file; a different package is
rejected until its official source/version is reviewed and the pinned checksum
is deliberately updated. The post-merge QA also records the official SHA1 and
a local SHA-256 digest.

The Peking University Open Research Data Platform also lists a Wave 2
`Weights.tab` file (Version 1.1; 19 variables; 19,679 observations; page-reported
MD5 `fe914ea9ba15da968c756217587e5d4b`). Its file page states that access
requires a signed-in account/request and presents CHARLS academic-use terms.
This is a separate tab-delimited artifact, not the hash-pinned CHARLS portal
`Weights.dta`; do not rename it or feed it to the current DTA intake script.
If an authorized account obtains this alternate file, preserve it separately
and first compare its metadata, field names, sample-flag definitions, version,
and provenance against the official Wave 2 Release Note. Any new intake path
must be reviewed and tested before it is allowed to supply analysis flags.

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

The official 2013 release note also distinguishes cross-sectional weights with/without nonresponse adjustment, a longitudinal weight based on baseline weights and second-wave participation (with deaths treated as responses in its construction), and a separate cross-sectional biomarker weight that applies a biomarker-response inverse-probability factor capped at its 99th percentile. It states that no longitudinal biomarker weight is offered. These are different target estimands and must not be substituted for one another. See [`wave2_weight_estimand_source_review_2026-10-24.md`](wave2_weight_estimand_source_review_2026-10-24.md). Restoring the two sample flags does not by itself decide which weight applies to a specific analysis or resolve the variance design.

The CHARLS Wave 2 release note describes `Weights.dta` as providing
cross-sectional and longitudinal sample identifiers. The project's local
official-source review is `audit/prepared_private_weight_sample_coverage_2026-10-23.md`;
the official release-note URL recorded there is
<https://charls.pku.edu.cn/en/data/Release2013.pdf>. At last local validation,
the original prepared table had no sample flags and no official `Weights.dta`
was found in the private data tree. The new merge utility has synthetic tests;
it has not yet been run on an official file. The alternate Dataverse file record
is <https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=95&fileId=198>;
its access gate and distinct format/MD5 are recorded above. No portal access was
requested and no restricted file was fetched.
