# 2014 Life History WEALTHHISTORY full-field review (2026-10-26)

## Scope and sources

Reviewed the official 2014 Life History questionnaire sections FS012–FS013, C6–C8 and HF001–HF009 against the matching official Codebook module. This review uses questionnaire wording, routing notes, field names and labels only. Codebook distributions and participant-level values are not used. `life_history_wealth_history_full_coverage_2014_v1.csv` assigns all 440 Codebook fields exactly one disposition; the builder fails if any field is unclassified or duplicated.

## New candidate concepts

| Concept | Codebook fields | Interpretation and restrictions |
|---|---:|---|
| Inheritance receipt, source, asset/debt type, timing and reported value (FS012–FS013) | 72 | One retrospective socioeconomic-history concept, not 72 independent exposures. Up to five reported events have year, source, asset/debt type and nominal value slots. The second household respondent's questionnaire route depends on the first respondent's FS012s status and may be limited to pre-marriage events. FS012s is route metadata and excluded. No amounts, participant values, response frequencies, inflation-adjusted values or derived net-wealth score are published. |
| Relatives reported to have died for political reasons (C6) | 9 | Sensitive, respondent-attributed family history for the 1950s–1970s. Does not establish independently verified cause of death. Selector slots are not independent participants. |
| Family member/respondent labelled a rightist (C7) | 10 | Sensitive retrospective political/family context, not a verified legal finding or current status. |
| Respondent-reported Red Guard participation (C8) | 1 | Sensitive retrospective political/social-history item. Kept distinct by module plus code from same-code items elsewhere. |
| Household land expropriation (HF001–HF004) | 93 | Current-household history since that house was established, with event, year, area and compensation fields. It is not necessarily the respondent's individually owned land. Preserve conditional routes and event structure; do not sum compensation or infer No from blank loops. |
| Household home demolition (HF005–HF009) | 58 | Separate household housing-disruption history with event, year, area and compensation fields. It is not necessarily the respondent's individually owned home. Preserve conditional loops and do not aggregate amounts without a defined estimand. |

All concepts are provisional metadata candidates. Sensitive political and financial items need separate ethics/privacy/disclosure review before any participant-level analysis or public result. Questionnaire-only write-ins and all individual responses remain excluded from the public site.

## Exhaustive module disposition

| Disposition | Fields |
|---|---:|
| Mapped candidate E/P metadata | 432 |
| Excluded person/household/community linkage keys | 3 |
| Excluded respondent/interviewer/proxy metadata | 3 |
| Excluded household-route field (`fs012s`) | 1 |
| Excluded release-version field | 1 |
| **Total WEALTHHISTORY fields** | **440** |

## Reproducibility and validation

`scripts/build_life_history_exposure_crosswalk.py` creates the candidate crosswalk, public Life History JSON and complete module ledger. The tests enforce 50 concepts / 1,695 field mappings (E 1,667; P 28), the six concept-family field counts above and exactly one disposition for every Codebook field. The independent 2014 Life History directory remains separate from the regular five-wave analysis because the official special-survey release notes indicate it has no sampling weight.

