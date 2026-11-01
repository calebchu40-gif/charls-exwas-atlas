# CHARLS ExWAS Atlas — active execution plan

**Updated:** 2026-11-01 (UTC)  
**Status:** Primary association families for all five available waves (2011, 2013, 2015, 2018, 2020) have been run on the private server. Core primary family size is K=845; 820 rows yielded estimates and 25 remain numerically unavailable/inestimable, retained in their registered families. The 2011/2013/2015 disclosure-reviewed aggregate families are live. Wave 4/5 complete-family QA and a conservative pair-cell/community disclosure screen are complete; no Wave 4/5 estimates have been published.

This plan supersedes earlier active-plan snapshots where their status statements conflict. It separates analysis completion, disclosure review, public aggregate release, and journal publication. User authorization for private analysis does not by itself imply disclosure clearance.

## Data handling and design

- CHARLS participant-level source and derived data, exact QA, and result tables stay in the user's protected server `private/` tree.
- Only allowlisted aggregate result fields may enter the public site after a wave-specific disclosure review. No respondent records, IDs, exact support counts, private paths, or review artifacts are public.
- The selected working variance estimator is with-replacement Taylor linearization, clustered by the available `communityID`, with no fabricated strata. The released design fields do not include the official split-community PSU map or strata; describe this as an approximation and avoid causal language for cross-sectional estimates.
- This is the user's chosen working method, not the only possible method. CHARLS's official sample description is multistage: county units were ordered/implicitly stratified and sampled by systematic PPS, then community/neighborhood PSUs were sampled within county; 30 large communities were split into sub-neighborhood PSUs. Metadata review of the released Wave 1/2 `PSU.dta` found the parent `communityID` map and geography/type labels, but no explicit variance-stratum key, respondent-level split-subcommunity PSU key, or replicate-weight set. The public `urban_nbs`/`areatype` fields are context classifications and will not be promoted to invented strata.
- Registered hypotheses remain in their complete wave-specific multiplicity families. Do not remove pairs based on p-values or observed effect direction.

## Current verified progress

| Wave | Registered primary family | Status | Public status |
|---|---:|---|---|
| 2011 | K=240 (K=150 household environment + K=90 heating route) | Main analysis, reproducibility run, and registered sensitivity work completed; complete-family BY and Bonferroni values computed. | Aggregate family is live. |
| 2013 | K=75 household environment × anthropometry | Midpoint-age primary family, lower/upper age-bound sensitivity families, age reconciliation, contrast-level sample/PSU support audit, schema normalization, and within-wave complete-family finalization completed in protected storage. The result table passed the project result-schema validator. | Complete K=75 aggregate family is live with the approximate-variance label. |
| 2015 | K=225 household environment × blood outcomes | Registered primary family and settlement-context sensitivity completed; complete-family adjustment computed within wave. | Aggregate family is live. |
| 2018 | K=140 | Primary age/sex/residence and secondary unadjusted families run; full-family BY/Bonferroni, status, support, and hash checks passed. Pair-cell/community disclosure screen completed; exact estimates and QA remain private. | No results published pending whole-family disclosure decision. |
| 2020 | K=165 | Primary age/sex/residence and secondary unadjusted families run; full-family BY/Bonferroni, status, support, and hash checks passed. Pair-cell/community disclosure screen completed; exact estimates and QA remain private. | No results published pending whole-family disclosure decision. |

Exact QA and support diagnostics remain private. The 2013 finalization used an explicit internal hash-bound scope audit; this is not represented as an external scientific review. The aggregate payload contains only the existing allowlisted result fields, preserves the approximate-variance label, and keeps the three wave-specific multiplicity families separate. The 2013 aggregate family was deployed in commit `9fc2ba1`; live JSON and home-page content were verified after deployment.

## Next execution queue

1. Add a same-model variance sensitivity for 2018/2020 comparing the selected `communityID` clustering with the already-used six-digit county-prefix clustering proxy; compare standard errors/intervals and resulting family adjustments without treating either proxy as automatically correct or selecting by p-value. This measures how much the inference depends on cluster level.
2. Complete a cross-wave primary-result audit: confirm each finalized table is bound to its source, frozen plan and code commit; compare wave-specific versus global-BY sensitivity without pooling effects or selecting hypotheses.
3. Finish Wave 4/5 methods and disclosure review. The protected cell screen flags some contrasts for suppression/aggregation review. The existing publisher is whole-family fail-closed, so do not publish a partial family or weaken the disclosure screen to force a release. Decide whether a safe full-family aggregate is possible; otherwise retain those two families privately.
4. If release criteria pass, convert both full K families to the public schema, generate hash-bound row-level disclosure decisions, validate the payload and repository boundary, deploy, and verify the live site. If they do not pass, document the private-only disposition and keep the site unchanged.
5. Write a concise completion record with the five-wave model counts, unavailable rows, variance-method comparison, private sensitivity inventory, public release status, and final repository/live-site hashes.

## Remaining-time estimate

The model runs are complete; remaining work is review, safe normalization/release, and final reconciliation rather than large-scale computation. Estimate **1–2 active workdays** to finish the private cross-wave review and disposition, plus **up to 1–2 active workdays** for a safe site update and live verification if the Wave 4/5 families pass whole-family disclosure review. Thus the remaining analysis-and-atlas milestone is about **2–4 active workdays**. If either family cannot be safely released under the current complete-family policy, analysis can still be completed in that window, while the public site will correctly remain at three waves. Manuscript writing and journal peer review are outside this estimate.

## Completion criteria

The analysis milestone is complete when every available registered wave family has a frozen source/estimand/design record, reproducible complete-family output, and wave-specific QA. The public-atlas milestone additionally requires disclosure-cleared aggregates for all released waves, correct family-level multiplicity, a successful site build/deployment, and a live-site content check. Journal submission and peer review are separate work and are not included in this analysis completion estimate.
