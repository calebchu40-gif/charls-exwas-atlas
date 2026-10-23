# CHARLS property-sale proceeds allocation fields (2013/2015)

Reviewed 2026-10-23 against the official 2013 and 2015 CHARLS questionnaires, Codebooks, and metadata-only raw variable catalog. This review corrects the 2026-10-21 audit: that version incorrectly said no separate percentage fields had been identified. The earlier search focused on the `HA026_W2_5_[slot]_S1-S9` option-indexed fields and missed the distinct letter-coded amount variables.

The Codebooks list numeric percent fields `HA026_W2_5[a-h,j]_[slot]_` for the three property slots `1`, `2`, and `25` in both waves: 27 fields per wave and 54 total. They also list `HA026_W2_5i_[slot]_` as “Specify Usage” text: three slots in 2013 and one in 2015. The questionnaire section routes into HA026 after household property-sale questions and asks how sale proceeds were allocated. This identifies a plausible numeric exposure family, but it does not by itself establish that a particular released file has the same field encoding, that each letter-coded percentage is correctly paired with its option selector, or which households form each valid denominator.

The metadata catalog now distinguishes three source roles:

- The 54 numeric percentage fields form a separate exploratory candidate concept, `house_sale_proceeds_allocation_percent_2013_2015`, with unit `% of proceeds from sale of the indexed household residential property`.
- The 54 `S1-S9` option-indexed fields are C metadata, not E measures. The question menu is documented, but a slot index is not a verified response value label; the website withholds those labels until the selector-to-percentage linkage is confirmed.
- The four `Specify Usage` fields are C metadata only. No free-text responses are read or published.

All numeric percentage candidates remain `DO NOT ANALYZE` pending authorized-release QA of file/version identity, selector-to-category mapping, property-slot routing, special/missing codes, valid range, duplicate or overlapping property records, and the analytic denominator. Do not assume that category percentages sum to 100%, infer selection from blank values, sum across property slots, or interpret Codebook summary statistics as participant-level analysis results. Cross-wave comparability also remains unestablished.

Reproducible metadata generation is in `scripts/build_household_sale_proceeds_allocation_crosswalk.py`; selector and free-text role corrections are in `audit/catalog_role_override_review_v1.csv`. Neither the Codebook frequencies nor any participant-level values are included in the public catalog.
