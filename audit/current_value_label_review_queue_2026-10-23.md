# Current value-label review queue (2026-10-23)

This snapshot reads only the public, generated metadata in `site-prototype/dist/catalog_{e,p,c}.json`. It contains no respondent records or response frequencies. “Not yet reviewed” is the catalog value-label review field; it does not mean every row should receive a discrete category label, and it is separate from E/P analysis eligibility.

| Role | Catalog rows | Generic `not yet reviewed` rows |
|---|---:|---:|
| E exposure candidates | 4,723 | 0 |
| P phenotype candidates | 2,067 | 0 |
| C covariate/measurement metadata | 979 | 210 |

The current E queue contains no rows with a generic pending value-label status. The latest batch audited the final 12 fields across household expenditure, interwave work counts, rental-income status, COVID-period wage direction, occupational classification, and pandemic/work-history items. Several retain specific unresolved source or route caveats and `DO NOT ANALYZE` locks. These are field rows, not independent concepts or tests.

## Processing rule

Continue by source-backed field families. For each field, establish whether its official questionnaire and Codebook define a categorical response, a continuous amount/count/date, an open response, a routed component, or a special missing code. Add categories only when the official source supports the exact wave-field mapping; omit frequencies. For numeric/open fields, replace the generic pending state only when the source record is located and its measurement meaning can be stated. Preserve conflicting labels and existing `DO NOT ANALYZE` locks. A blank category list is not itself an error for a continuous measure.

## Next review batches

The individual income and wage batch is reviewed at source-metadata level (46 crosswalk rows); social-care, education/hukou, and final 12-field reviews are also recorded below. Completed metadata review does not prove analysis readiness. Continue checking questionnaire scope, response unit, household/person measurement level, wave comparability, routing, and Codebook storage semantics. Amount slots must not be counted as independent exposures without a construct-level rationale.

The 2018 current-home owner-relation batch is reviewed at the response-label level: one of nine fields has a complete Codebook 0/1 label set; eight show only the `0=Do Not Own` category in the extracted Codebook and are marked partial without guessing the missing category. Five adjacent current-home ownership-share fields are now identified as continuous percentages. Eight additional area, rent, value and acquisition-year fields now show their exact questionnaire units and route/coding limits; ownership area measures remain route-specific, rent zero may trigger unfolding brackets, and total/unit market-price formats are not combined. Fifteen bedroom, living-room and toilet fields across five waves are now identified as numeric counts, with residence scope, soft-check interpretation and cross-wave caveats. Eight additional dwelling-area, construction-year and 2020 move-in fields now carry units or exact wave-specific measurement meaning. Ten weekly household food/eating-out expense fields now show Yuan/week and describe own-production and banquet/wedding exclusions by wave; they remain household resource measures, not personal dietary intake. Codebook extrema are not treated as valid ranges and no frequencies were copied. See [`housing_current_owner_relation_labels_2018_v1.csv`](housing_current_owner_relation_labels_2018_v1.csv), [`housing_current_owner_relation_labels_2018_review_2026-10-23.md`](housing_current_owner_relation_labels_2018_review_2026-10-23.md), [`housing_current_owner_share_2018_review_2026-10-23.md`](housing_current_owner_share_2018_review_2026-10-23.md), [`housing_current_home_measurements_2018_review_2026-10-23.md`](housing_current_home_measurements_2018_review_2026-10-23.md), [`housing_room_count_measure_review_2026-10-23.md`](housing_room_count_measure_review_2026-10-23.md), [`housing_area_and_year_measure_review_2026-10-23.md`](housing_area_and_year_measure_review_2026-10-23.md), and [`household_food_expenditure_measure_review_2026-10-23.md`](household_food_expenditure_measure_review_2026-10-23.md). The E generic-pending count is now 578.

The five-wave food-purchaser yes/no, roster-identity selector and shared-meal-count fields are now reviewed: Yes/No labels are explicit, dynamic roster indices are not presented as fixed categories, and meal counts are household-level persons/week context with soft checks excluded from analytic cutoffs. Eight housing floor/access fields are also reviewed, including the 2020 ground/underground selector, routed floor counts and entrance-step count. Thirteen toilet type/distance fields preserve split option-specific 2011–2015 coding versus single-item 2018/2020 coding; distances remain meters and Codebook extrema are not valid-range cutoffs. DA058 in 2011/2013 now has the six ordered self-reported meals-per-day labels, recorded as behavior rather than nutrient intake. Eight kitchen/balcony counts are identified as household-level numeric built-environment measures, with soft checks excluded from thresholds. Four homestead-area fields are recorded in m², with rural-homestead definition and zero-as-possible-nonapplicable behavior preserved. Eight 2018 household property fields distinguish the new-household property count from seven per-property rent-status slots, retaining refusal and routing codes. Thirteen 2018 per-property actual/monthly market-rent fields now show Yuan/month and remain separate by amount type, route and property slot. No frequencies or Codebook extrema were copied. See [`household_food_roles_and_shared_meals_review_2026-10-23.md`](household_food_roles_and_shared_meals_review_2026-10-23.md), [`building_floor_and_entrance_access_review_2026-10-23.md`](building_floor_and_entrance_access_review_2026-10-23.md), [`toilet_type_and_distance_review_2026-10-23.md`](toilet_type_and_distance_review_2026-10-23.md), [`individual_meal_frequency_review_2026-10-23.md`](individual_meal_frequency_review_2026-10-23.md), [`housing_kitchen_balcony_counts_review_2026-10-23.md`](housing_kitchen_balcony_counts_review_2026-10-23.md), [`homestead_land_area_review_2026-10-23.md`](homestead_land_area_review_2026-10-23.md), [`household_property_count_and_rent_status_2018_review_2026-10-23.md`](household_property_count_and_rent_status_2018_review_2026-10-23.md), and [`property_actual_and_market_rent_2018_review_2026-10-23.md`](property_actual_and_market_rent_2018_review_2026-10-23.md). The E generic-pending count is now 496.

