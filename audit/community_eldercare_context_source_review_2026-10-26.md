# 2011 community elder-care context source review (2026-10-26)

## Scope and decision

Compared the 2011 community raw-field inventory with the existing community exposure crosswalk and reviewed the matching official Community Questionnaire and Codebook sections. Added two provisional community-level E candidate concepts: `community_eldercare_center_context` (JB030–JB035 service-center availability, facilities, reported use, service options, user fee, and funding) and `community_home_eldercare_context` (JB036 household live-in-caregiver prevalence and village-only JB037–JB038 family-based service-station availability/use).

The community center question is CAPI community-only; JB030=No skips the facility follow-up items. The family-based station questions are village-only; JB037=No skips the number served. These routes and observational units remain distinct. The concepts are contextual service-access candidates, not respondent service use, care quality, individual household exposure, or approved covariates. Conditional blanks must not be recoded as zero. User-fee zero is explicitly a valid value because the questionnaire instructs zero for free service. Numeric units are retained as square meters, persons, Yuan/year, and percent of community households.

The multi-response JB033 service indicators retain their separate source slots and nominal interpretation. Official answer labels are drawn from questionnaire/Codebook text; Codebook frequencies and summary statistics are excluded. Open-text “other” fields and informant identity/name are not mapped into the E/P catalogue.

## Inventory diagnostic and its limit

The raw inventory contains 33,990 distinct wave–field-code pairs across the five interview waves when harmonized files are excluded. The existing source crosswalk matched 8,117 of those exact wave–field-code pairs before this review. This ratio is **not a completeness score**: the denominator includes IDs, interviewer/proxy metadata, string constants, roster repetitions, technical flags, non-E/P measures, and fields intentionally excluded from candidate analysis. It is useful only as a signal that completeness must be assessed by source module and semantic disposition, not by raw row totals. The current review was a targeted community-module comparison, not a disposition of every unmatched raw field.

## Sources and constraints

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, Part B, printed pp. 13–14 (PDF pp. 16–17), JB030–JB038.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, corresponding JB030–JB038 field headings and labels.
- Generated field mappings and value-label status: `audit/community_exposure_crosswalk_v1.csv`, `audit/community_exposure_value_labels_v1.csv`.

No participant records, identifiers, Codebook frequency tables, or association results were read or added. Release-specific special values, eligible denominator, linkage between the community interview and respondent records, clustered design, and analytic eligibility remain unresolved; the candidate fields remain subject to those gates.
