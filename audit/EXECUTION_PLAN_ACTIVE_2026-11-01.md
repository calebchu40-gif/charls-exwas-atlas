# CHARLS ExWAS Atlas — active execution plan

**Updated:** 2026-11-01 (UTC)  
**Status:** The 2011, 2013, and 2015 registered association families are live as disclosure-reviewed aggregate results. Official 2018 and 2020 source packages are now verified in protected storage; prepared person tables, routed disease outcomes, and age candidates have been built and privately validated. The Wave 4/5 association families are being registered next; no Wave 4/5 association estimates have been fitted or published.

This plan supersedes earlier active-plan snapshots where their status statements conflict. It separates analysis completion, disclosure review, public aggregate release, and journal publication. User authorization for private analysis does not by itself imply disclosure clearance.

## Data handling and design

- CHARLS participant-level source and derived data, exact QA, and result tables stay in the user's protected server `private/` tree.
- Only allowlisted aggregate result fields may enter the public site after a wave-specific disclosure review. No respondent records, IDs, exact support counts, private paths, or review artifacts are public.
- The selected working variance estimator is with-replacement Taylor linearization, clustered by the available `communityID`, with no fabricated strata. The released design fields do not include the official split-community PSU map or strata; describe this as an approximation and avoid causal language for cross-sectional estimates.
- Registered hypotheses remain in their complete wave-specific multiplicity families. Do not remove pairs based on p-values or observed effect direction.

## Current verified progress

| Wave | Registered primary family | Status | Public status |
|---|---:|---|---|
| 2011 | K=240 (K=150 household environment + K=90 heating route) | Main analysis, reproducibility run, and registered sensitivity work completed; complete-family BY and Bonferroni values computed. | Aggregate family is live. |
| 2013 | K=75 household environment × anthropometry | Midpoint-age primary family, lower/upper age-bound sensitivity families, age reconciliation, contrast-level sample/PSU support audit, schema normalization, and within-wave complete-family finalization completed in protected storage. The result table passed the project result-schema validator. | Complete K=75 aggregate family is live with the approximate-variance label. |
| 2015 | K=225 household environment × blood outcomes | Registered primary family and settlement-context sensitivity completed; complete-family adjustment computed within wave. | Aggregate family is live. |
| 2018 | Disease family not yet registered | Official 2018 source package and input hashes verified; prepared table, route-aware 14-disease outcome table, row-level route QA, and source-routed age candidate have passed protected validation. Exact QA remains private. | No results. |
| 2020 | Disease family not yet registered | Official 2020 source package and input hashes verified; prepared table, route-aware 15-disease outcome table, row-level route QA, and official `XRAge` formula check have passed protected validation. Exact QA remains private. | No results. |

Exact QA and support diagnostics remain private. The 2013 finalization used an explicit internal hash-bound scope audit; this is not represented as an external scientific review. The aggregate payload contains only the existing allowlisted result fields, preserves the approximate-variance label, and keeps the three wave-specific multiplicity families separate. The 2013 aggregate family was deployed in commit `9fc2ba1`; live JSON and home-page content were verified after deployment.

## Next execution queue

1. Register wave-specific 2018/2020 disease-association families by official disease concept and the existing household-environment exposure crosswalk; specify target frame, age adjustment/domain, missingness, covariate set, and complete-family multiplicity before fitting.
2. Run and privately QA the frozen Wave 4/5 families, preserving wave-specific disease routes and design labels. Then complete cross-wave consistency, atlas-wide multiplicity, disclosure review, and release-safe aggregate updates.

## Completion criteria

The analysis milestone is complete when every available registered wave family has a frozen source/estimand/design record, reproducible complete-family output, and wave-specific QA. The public-atlas milestone additionally requires disclosure-cleared aggregates for all released waves, correct family-level multiplicity, a successful site build/deployment, and a live-site content check. Journal submission and peer review are separate work and are not included in this analysis completion estimate.
