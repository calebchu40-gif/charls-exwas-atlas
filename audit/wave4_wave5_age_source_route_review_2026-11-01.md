# Wave 4/5 age source and candidate derivation review (2026-11-01)

## Scope

This note records official source semantics and the protected age-candidate preparation for the 2018 and 2020 cross-sections. It does not impose an age-45 cutoff or define a disease-specific age domain. Exact age coverage, IDs, and row-level candidate values remain in server-private QA.

## 2018 / Wave 4

The official questionnaire asks for the birth date on the respondent's ID card or household register (`BA004_W3`). It then asks whether the respondent's actual date of birth matches that date (`BA005_W4`). The CAPI routing states that when `BA005_W4=1`, actual date of birth is taken from `BA004_W3`; when `BA005_W4=2` or the respondent has no/refuses an ID date (`BA004_W3=2/3`), actual date of birth is taken from `BA002`. `BA002_1` is actual birth year. The survey table also provides interview year `iyear`.

The protected candidate uses the documented route to select the actual birth year and computes `iyear - actual_birth_year`. Missing, unsupported, or inconsistent routes remain unavailable; no demographic field is guessed from a prior-wave value. This year-based age follows the survey's released age convention and avoids treating unknown month/day as an exact birthday.

## 2020 / Wave 5

The official questionnaire's generated field defines `XRAge` as `2020 - BA003_1` for new respondents or when prior birth year is empty, and `2020 - ZRBirthYear` otherwise. The protected candidate retains the released `XRAge` and checked it against that formula using the routed birth-year source. Formula and readback checks passed; exact match counts remain private. The fixed 2020 constant is preserved as specified by the source and is not silently replaced by an alternate birthday-adjusted age.

## Protected processing status

The age-candidate tables are hash-bound to the protected prepared-table manifest. Protected readback checks confirmed ID integrity, row-count preservation, plausible age bounds, and the official Wave 5 formula. These are candidate adjustment variables only. Pair-specific completeness, model target, any age-domain sensitivity, and association estimates are separate subsequent steps.

## Official source files

- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`, section BA004_W3–BA002.
- `sources_official/CHARLS_2018_Codebook_extracted.txt`, labels for BA004_W3, BA005_W4, BA002_1, and `iyear`.
- `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`, BA003 and generated `XRAge` code.
- `sources_official/CHARLS_2020_Codebook_extracted.txt`, `XRAge`, BA003_1, and `ZRBirthYear` labels.

## Next step

Register the later-wave household-environment × doctor-diagnosed-disease families with wave-specific fields and valid-value routes. Fit all registered hypotheses under the frozen cross-sectional frame, age/sex/settlement adjustment, and approximate community-cluster variance specification; retain nonestimable rows in the complete-family multiplicity denominator.
