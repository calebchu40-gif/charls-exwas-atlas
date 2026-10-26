# 2014 Life History sibling module field review (2026-10-26)

## Official-source review

Reviewed Section B (Sibling Information) in the official 2014 Life History Questionnaire and matched it to the FAMILYINFORMATION Codebook. The generated coverage ledger contains every one of the 271 Codebook fields whose code belongs to the B sibling module. It assigns 256 fields to seven metadata-only candidate concepts and explicitly defers the 15 undated sibling living-status fields. The 15 sibling education slots are included as a family-of-origin socioeconomic-context candidate, with timing and repeated-roster limitations explicit. Codebook response frequencies and participant data are not used.

## Candidate concepts and field mapping

| Concept | Fields | Role | Boundary |
|---|---:|---|---|
| Sibling deaths before age six and family relationship context | `b1`, `b2_1_*`, `b2_2_*`, `b2_3_*`, `b2_5_*` (61) | E | B1 count and repeated relationship, age-at-death, age-gap and parentage slots; B2 loops only when B1 indicates a death. Cause-of-death free text is excluded. |
| Sibling composition and half-sibling family structure | `b3`, `b4_2_*`, `b4_3_*`, `b5s*`, `b6_*` (72) | E | Count of siblings surviving to six; roster gender/birth year; parentage selectors and conditional relationship fields. No sibling names are included. |
| Highest completed education of siblings | `b4_5_*` (15) | E | Household/family socioeconomic context only; no age/date is given, so it cannot be assumed to precede the respondent's childhood. Roster slots are not independent exposures. |
| Sibling party-membership context | `b7s*` (26) | E | Sibling-list selectors, not 26 independent yes/no exposures. |
| Sibling ethnic-composition context | `b8s*`, `b9_*` (41) | E | Minority sibling selectors and conditional ethnicity categories; not the respondent's ethnicity. |
| Sibling sent-down movement experience | `b10s*` (26) | E | Sibling-list selectors for a sibling's historical experience; not necessarily respondent residence or exposure. |
| Death years of siblings who survived to age six | `b11_*` (15) | P | Conditional family-level death-year fields, not respondent mortality. Relative timing needs respondent birth-year linkage and release verification. |

Repeated sibling slots, list selectors, and conditional branches are components of family-level history, not independent exposures/outcomes. The atlas does not derive sibling counts, mortality rates, respondent-level adversity, or event ages from these metadata fields.

## Deferred fields and exclusions

The field-level ledger `life_history_sibling_module_coverage_2014_v1.csv` dispositioned all 271 Codebook B fields. The 15 deferred fields are:

- `b4_4_*`: sibling alive/deceased status without an event date in that field; retained as roster/routing metadata.

`b4_5_*` now maps to one sibling-education family-context candidate. The lack of date/age remains a limitation: do not claim temporal precedence or treat each sibling slot as an independent exposure. `b4_4_*` remains deferred because current living status is an undated attribute of another person and cannot safely be turned into respondent exposure or phenotype from metadata alone.

The questionnaire also asks for sibling names (`B4_1`) and open-text causes of death (`B2_4`, `B12`). They are excluded from the public catalog and were not found as structured fields in the Codebook B inventory. No names or free-text responses are ingested. The official B4 sibling roster order is required to interpret selector fields; the licensed release's storage and slot ordering still require verification.

## Catalog state and regeneration

The independent 2014 Life History directory now contains 33 candidate concepts and 785 source-field mappings (757 E-role, 28 P-role). These counts include routed fields and repeated sibling components and must not be read as independent measures. The public view remains separate from the five regular-wave pair matrix because the official 2014 release provides no survey weight and has a distinct sample composition.

Regenerate the crosswalk, special-survey JSON and 271-field B-module coverage ledger with:

```powershell
python scripts/build_life_history_exposure_crosswalk.py
```

