# 2014 Life History offspring-context candidates: source and routing review (2026-10-26)

## Scope and source basis

Reviewed the official CHARLS 2014 Life History Questionnaire and Codebook for biological-child items C012a/C012c/C013 and adopted-child items C020a/C020c/C020b. Questionnaire pages 16–19 contain the status, schooling and attainment items and their routing. The source PDFs and extracted text are in `sources_official/CHARLS_Life_History_Questionnaire.pdf`, `sources_official/CHARLS_Life_History_Questionnaire_extracted.txt`, `sources_official/CHARLS_Life_History_codebook.pdf` and `sources_official/CHARLS_Life_History_codebook_extracted.txt`. The Codebook was used only for field identities and category labels; its descriptive response-frequency tables were not copied or used.

## Mapping decisions

| Candidate concept | Questionnaire item families | Official source fields | Rows | Interpretation boundary |
| --- | --- | --- | ---: | --- |
| Offspring highest completed education context | C012a / C020a | `c012a_*` (10 biological-child slots) and `c020a_1`–`c020a_4` | 14 | Reported child education category; not respondent education.
| Offspring current schooling level and grade context | C012c / C020c | `c012c_1`–`c012c_7` and `c020c_1`–`c020c_2` | 9 | School-route-only grade/stage; not a complete enrollment measure.
| Offspring work, school, neither, or reported deceased status context | C013 / C020b | `c013_1`–`c013_9` and `c020b_1`–`c020b_4` | 13 | Respondent-reported child status; not respondent employment or a validated mortality endpoint.
| **Total** |  |  | **36** | Family/intergenerational context only.

The slot counts above are Codebook field inventory counts, not numbers of children or counts of responses. Biological and adopted child item families stay distinct within each concept. No roster names, identities, exact dates, respondent values, response frequencies, child linkage keys, or child-level data are present in the website payload.

## Routing and missingness

For biological children, C013 routes “at work” and “neither at work nor at school” to C012a; “at school” to C012c; and “passed away” to C014 death-date follow-up. For adopted children, C020b similarly routes work/neither to C020a, school to C020c and reported deceased to C023. Therefore, an empty attainment or schooling slot can reflect questionnaire routing and cannot be interpreted as “no education,” “not enrolled,” or “no.” The schooling candidate describes schooling stage/grade as asked only on the in-school route. Death routing is documented as context only; no death-date or mortality construct is exposed here.

Education categories and grade labels retain the official category distinctions (including preschool, primary/middle/high school, vocational school, college, master's and doctoral categories). They are descriptive metadata, not ordinal scores or an assumed common scale; any future analysis must prespecify harmonization and validate codes against the authorized release.

## Atlas classification and design limits

The three concepts use the metadata catalog's `E` role to indicate an exposure/context candidate. This label does not mean environmental exposure: these are reported family/social-context variables. They are not included in the regular five-wave pair matrix, are not respondent clinical phenotypes, and are not claims of causal exposure. The official release note states that 2014 Life History has no survey weight; it remains a separately browsable special-wave catalog and cannot simply be pooled into the regular-wave weighted analysis. Any analysis would require authorized microdata, an explicit estimand, age/eligibility and linkage review, and privacy/ethics review.

## Reproducible output state

The builder is `scripts/build_life_history_exposure_crosswalk.py`. Its regenerated metadata-only JSON is `site-prototype/dist/life_history_exposures_v1.json`; the field-level crosswalk and exhaustive module ledger are `audit/life_history_exposure_crosswalk_v1.csv` and `audit/life_history_demographic_backgrounds_full_coverage_2014_v1.csv`. The local pending build contains 184 concepts / 5,915 source-field rows (E=5,854, P=61), including these 36 fields. It also dispositions all 1,920 unique DEMOGRAPHICBACKGROUNDS fields: 1,063 mapped candidates; 440 C-only interview/roster/family-context metadata; 204 sensitive relative-identity fields deferred; 210 date/linkage/release fields excluded; and 3 linkage keys excluded.

Local static assets are app v187 / JSON v53. The public website remains app v186 / JSON v52 until a separately reviewed deployment. No association model has been fit and no result is implied.
