# 2011 community economic, housing-market, and credit-context review

## Scope and additions

Compared the unmatched 2011 Community Questionnaire Part J fields against the official questionnaire and Codebook. Added three provisional E concepts and 13 source fields:

- `community_economic_activity_and_fiscal_context`: JJ011–JJ016 (2010 agricultural/industrial revenue, village public expenditure, total village income, net investment, and per-capita net income).
- `community_housing_market_context`: JJ026–JJ030 (new/used apartment price, two-bedroom monthly rent, share of households renting out homes, and share living in market-purchased commercial housing).
- `community_formal_credit_access`: JJ031–JJ032 (2010 village-only farmer access proportion and ordinal relative borrowing difficulty).

The household/individual interpretation boundary is explicit: community informant estimates are contextual aggregates, not the CHARLS respondent's household income, wealth, home value, rent, tenure, loan, or debt. The concepts are one-wave candidates; no cross-wave repeatability is asserted and no default adjustment recommendation is made.

## Source and harmonization notes

- Questionnaire Part J, printed pp. 35–37 (PDF pp. 38–40), supplies reference years, stated units, and CAPI `V ONLY` routes for JJ011–JJ015 and JJ031–JJ032. JJ016 is phrased for village/community rather than explicitly `V ONLY`.
- JJ011–JJ012 are in 10,000 Yuan; JJ013–JJ015 in Yuan; JJ016 in Yuan. JJ026–JJ027 are Yuan/m²; JJ028 is Yuan/month; JJ029–JJ031 are percentages. These values have different constructs, denominators and reference periods and must not be combined into an invented SES score.
- JJ032 retains the five official ordered response categories as labels, with no frequencies. The English Questionnaire asks about loans from formal financial institutions while the accompanying Chinese wording names a credit cooperative (信用社); the Codebook field label is broader. The bilingual discrepancy is retained and requires release-specific interpretation before modelling.
- Questionnaire and Codebook labels were used only. Codebook frequencies, minima, maxima, and other summary statistics were not copied. Authorized-release special values, actual eligible denominators, respondent-to-community linkage, survey design/weights, and analytic use remain unresolved.

## Inventory context and limits

This is a targeted source-module addition, not a claim that all community fields or all CHARLS fields have been reviewed. Raw inventory match ratios are not completeness scores because the inventory includes IDs, interviewer identities, route flags, open-text fields, repeated roster slots and non-E/P metadata. Unmapped fields need semantic dispositions by module, not blind conversion into E/P concepts.

Sources: `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt` and `sources_official/CHARLS_2011_Codebook_extracted.txt`. Crosswalks: `audit/community_exposure_crosswalk_v1.csv` and `audit/community_exposure_value_labels_v1.csv`.

No participant-level records or Codebook descriptive statistics were accessed. No associations were estimated.