This queue snapshot is descriptive and does not change the current formal model count (0) or overall result-atlas completion estimate (25%–30%).


2026-10-23 household property value correction: official 2018 HA004 uses measure-first, slot-second variable names. All 12 amount fields (seven total values in 10,000 Yuan and five unit-area values in 1,000 Yuan/square metre) are now present with the correct concept and unit; seven same-slot format selectors moved from E to C and show only `1=Total Value; 2=Unit Value`. The full metadata pipeline and 108 tests passed. E generic pending is 496 (housing 40); formal models remain 0. See [`household_property_value_2018_slot_unit_review_2026-10-23.md`](household_property_value_2018_slot_unit_review_2026-10-23.md).


2026-10-23 housing numeric review: the remaining 40 pending E rows in the housing/property domain are now reviewed as numeric amounts across 2011, 2013, and 2015. Official questionnaires identify Yuan, 10,000 Yuan, or 1,000 Yuan/square metre units by measure; continuous measures receive no invented category labels. Interviewer soft checks are not analytic thresholds, and authorized-release storage scale/special codes/bracket linkage remain pending. E generic pending is 456; housing and food/household-environment generic pending are both 0. See [`housing_numeric_value_metadata_review_2026-10-23.md`](housing_numeric_value_metadata_review_2026-10-23.md).


2026-10-23 parent-visit update: 33 wave-specific parent-contact fields (2011/2013/2015/2018) now carry official field-level ordinal category labels in the candidate catalogue and site. Twenty-seven fields list codes 1–10; six show only the categories present in their field-specific Codebook extract. Numeric frequencies and roster names are excluded, partial categories are not imputed, and categories are not treated as equally spaced. The E generic-pending count is now 369; P remains 0 and C remains 329.


2026-10-23 DA056 option-status update: 41 2011–2015 social-activity and internet-device fields now show that the Codebook identifies the selected option, while participant-level value coding, unselected-option representation, and denominator remain unresolved. The site intentionally leaves response-value labels empty and states that absence cannot be interpreted as “No.” E generic pending is now 328; C is 328; P remains 0. See [`social_code_value_review_v1.md`](social_code_value_review_v1.md).


2026-10-23 household-member amount update: 124 official-source matched roster amount fields (2011 n=80; 2013 n=24; 2015 n=20) now display Yuan/year or Yuan/month and wave-specific roster/cross-wave caveats. No Codebook summary values or categories copied; no slot summation or respondent attribution. E generic pending is now 204, C 328, P 0. See [`household_member_income_amount_review_2011_2015_2026-10-23.md`](household_member_income_amount_review_2011_2015_2026-10-23.md).

2026-10-23 household expenditure review: 53 fields across 2011–2020 classified by household scope, period, and official units; four self-production indicators carry Codebook-supported Yes/No labels. No frequencies or extrema copied. The current generic-pending queue is E 151, P 0, C 328. The remaining E subgroups and review rules are listed above; see [`household_expenditure_metadata_review_2011_2020_2026-10-23.md`](household_expenditure_metadata_review_2011_2020_2026-10-23.md).

Latest 2026-10-23 rollup after household expenditure review: E generic pending 151, P 0, C 328; E/P nonempty official/reviewed value-label texts 3,212 rows across 3,186 wave-fields. Parent-visit categories (33 fields: 27 complete, 6 partial), DA056 option-storage cautions (41 fields with no fabricated response labels), household-member amount measurement states (124 fields, no categories), and household expenditure metadata (53 fields) are reflected in the generated catalog.

2026-10-23 individual transfer-income review: 50 source-option fields checked across five waves. 2011–2015 option identity is documented but the unselected state remains unresolved; no No labels were inferred. In 2018/2020, explicit Codebook labels `0=No` and the option-specific code `=Yes` are shown for 20 fields; frequencies are omitted. E generic pending is now 101, P 0, C 328. See [`individual_transfer_income_source_review_2011_2020_2026-10-23.md`](individual_transfer_income_source_review_2011_2020_2026-10-23.md).

