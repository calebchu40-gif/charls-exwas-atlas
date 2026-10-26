# 2014 Life History RESIDENCE full-field review (2026-10-26)

## Scope and source basis

Reviewed the official 2014 Life History Questionnaire Residence section and its matching Codebook module. The full module has 935 structured fields, all assigned exactly one disposition in `life_history_residence_full_coverage_2014_v1.csv`. The field-coverage builder fails if a field is unmapped, duplicated, or if the inventory changes without review. Only official questionnaire wording and Codebook names/labels are used; Codebook frequency tables and participant values are excluded.

## Newly mapped candidate concepts

### T001a/T001b: residential episode timeline (250 fields)

Maps the same-time indicator and year/month/season/half-year fields for entry to and exit from up to 25 residences. The first entry may coincide with birth; later entries can coincide with the prior residence exit. T001b can indicate that the respondent still lives in the listed residence; incomplete or same-time dates cannot be naively subtracted. This is a retrospective residential-mobility timeline candidate, not a geocoded or pollutant exposure. Participant dates are never published, and no duration or cumulative index is derived in the metadata build.

### T003e: migration reasons during residence-history gaps (169 fields)

The questionnaire's T002e branch identifies periods of cross-county mobility where gaps exceed six months before, between, or after listed residences. T003e asks reasons the respondent stopped this mobility. It is distinct from T003c, which asks why the respondent left a listed residence. The 169 option-by-episode fields are one concept family, not 169 exposures; unselected slots are not coded No and write-in “Other” text is excluded.

## Complete module disposition

| Disposition | Fields | Interpretation |
|---|---:|---|
| Mapped E/P candidate metadata | 827 | Existing 408 fields plus 250 T001 timing and 169 T003e gap-reason fields |
| Excluded geographic/location metadata | 95 | Residence location/county and T002e region codes; no geocoding or external linkage |
| Deferred respondent demographic/ID verification | 6 | Birth date, gender and identity-card consistency metadata |
| Excluded person/household/community linkage keys | 3 | Controlled joins only when authorized and required |
| Excluded proxy/interview metadata | 3 | Interview respondent/proxy and relationship fields |
| Excluded release-version metadata | 1 | Not an E/P measure |
| **Total** | **935** | **Every RESIDENCE Codebook field dispositioned once** |

The official release note warns that `t002_psu_*` location codes are not directly comparable to `PSU.dta`. Those fields and all other geographic location values are excluded from the public association atlas; rural/urban context remains a separate questionnaire measure and is not treated as an objective environmental exposure.

## Reproducibility

`scripts/build_life_history_exposure_crosswalk.py` generates the full ledger plus dedicated 250-row T001 and 169-row T003e ledgers. Unit tests enforce exact module totals, unique field coverage, separation of T003c/T003e concepts, and exclusion of geolocation metadata from E/P mapping.
