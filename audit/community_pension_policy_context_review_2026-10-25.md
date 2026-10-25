# CHARLS 2011 community pension-policy context review (2026-10-25)

## Scope

Four separate community-level metadata concepts were added from Part G of the official 2011 Community Questionnaire and cross-checked against the official Codebook: the pension subsidy for persons older than 65 (JG025–JG028), the subsidy for persons older than 80 (JG029–JG032), the New Rural Pension System (JG033–JG036), and the Old Rural Pension System (JG037–JG040). Together they add 16 source fields. The catalog preserves the wave, community/village scope, V-only flags where the questionnaire marks them, recipient unit (persons), start year, and stated monthly Yuan standard. Codebook frequencies and descriptive statistics are not copied.

These measures describe community programs and reported uptake. They do not identify an individual respondent's eligibility, enrollment, contribution, receipt, income, or exposure. They remain candidate metadata with analysis eligibility pending release-specific value, linkage, estimand, sample, and survey-design review.

## Routing and ambiguity

- JG025=No skips to JG029; JG029=No skips to JG033. Follow-up fields must not be interpreted as zero for routed-out communities.
- JG033 is marked village-only. Its No response skips directly to JG036, bypassing JG034 (start year) and JG035 (2010 recipients), although JG036 is an average monthly subsidy-standard question. The public catalog retains JG036 as its own source field and flags applicability as ambiguous; it does not infer NRPS uptake from it.
- JG037–JG040 form a separate village-only Old Rural Pension System section. Do not collapse this with NRPS or the age-specific subsidy programs.

## Official sources

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, Part G, JG025–JG040 (printed pages 29–30; PDF pages 32–33).
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, JG025–JG040 entries.

Only public questionnaire wording, source-field labels, and response-category metadata were used. No participant records, Codebook frequencies, or fitted associations were used. Public site pair counts remain metadata co-availability counts, not analytic Ns or estimates.