2026-10-23 pension interval endpoint review: 16 lower/upper bracket fields across 2011/2013/2015 are identified as conditional amount bounds, not point estimates or response categories. The 2013 Codebook's string type and 2015's summary-only evidence are distinguished; no extrema or frequencies copied. Latest queue: E 85, P 0, C 328. E/P nonempty reviewed/official value-label texts: 3,232 rows across 3,206 wave-fields. See [`pension_interval_endpoint_review_2011_2015_2026-10-23.md`](pension_interval_endpoint_review_2011_2015_2026-10-23.md).


2026-10-23 individual income/wage review: official wave-specific wage units, asset indicator response labels, inheritance checkbox limits, fraud measures and 2020 wage-deduction special codes were added to the candidate metadata. No Codebook frequencies or descriptive extrema were copied. E generic pending is now 12; P 0, C 328. See [`personal_income_wage_metadata_review_2011_2020_2026-10-23.md`](personal_income_wage_metadata_review_2011_2020_2026-10-23.md).


Latest rollup after individual income/wage review: E generic pending 40, P 0, C 328; E/P nonempty official/reviewed label texts 3,316 rows across 3,290 wave-fields. The 46-row personal-income crosswalk review includes both categorized and continuous/count metadata states; 89 analysis locks remain unchanged.


2026-10-23 social-care metadata review: 14 2011/2013 caregiver/helper fields were checked against the questionnaires and Codebooks. Thirteen helper-option fields retain blank labels because unselected storage/denominators are unresolved; one helper-days field is recorded as a routed continuous count. No categories or frequencies were inferred. E generic pending is now 26; P 0, C 328. See [`social_care_caregiver_metadata_review_2011_2013_2026-10-23.md`](social_care_caregiver_metadata_review_2011_2013_2026-10-23.md).


2026-10-23 education/hukou response-label review: 14 wave-field mappings across 2011–2020 now show official wave-specific education and hukou categories, including the special 2013 Z-prefixed Codebook aliases and 2013/2015 `12=No change` education option. Frequencies were omitted. E generic pending is now 12; P 0, C 328. See [`education_hukou_value_label_review_2011_2020_2026-10-23.md`](education_hukou_value_label_review_2011_2020_2026-10-23.md).


Latest rollup after education/hukou review: E generic pending 12, P 0, C 328; E/P nonempty official/reviewed labels 3,274 rows. The reviewed 2013 hukou/education fields retain a Z-prefixed Codebook alias caution; 89 analysis locks are unchanged.


## Latest rollup: 2026-10-23 final E review

The generated E catalogue has 4,723 field-wave rows and zero generic `not yet reviewed` value-label states. The P catalogue remains at zero generic pending; C retains 257 generic pending rows. E/P nonempty reviewed/official label text totals 3,279 rows across 3,253 distinct wave-fields. Continuous amounts, counts, classification codes and dates may correctly have no categorical labels. The final 12-field review preserves all existing `DO NOT ANALYZE` locks and questionnaire/Codebook conflicts. Formal association models remain 0. See [`final_pending_field_review_2026-10-23.md`](final_pending_field_review_2026-10-23.md).


## Latest C metadata batch: prior-wave history and routing

The 41 prior-interview response-history/routing flags and 14 prior-wave diagnosis-time answer-history flags were checked against their wave-specific official Codebooks. They remain C-only metadata; no response categories were inferred, and empty slots are not interpreted as “No.” This resolves 55 C rows with a specific metadata/source status. The latest generated C catalogue now has 257 generic pending rows. Review record: [`prior_wave_history_routing_metadata_review_2026-10-23.md`](prior_wave_history_routing_metadata_review_2026-10-23.md).


## Latest C metadata batch: disease-slot placeholders and inactive legacy fields

A further 24 C-only fields were reviewed against the official Codebooks: 15 unsupported prior-wave disease slots, five unlisted disease-index placeholders and four inactive 2015 household lending/debt fields. No response categories were inferred; unsupported disease blanks are not “No.” The latest C generic-pending count is 233. See [`c_placeholder_legacy_field_review_2026-10-23.md`](c_placeholder_legacy_field_review_2026-10-23.md).


## Latest C metadata batch: measurement protocol and selectors

An additional 23 C fields were checked: debt unfolding-bracket protocol, household/person response selectors, interview assistance, chair setup, financial-respondent source, pandemic work-module selection and one unresolved questionnaire/Codebook conflict. They remain measurement/routing metadata; the conflict stays locked. C generic pending is now 210, all within the broad demographic/design/socioeconomic covariate-candidate family, so the remaining queue needs causal/model-role review rather than category-label transcription. See [`c_measurement_protocol_metadata_review_2026-10-23.md`](c_measurement_protocol_metadata_review_2026-10-23.md).
