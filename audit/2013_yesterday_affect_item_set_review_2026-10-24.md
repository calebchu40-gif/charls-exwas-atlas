# CHARLS 2013 yesterday-affect item set review

Review date: 2026-10-24. This review uses the official 2013 questionnaire and Codebook only. No respondent-level records or Codebook frequency tables were used to define the catalogue.

## Scope and mapping

The questionnaire places WB05–WB15 under the prompt asking how the respondent felt yesterday and applies the same five response categories to each item: 1=Not at all, 2=A little, 3=Somewhat, 4=Quite a bit, 5=Very. The eleven items are frustrated (WB05), sad (WB06), enthusiastic (WB07), lonely (WB08), content (WB09), worried (WB10), bored (WB11), happy (WB12), angry (WB13), tired (WB14), and stressed (WB15).

WB06 and WB08 were already present as yesterday-specific outcome candidates. Nine missing items have now been added individually to `audit/health_symptom_variable_mapping_v1.csv` and the symptom browser. No item is reverse-coded, summed, or represented as a validated multi-item mood scale. CES-D items use a different recall period and response format and remain separate.

## Interpretation limits

- These are single-item, previous-day affect ratings. A common response card does not establish that the eleven items form one scale or that a higher value has equivalent meaning across positive- and negative-valence items.
- The item routing, eligible denominator, proxy-response eligibility, and release-specific missing values must be checked in the authorized released dataset before analysis. Codebook frequency tables are not project sample sizes.
- WB03/WB04 sleep clock-time and WB05–WB15 affect all refer to yesterday. Their same-day association has no demonstrated time ordering and cannot be presented as a causal sleep effect.
- WB08 also has an explicitly reviewed E role as a subjective loneliness candidate. The pair explorer omits same-concept E–P self-pairs; the loneliness item must never be tested against itself or included in an outcome score that contains the same item.

## Sources and reproduction

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, Health Status and Functioning, WB03–WB16 block.
- `sources_official/CHARLS_2013_Codebook_extracted.txt`, WB05–WB15 item response labels.
- `scripts/build_health_symptom_crosswalk.py` creates the individual P mappings; `scripts/enrich_outcome_value_labels.py` adds the reviewed item labels without Codebook frequencies.
- Run `python scripts/build_ep_atlas_metadata.py --finalize-only` to propagate changes through the catalogue and website assets.
