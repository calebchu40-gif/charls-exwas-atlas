# CHARLS result-table design success gate review (2026-10-24)

The result validator previously rejected unresolved or unavailable survey-design statuses on successful rows, but still permitted `not_applicable` statuses. That was too permissive for this project: CHARLS is a clustered sample survey, and the analysis protocol requires each successful fit to identify its weight choice and use the verified community PSU.

The validator now permits a successful row only when its weight choice is `verified_used` or `verified_unweighted`, its PSU is `verified_used`, and its variance stratum is either `verified_used` or `not_released`. A not-released stratum is acceptable only when the stated variance method explicitly identifies an approximation. The existing result schema still requires the method and its limitations to be documented. These rules do not establish that any particular CHARLS wave/module is ready for fitting; official weight applicability, module eligibility and variance method must still be reviewed separately.

Synthetic regression tests cover rejected `not_applicable` design choices, missing-PSU success, the approximation label for an unreleased stratum, and accepted verified design metadata. Tests use fabricated fixture values only. No respondent data, private summaries, model outputs, or CHARLS-specific counts are involved.

Run the focused tests with:

```powershell
python -m unittest tests.test_validate_exwas_result_table -v
```
