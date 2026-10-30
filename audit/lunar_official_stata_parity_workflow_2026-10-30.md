# CHARLS official lunar conversion parity workflow

Reviewed: 2026-10-30  
Pinned CHARLS source: `charls-data/lunar2solar` commit `2284ccffdd74f057c234a446585ec32034b2d50d`

**Superseded status (2026-10-30):** a source-only parser now reads the pinned official `.mmat` matrices and compares every ordinary/leap mapping with pinned Python 0.1.4; the comparison completed with zero mismatches. A Stata runtime is therefore not required for this mapping-table parity subgate. The Stata workflow below is retained as an optional independent implementation cross-check, not as a prerequisite. See [`verify_official_lunar_table_parity.py`](../scripts/verify_official_lunar_table_parity.py) and [`wave1_age_interval_candidate_review_2026-10-29.md`](wave1_age_interval_candidate_review_2026-10-29.md).

## Purpose

The Wave 1 age candidate uses the CHARLS-maintained `lunar2solar` program as its conversion reference. Before any age candidate can be considered for an analysis specification, the reference implementation needs a direct synthetic cellwise comparison against the pinned `.mmat` tables. The previous Python 0.1.4/0.1.5 comparison only established matching mapping dimensions and agreement between those two Python releases; it did not establish parity with the CHARLS Mata tables.

## Prepared workflow

Two reusable files now support that direct comparison:

- `scripts/export_charls_lunar2solar_official_grid.do` asks the official ado and `.mmat` files to convert a grid of synthetic `YYYYMMDD` keys from 1900 through 2040, for ordinary and leap-month routes. It does not load or refer to participant data. Its CSV should be written to a protected temporary/QA directory and must not be committed or uploaded.
- `scripts/audit_lunardate_release_domain.py` accepts that CSV plus the pinned ado and `.mmat`, verifies the official-source hashes, checks the full synthetic key grid and published table dimensions, then compares each pinned Python release with the official lookup. Its report contains aggregate counts and booleans, not the mapping table.

Example after a licensed Stata runtime is available:

```stata
do scripts/export_charls_lunar2solar_official_grid.do "<project-root>" "<protected-qa-dir>/charls_lunar_grid.csv"
```

```text
python scripts/audit_lunardate_release_domain.py \
  <pinned-python-release-a.py> <pinned-python-release-b.py> \
  --official-grid-csv <protected-qa-dir>/charls_lunar_grid.csv \
  --official-ado references/charls_lunar2solar/src/lunar2solar.ado \
  --official-mmat references/charls_lunar2solar/src/lunar2solar.mmat \
  --output <protected-qa-dir>/lunardate_official_parity_aggregate.json
```

The Stata script creates its own temporary `PERSONAL` directory for the official ado's documented `.mmat` lookup and removes that temporary copy on normal completion. It does not change the user's permanent Stata configuration. Keep the generated CSV and report in controlled local storage. Do not send the synthetic lookup grid to GitHub, the public website, OneDrive, collaborators, or the analysis server.

## Current status and interpretation

This execution environment has no Stata runtime in PATH on the workstation or private server. Therefore the new direct comparison workflow is **prepared but not executed**, and parity with the official Mata matrix remains unresolved. No participant DOB or respondent-level data was used to write the workflow. No age algorithm, survey-design decision, or association model is approved by this work. Once executed, zero synthetic mismatches would establish converter parity over the stated lookup domain; it would still not resolve questionnaire routing, missing/leap-month interpretation, age measurement error, target population, survey variance, or independent methods review.
