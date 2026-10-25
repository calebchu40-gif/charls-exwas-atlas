# CHARLS 2011 community medical-insurance policy context review (2026-10-25)

## Source-mapped candidate fields

The official 2011 Community Questionnaire Part F asks which types of insurance are provided through the community (JF010, multiple select). Option 1 routes to urban-resident medical insurance follow-ups JF011–JF013. Option 2 routes to New Rural Cooperative Medical Insurance follow-ups JF014–JF016. Both options can be selected, so the two policy concepts remain separate and both routes can apply.

The urban-resident concept maps nine fields: the option selector, community start year, six year-indexed cumulative household-participation counts (2010–2005), and annual premium. The rural cooperative concept maps eleven fields: its selector, community start year, eight year-indexed cumulative household-participation counts (2010–2003), and annual premium. Household counts remain numeric/count measures with no categorical labels; source years and units are retained.

## Interpretation boundary

These are community-reported policy and aggregate participation measures. They do not identify an individual or sampled household's enrollment, subsidy, premium, benefit, or health-care use. The start year is the community program start, not a person's enrollment date. Cumulative community household counts must not be converted to rates without a verified denominator. Preserve the JF010 option-specific follow-up routes and verify each field against the authorized release before analysis.

The concepts remain candidate metadata with analysis eligibility pending. This update uses public questionnaire wording and official Codebook field labels only; no respondent data, response frequencies, sample sizes, or association estimates were used. Directory co-availability counts are metadata statistics only.

## Official sources

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, Part F, JF010–JF016; JF010 explicitly states that it is a multiple-choice item and specifies both follow-up routes.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, JF010–JF016 field entries and labels.

## Build status

Candidate crosswalk: 125 community concepts and 350 source-field mappings. The 2011 E/P metadata co-availability count is 131,185; this is not an analytic sample size. Models and analytic Ns remain zero. Public deployment is pending release verification.
