# 2014 Life History adopted-child source context review (2026-10-26)

## Official source review

Reviewed the official 2014 Life History Questionnaire page 19–20, including C017–C019a, and the corresponding Codebook fields in `DEMOGRAPHICBACKGROUNDS`. C007 distinguishes additional biological versus adopted-child routes; C017 records the number of additional adopted children; C018 starts the adopted-child loop; C019 asks adoption year; and C019a asks where each child was adopted from. The Codebook lists four C019a source slots. Questionnaire categories are: orphanage or Children Welfare Home; relative's child; friend's child; abandoned baby; other. The Codebook's descriptive frequencies are not copied or used.

## Mapping decision

Mapped `c019a_1_` through `c019a_4_` as one E-role family-context candidate, `life_history_adopted_child_source_context` (four source fields). The four slots are repeated components of C019a, not four independent observations or a number of adopted children. Existing C007/C009/C017 screen-and-count fields remain their own concept (`life_history_additional_biological_and_adopted_children`) and are not summed with roster slots. C019 exact adoption-year fields, child names, roster/order/linkage fields remain outside the published E/P map.

This is a reported characteristic of adopted children/adoption episodes, not an environmental measurement, respondent phenotype, or automatically shared exposure. Keep the adopted-child route, preserve structural missingness, do not infer a zero from an unasked field, do not derive child counts from slots, and do not publish person-level source categories, values, frequencies, or identities.

The 2014 Life History survey is retrospective and has no released survey weight. This candidate is separately browsable and not part of regular-wave pair coavailability or weighted models. Any future analysis needs licensed microdata, a clear family-context estimand, route/eligibility checks, and design and disclosure review.

## Current output state

Builder: `scripts/build_life_history_exposure_crosswalk.py`. The generated local catalog is app v189 / JSON v55, 190 concepts / 6,045 mappings (E=5,984, P=61). The exhaustive 1,920-field Demographic Backgrounds ledger has 1,193 mapped candidates, 256 C-only interview/roster/family-context metadata fields, 204 deferred sensitive relative-identity fields, 264 date/linkage/release exclusions, plus three separate join-key exclusions. This release remains local pending deployment verification. No association model has been fit.
