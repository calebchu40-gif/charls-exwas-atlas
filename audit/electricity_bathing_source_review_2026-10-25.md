# Household electricity and bathing-facility source review

Reviewed CHARLS household housing items against the wave-specific official questionnaires and Codebooks. This is a metadata review only; no respondent records, observed values, Codebook frequencies, or associations were accessed.

Electricity availability is mapped where a corresponding housing field exists in the current source catalogue: residence electricity in 2011 (`I016`), 2013 (`I016`), and 2018 (`I016`), plus the Household Financial Respondent's house in 2020 (`I015`). Each is a Yes/No household or residence characteristic. It does not measure reliability, duration, consumption, or an individual exposure dose. The current food/housing crosswalk has no 2015 electricity row, so the reviewed questionnaire wording was not used to invent one.

The in-house shower/bath item is represented in 2011, 2013, 2015, and 2018 as `I018`, and in 2020 as `I017`. The response categories distinguish supplied hot water, a household-installed water heater, and no facility; 2020 uses “Unified hot water supply” and “Water heater.” Categories are nominal and must retain wave-specific labels. They do not measure bathing behavior, hygiene, water quality, or personal exposure.

The site and source index now show the official-questionnaire/Codebook review and the remaining limits on special-value storage, eligible denominators, missingness, household-person linkage, and cross-wave equivalence. Household attributes must not be assigned to individuals without an explicit, justified linkage. No structural routing or missing value should be recoded as “No.” Generic pending/under-review statuses in the housing crosswalk fell from 32 to 23.

Reproduction: `python scripts/apply_electricity_bathing_source_review.py`. Regression checks are in `tests/test_electricity_bathing_source_review.py`.
