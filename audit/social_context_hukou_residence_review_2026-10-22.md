# Historical hukou and residential context review (2026-10-22)

## Scope and source review

This metadata-only pass reviewed CHARLS 2011/2013 retrospective hukou-location questions, 2015/2018 prior-interview hukou status, 2018 prior-wave and current dwelling context, and 2020 current dwelling type. Official questionnaires and codebooks were used to retain exact wave-specific wording, routing, reference period, and response categories. No respondent-level records or response frequencies were read.

## Candidate mappings

The crosswalk adds 11 source-field links across 9 concepts: last hukou location relation (2011 and 2013 separately), first hukou location relation (2011 and 2013 separately), reason current hukou location differs from first location (2011), prior-interview hukou type (2015 and 2018), 2018 prior-wave dwelling type and settlement context, and current dwelling type (2018 and 2020).

Historical questions are route-conditional. The 2011 and 2013 location categories differ and remain wave-specific; no category code is harmonized by numeric value. Prior-interview hukou type is not current status. 2018 BB000_W3 refers to the prior interview time, while BB001_W3 is asked only on the new-interview route. The 2020 BA007 item is recorded for a named household roster member, so respondent linkage must be confirmed before any analysis. Household/roster and respondent units must not be mixed.

## Exclusions and privacy boundary

Exact residential address strings (2018 BB000_W3/BB001_W3 and 2020 BA006), geographic detail child fields for retrospective hukou locations, and open-ended “other specify” text fields are C metadata and excluded from the public E/P association matrix. `bc012_1` was absent from the automatically generated candidate catalog despite appearing in the official raw-field inventory; the role-override pipeline now adds a source-metadata row for such reviewed C fields rather than silently dropping them. No address is geocoded or published.

Generic parent/sibling module rows and dynamic family slots remain unmapped: a parent/sibling label alone does not establish the respondent or relative unit, and wave-specific roster structures do not support safe cross-wave harmonization. They require explicit slot/relationship audit before inclusion.

## Build results and limits

The complete metadata build passes. The Atlas currently contains 1,275 candidate E/P concepts (1,005 E-role, 279 P-role, 9 dual; 996 E-only and 270 P-only), with 6,231 E/P concept-source links. The full source crosswalk contains 6,404 rows including 173 C-role links; 6,401 rows match the site catalog and 3 are external design/eligibility metadata. The website catalog has 7,866 rows: 7,190 E/P and 676 C. Metadata co-availability pairs are 104,741 (2011), 110,082 (2013), 112,039 (2015), 89,193 (2018), and 12,598 (2020). These are field-level metadata pair counts, not sample sizes or eligible analysis counts. No models were run.

## Files

- `social_context_remainder_crosswalk_v1.csv` — reviewed 11-link crosswalk.
- `catalog_role_override_review_v1.csv` — role and privacy overrides, including address and open-text exclusions.
- `ep_candidate_pair_wave_coverage_v1.md` — current field-level co-availability counts and cautions.
- Official extracts: CHARLS 2011/2013/2015/2018 questionnaires, 2020 English questionnaire, and wave-specific codebooks under `sources_official/`.
