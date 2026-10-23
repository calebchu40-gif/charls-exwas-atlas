# 2011 community education and context source review

Reviewed 2026-10-24 against the official 2011 Community Questionnaire and Codebook extracts. This is a metadata-only review; it uses no community or respondent answers, frequencies, or summary statistics.

## Community adult education percentages

The Part C questionnaire (printed p.16; PDF p.19) asks community informants for the exact percentage of adults in the village/community at each of six attainment levels: illiterate/semi-illiterate (JC019), primary school (JC020), junior middle school (JC021), senior high school (JC022), college (JC023), and graduate school or above (JC024). Each exact percentage has a separate `_1` field. The interviewer is instructed to use that category field only when the informant does not know the exact percentage. Therefore each paired source field is an alternate response format for the same question, not two independent measures and not values to combine without a missingness/routing review.

The questionnaire prints the complete category menus:

| Field family | Fallback brackets |
| --- | --- |
| JC019_1 | 0–20%; 20–40%; 40–60%; 60–80%; 80–100% |
| JC020_1–JC022_1 | 0–10%; 10–20%; 20–30%; 30–40%; >40% |
| JC023_1 | None; 0–1%; 1–5%; 5–10%; 10–15%; >15% |
| JC024_1 | None; 0–1%; 1–5%; 5–10%; >10% |

Codebook tables confirm response labels for the fallback fields but may omit categories with no observed responses (for example, JC021_1 category 1). The public mapping therefore follows the full questionnaire menu, omits all frequency columns, and marks the fields as conditional fallback categories. The exact-percentage fields remain continuous percentages; they are not assigned the fallback category labels.

All values are community-informant reports about adults in the community, not each sampled respondent's own education. The public directory keeps that ecological unit and the exact/fallback pairing visible. No denominator, cut-point derivation, or individual-level exposure is inferred.

## Other codebook-only community mappings closed in this review

The same questionnaire review verified 11 rows that previously had only Codebook-label evidence: JC020–JC024; JJ023–JJ024; JK001; JK003; JI001; and JB015. The newly added JC019 and six `_1` fields are covered by the education review above. JJ023 is a current average water price in Yuan/ton; JJ024 is a current average electricity price in Yuan/degree (kWh). JK001 asks whether roads pass through the village/community (Yes/No). JK003 is a community informant's ordered 1–7 road-tidiness assessment, anchored from very dirty to very tidy. JI001 asks whether any serious natural disaster occurred during the prior five years; a No response skips the conditional JI002 event detail. JB015 is village-only and asks whether the village restructured its toilet/sewer system; the Codebook's derived-variable label does not establish its construction, so its derivation remains unresolved.

These are single-wave community-context candidates. Formal analysis still requires release-level value/storage checks, the correct community/respondent linkage and denominator, and survey-design handling. They are not individual measured exposures or association results.
