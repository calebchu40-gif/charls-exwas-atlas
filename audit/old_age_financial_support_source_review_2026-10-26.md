# FN097 old-age financial resource source review (2026-10-26)

## Decision

Retain `fn097_w2` as one provisional, categorical E/P candidate concept, `old_age_financial_support_source`, for 2013, 2015 and 2018. It records the respondent's stated expected or hypothetical main financial resource in old age. It is **not** a measure of current pension enrollment, pension receipt, realized family transfers, or income. The child roster (`fn098_w2` / `fn098_w2_s*`) is a separate conditional follow-up and is not folded into the single-response exposure.

## Official wording and response categories

- **2013 and 2015:** “Who do you think you can rely on financially for old-age support?” The questionnaire lists Children, Savings, Pension or retirement salary, Commercial pension insurance, and Other. Choosing Children routes to `FN098_w2` (choose all applicable children). The questionnaire marks this item for all respondents in the section. Preserve these waves' wording and their separate source files.
- **2018:** “If you are too old to work, what would be your financial resource?” The same five high-level response categories appear, with Children routing to `FN098_W2` and categories 2–5 ending the section. The interviewer note defines commercial pension insurance as life insurance directly purchased by the respondent from a commercial company with regular premiums and recurring benefits beginning at the contracted age. `FN097_W2` itself is reached through wave-specific pension screen/skip logic; do not assume its denominator is identical to 2013/2015.
- Preserve the response labels as questionnaire categories only. Codebook frequency counts and percentages are intentionally excluded from catalog output and are not analytic sample sizes.

## Harmonization limits and analysis cautions

The shared five-category menu supports a source-level crosswalk, but 2018's hypothetical wording, interviewer definition and upstream routes differ. Retain wave-specific wording, denominator and route metadata; do not claim full measurement equivalence or pool without an explicit estimand and route/denominator review. Do not infer skipped child roster fields as “no children” or interpret a non-child response as no family support. These remain catalog candidates, not approved covariates or tested model variables. Before analysis, confirm authorized respondent-file codes, special missing values, wave weights, linkage and survey design.

## Source evidence

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, FN097_w2–FN098_w2 (printed questionnaire pages 217–219 in the extraction).
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`, FN097_w2–FN098_w2 (printed questionnaire pages 189–190 in the extraction).
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`, FN097_W2–FN098_W2 and commercial-insurance interviewer note (printed page 243 in the extraction).
- `sources_official/CHARLS_2013_Codebook_extracted.txt`, FN097_w2 entry around line 27999; `sources_official/CHARLS_2015_Codebook_extracted.txt`, around line 24951; `sources_official/CHARLS_2018_Codebook_extracted.txt`, around line 65929. These were used to confirm field identity and category codes only; distribution statistics were not copied.

## Updated artifacts

`scripts/build_pension_exposure_crosswalk.py` now emits wave-specific status, response labels, route/construct caveats and source citations. The full finalization workflow propagates these fields to the E/P source crosswalk, catalog and web payload.
