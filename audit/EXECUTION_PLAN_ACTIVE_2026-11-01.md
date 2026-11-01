# CHARLS ExWAS Atlas — active execution plan

**Updated:** 2026-11-01 (UTC)  
**Status:** Wave 1 and 2015 association families are live as reviewed aggregate results. The registered 2013 anthropometry family has been modeled and finalized privately; its disclosure review and possible aggregate release remain in progress.

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
| 2013 | K=75 household environment × anthropometry | Midpoint-age primary family, lower/upper age-bound sensitivity families, age reconciliation, contrast-level sample/PSU support audit, schema normalization, and within-wave complete-family finalization completed in protected storage. The result table passed the project result-schema validator. | Not published; wave-specific aggregate disclosure review remains next. |
| 2015 | K=225 household environment × blood outcomes | Registered primary family and settlement-context sensitivity completed; complete-family adjustment computed within wave. | Aggregate family is live. |
| 2018/2020 | Not yet registered for association execution | Official outcome-route documentation and protected derivation utility are ready. The protected workspace check found no prepared analysis tables/manifest or raw package for these waves. | No results. |

Exact coefficients, counts, and QA remain private. The 2013 finalization used an explicit internal hash-bound scope audit; this is not represented as an external scientific review. No 2013 estimates have been copied to the public repository or site.

## Next execution queue

1. Review the finalized 2013 K=75 table against its frozen scope, complete-family multiplicity record, pair-support audit, age-bound reconciliation, sparse exposure diagnostics, and release allowlist. Record a private wave-specific disclosure decision and its input hashes.
2. If the disclosure review passes, add the entire registered 2013 aggregate family to the site payload and run the existing schema, allowlist, and publication checks. Keep each wave's registered multiplicity family distinct; do not publish exact QA.
3. Recheck protected intake for authorized 2018/2020 source files. When they appear, perform metadata-only provenance/header checks first, then source and design review before derivation or association execution.
4. Complete later-wave registered families, cross-wave consistency review, full atlas multiplicity policy, and final disclosure review before declaring the multi-wave atlas complete.

## Completion criteria

The analysis milestone is complete when every available registered wave family has a frozen source/estimand/design record, reproducible complete-family output, and wave-specific QA. The public-atlas milestone additionally requires disclosure-cleared aggregates for all released waves, correct family-level multiplicity, a successful site build/deployment, and a live-site content check. Journal submission and peer review are separate work and are not included in this analysis completion estimate.
