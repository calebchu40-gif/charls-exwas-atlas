# Wave 4/5 household-environment × doctor-diagnosed disease analysis plan

**Scope:** separate 2018 and 2020 cross-sectional association scans; no pooling across waves. Disease variables represent cumulative self-reported doctor-diagnosed history as of interview, not incidence or laboratory-confirmed disease.

## Registered exposure contrasts

All yes/no exposures use the documented `1=Yes`, `2=No` route. Fuel contrasts compare the listed category with electric fuel (code 5); do-not-cook responses are outside these contrasts and remain missing for the fuel comparisons.

| Concept | Wave 4 (2018) | Wave 5 (2020) |
|---|---|---|
| Electricity access | `i016` | `i015` |
| Running/tap water | `i017` | `i016` |
| Coal/natural-gas supply | `i019` | `i018` |
| Residential heating | `i020` | `i019` centralized heating; interpret as wave-specific wording |
| Main cooking fuel | `i022_w4`: coal, natural gas, marsh gas, LPG, crop/wood, other vs electric | `i021`: coal, natural gas, marsh gas, LPG, crop/wood, other vs electric; “other” shifts from code 7 to 8 |
| Wave-specific fuel contrast | — | Solar vs electric (code 7) |

The common set contains ten contrast terms per wave. Wave 4 has 14 registered disease outcomes; Wave 5 has 15, including a Parkinson's item with no standalone Wave 4 equivalent. This produces complete predeclared families of K=140 for Wave 4 and K=150 common terms plus K=15 solar terms (total K=165) for Wave 5, separately for each model. All hypotheses remain in K whether estimable or not.

## Outcomes

Use the route-derived prior-positive/current-routed-yes/current-routed-no disease history variables. Unresolved skips, unsupported codes, and route contradictions are missing; a blank is never recoded as No. Disease labels are harmonized by documented meaning, not slot number. Parkinson's and the Wave 4 memory-related disease wording are not treated as equivalent.

## Target and models

- Target frame: `crosssection=1`, the official cross-sectional sample flag, with positive `INDV_weight_ad2`; no automatic age-45 cutoff. Each hypothesis uses pairwise complete cases for the exposure, routed outcome, and selected model covariates.
- Primary M1: survey-weighted logistic regression, age candidate linear and quadratic, female indicator (`XRGender`: 1 male, 2 female), and current residence indicators (2018 `i000_w4_2`, 2020 `ba008`; categories 2/3/4 relative to category 1). Residence categories are the wave's city/town centre, urban-rural fringe, village, and special area labels. Valid nonreference categories are encoded 1 and all other valid categories 0; invalid residence codes are missing. The city/town centre remains the fixed reference.
- Secondary M0: survey-weighted unadjusted logistic regression.
- Sampling: `INDV_weight_ad2`, PSU `communityID`, with-replacement Taylor approximation and no fabricated strata. This is explicitly approximate because released files do not supply the official split-community PSU map or variance strata.
- Prespecified support gate: fit only when pair/model complete-case N is at least 500 and distinct PSU count is at least 30. Below-threshold hypotheses remain in the family as inestimable; do not lower the threshold after inspecting results.
- Residence categories and reference groups are fixed before fitting. If the reference category is absent in a pair/model complete-case sample or the design matrix is rank-deficient, retain the hypothesis as numerically unavailable; do not switch the reference or collapse categories after looking at support/results.
- Multiplicity: BY and Bonferroni within each complete wave-by-model family; no hypothesis is removed using p-values, effect direction, or observed support.

## Reporting and limitations

Report odds ratios and confidence intervals as cross-sectional associations. Do not imply causal effects or new disease onset. Sparse exposures, nonconvergence, low PSU support, and incomplete outcomes remain visible as non-success statuses in the private complete-family output. Exact support and coefficients remain private until separate disclosure review; no Wave 4/5 result is pre-approved for the public site.

Official source evidence is archived in `sources_official/CHARLS_2018_Codebook_extracted.txt`, `sources_official/CHARLS_2020_Codebook_extracted.txt`, the 2018/2020 questionnaires, and `audit/wave4_wave5_age_source_route_review_2026-11-01.md`.
