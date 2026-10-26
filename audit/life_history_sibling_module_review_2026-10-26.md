# 2014 Life History sibling module field review (2026-10-26)

## Official-source review

Reviewed Section B (Sibling Information) in the official 2014 Life History Questionnaire and matched it to the FAMILYINFORMATION Codebook. The generated coverage ledger contains every one of the 271 Codebook fields whose code belongs to the B sibling module. All 271 fields now map to seven metadata-only candidate concepts; sibling survival status is paired with conditional B11 death year in one family-level outcome candidate. The 15 sibling education slots form a separate family-of-origin socioeconomic-context candidate, with timing and repeated-roster limitations explicit. Codebook response frequencies and participant data are not used.

## Candidate concepts and field mapping

| Concept | Fields | Role | Boundary |
|---|---:|---|---|
| Sibling deaths before age six and family relationship context | `b1`, `b2_1_*`, `b2_2_*`, `b2_3_*`, `b2_5_*` (61) | E | B1 count and repeated relationship, age-at-death, age-gap and parentage slots; B2 loops only when B1 indicates a death. Cause-of-death free text is excluded. |
| Sibling composition and half-sibling family structure | `b3`, `b4_2_*`, `b4_3_*`, `b5s*`, `b6_*` (72) | E | Count of siblings surviving to six; roster gender/birth year; parentage selectors and conditional relationship fields. No sibling names are included. |
| Highest completed education of siblings | `b4_5_*` (15) | E | Household/family socioeconomic context only; no age/date is given, so it cannot be assumed to precede the respondent's childhood. Roster slots are not independent exposures. |
| Sibling party-membership context | `b7s*` (26) | E | Sibling-list selectors, not 26 independent yes/no exposures. |
| Sibling ethnic-composition context | `b8s*`, `b9_*` (41) | E | Minority sibling selectors and conditional ethnicity categories; not the respondent's ethnicity. |
| Sibling sent-down movement experience | `b10s*` (26) | E | Sibling-list selectors for a sibling's historical experience; not necessarily respondent residence or exposure. |
| Survival status and death timing of siblings who survived to age six | `b4_4_*`, `b11_*` (30) | P | B4_4 alive/deceased gate and conditional B11 death year for deceased siblings. Family-level outcome, not respondent mortality; timing needs approved linkage and release verification. |

Repeated sibling slots, list selectors, and conditional branches are components of family-level history, not independent exposures/outcomes. The atlas does not derive sibling counts, mortality rates, respondent-level adversity, or event ages from these metadata fields.

## Deferred fields and exclusions

The field-level ledger `life_history_sibling_module_coverage_2014_v1.csv` dispositioned all 271 Codebook B fields. `b4_5_*` maps to one sibling-education family-context candidate. The lack of date/age remains a limitation: do not claim temporal precedence or treat each sibling slot as an independent exposure. `b4_4_*` is paired with the conditional `b11_*` death-year fields because the questionnaire explicitly uses the alive/deceased response to select the siblings routed to B11. These are family-level history fields, not respondent mortality or a mortality-rate denominator. Death-year linkage, sibling slot ordering, and any derived timing remain gated on authorized-release validation.

The questionnaire also asks for sibling names (`B4_1`) and open-text causes of death (`B2_4`, `B12`). They are excluded from the public catalog and were not found as structured fields in the Codebook B inventory. No names or free-text responses are ingested. The official B4 sibling roster order is required to interpret selector fields; the licensed release's storage and slot ordering still require verification.

## Catalog state and regeneration

The full 2014 Life History directory now contains 180 candidate concepts and 5,875 source-field mappings (5,814 E-role, 61 P-role). These counts include routed fields and repeated relative components and must not be read as independent measures. The 2014 special-wave fields remain separate from the five regular-wave pair matrix because the official release provides no survey weight and has a distinct sample composition.

Regenerate the crosswalk, special-survey JSON and 271-field B-module coverage ledger with:

```powershell
python scripts/build_life_history_exposure_crosswalk.py
```

