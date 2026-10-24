# Past-year alcohol-frequency route and harmonization review

Date: 2026-10-25. Scope: official 2011, 2013, 2015, 2018 and 2020 questionnaires, plus the 2020 Chinese flowchart. Codebook response labels were retained where already reviewed; Codebook frequency summaries were not used.

## Current-year threshold item

The 2011, 2013, 2015 and 2018 questionnaires ask DA067 whether/how often the respondent drank during the past year, with three threshold responses: more than once a month, less than once a month, or none. Responses 2 and 3 route past the current-year beverage-detail sequence to the past-history section (DA069). In Wave 5 the corresponding item is DA051; the Chinese flowchart (PDF p.30, printed p.24) routes response 1 to DA052 and responses 2/3 to the end of this alcohol sequence. A skipped or structurally absent field must not be interpreted as zero or No.

## Beverage type and detail

Wave 1–4 include a multi-select beverage-type item (DA068). The frequency questions DA072, DA074 and DA076 describe liquor, beer, and wine/rice wine separately, with type-specific routes documented in 2013–2018. The Wave 5 DA052 item asks one overall monthly frequency for any alcoholic beverage after DA051=1; its ordinal response categories resemble the older frequency categories but its measure is not beverage-specific. Do not sum older beverage categories or directly pool them with DA052 without a prespecified, validated harmonization rule.

Wave 1 has a source wording difference that affects denominator interpretation: its procedure explicitly says to ask liquor frequency DA072 when DA067=1, but does not explicitly state that a liquor choice at DA068 is required. The catalog therefore keeps the liquor-specific item label while marking the exact released-file route/eligible denominator for authorized-release QA. This must not be silently harmonized to the later selected-type route.

## Implementation and limits

The idempotent updater scripts/apply_alcohol_frequency_route_review.py adds wave-specific route and measure semantics to the behavior crosswalk and topic JSON. Regression tests protect the 2020 overall-vs-earlier beverage-specific distinction and the unresolved Wave 1 DA072 denominator. It does not read respondent records, Codebook frequency tables, or derive alcohol dose.

Sources: CHARLS_2011_Baseline_Questionnaire_official_extracted.txt:L3886-L3892, L3930-L3965; CHARLS_2013_Questionnaire_extracted.txt:L3233-L3244, L3260-L3301; CHARLS_2015_Questionnaire_extracted.txt:L2637-L2648, L2668-L2703; CHARLS_2018_Questionnaire_extracted.txt:L3102-L3117, L3147-L3179; CHARLS_2020_Questionnaire_Chinese_extracted.txt:L1395-L1406; and CHARLS_2020_Flowchart_Chinese.pdf:PDF p.30 (printed p.24). Extracted text is a search aid; the PDF flowchart page was visually checked for arrows.
