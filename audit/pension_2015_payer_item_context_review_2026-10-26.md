# 2015 pension payer item context review (2026-10-26)

## Decision

Keep the 2015 payer-related families as separate, plan-specific candidate concepts. Their labels look similar in the Codebook, but the questionnaire places them in different item contexts and reference periods. Do not harmonize them to the generic cross-wave payer concept based only on the repeated “Who Pay for … Pension?” labels.

| Source family | Source-field structure | Catalog treatment |
|---|---|---|
| `FN074_W3_pay_[1-3]_FN074_W3s28` | One Codebook field per plan, representing the option-28 (“Other People”) response slot in the supplementary-payment follow-up. The questionnaire has a separate write-in prompt; its text is not imported. | `pension_2015_fn074_supplementary_payer_other_person_option_<plan>`; a selected response option, not free text. |
| `FN076_W3_[1-3]_s1..s28` | Multi-response payer option slots for the FN076 item, with three plan routes and roster-position slots. | `pension_2015_fn076_contribution_payer_<plan>`; keep all plan routes and option positions. Names/identities are not exposed. |
| `FN075_W3_5_[1-3]_` | Payer item reached after the question asking whether annual payments continue after the supplementary amount; it asks who paid that annual expense. | `pension_annual_contribution_payer_<plan>_2015`; do not label as the payer of the earlier supplementary payment. |
| `FN072_W3_5_[1-3]_s1..s28` | “Last Year” payer item, explicitly named as such by the Codebook and linked to its own questionnaire route. | Retain the existing `_last_year` concepts; do not merge with the other three families. |

## Evidence consulted

- CHARLS 2015 Questionnaire, printed pages 178, 180 and 181 (the official PDF is retained in `sources_official/CHARLS_2015_Questionnaire.pdf`). Page 178 locates the FN072/FN074 supplementary-payment payer follow-up. Page 181 distinguishes the FN076 item and then asks whether annual contributions continue apart from the earlier supplementary amount, followed by the FN075_W3_5 payer fields.
- CHARLS 2015 Codebook (`sources_official/CHARLS_2015_Codebook_extracted.txt`): `fn074_w3_pay_[1-3]_fn074_w3s28`, the `fn076_w3_[1-3]_s1..s28` option slots, `fn075_w3_5_[1-3]_`, and the separately labelled `fn072_w3_5_[1-3]_s1..s28` “Last Year” fields.

## Encoding and analysis boundaries

- These remain candidate exposure metadata. No response counts, respondent records, or association estimates are copied to the public atlas.
- For multi-response items, a selected slot can represent an endorsement. A blank child slot is not assumed to be an explicit “No”; authorized-release storage semantics and routed denominators still need data-level QA before modeling.
- The FN076 child-name options are roster positions, not names. The separate FN074 write-in is not imported.
- Preserve plan route, question context, and reference period. Do not collapse across plans or waves until a documented harmonization review demonstrates equivalence.
- This review changes metadata interpretation only; it does not approve covariate adjustment sets or formal model eligibility.

## Reproducibility

`scripts/build_pension_exposure_crosswalk.py` contains the source-specific rules. `tests/test_2015_pension_payer_item_context.py` verifies the separate concepts, coverage of all 84 FN076 and 84 prior-year FN072 option slots, the three FN074/FN075 plan fields, and the no-pooling caveats.
