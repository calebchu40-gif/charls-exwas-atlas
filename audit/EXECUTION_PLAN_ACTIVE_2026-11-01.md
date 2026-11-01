# CHARLS ExWAS Atlas — active execution plan

**Updated:** 2026-11-01 (UTC)  
**Status:** Five-wave association runs exist in private storage (K=845 registered primary hypotheses; 820 coefficient rows were estimable under the earlier community-cluster approximation and 25 were retained as unavailable). On 2026-11-01 the user directed that the analysis follow official CHARLS sampling and weighting documentation. Those runs remain private historical comparisons, not the new primary results. Official-source review and a synthetic county-key implementation check are complete; the analysis runners are being converted to the documented county stage with community-only results retained as sensitivity. Three earlier aggregate families remain on Pages with their approximate-variance labels; no replacement results will be published before rerun and QA.

This plan supersedes earlier active-plan snapshots where their status statements conflict. It separates analysis completion, disclosure review, public aggregate release, and journal publication. User authorization for private analysis does not by itself imply disclosure clearance.

## Data handling and design

- CHARLS participant-level source and derived data, exact QA, and result tables stay in the user's protected server `private/` tree.
- Only allowlisted aggregate result fields may enter the public site after a wave-specific disclosure review. No respondent records, IDs, exact support counts, private paths, or review artifacts are public.
- The new governing order is: official CHARLS wave guide, official sampling/weight construction notes, official released design fields, then a survey estimator that matches those documented stages. The prior `communityID` with-replacement Taylor setup will be used only as a historical comparison unless the design audit independently establishes it as the documented implementation.
- CHARLS describes a multistage baseline sample: county-level PPS selection after implicit stratification/sorting, followed by three community/neighborhood PSUs per county; 30 large communities were split into sub-neighborhood PSUs. The Wave 1/2 PSU tables identify parent communities and context fields, and the Wave 4/5 guides state the PSU information is the same as earlier waves. No explicit variance-stratum key, split-subcommunity respondent key, or replicate weights appeared in inspected design tables. The 2011 guide documents county/community positions in respondent IDs, so an ID-derived county key is now a source-supported candidate for validation as a sampling-stage identifier, never a stratum. Wave-specific weights and sample flags remain tied to their official target populations. `urban_nbs`/`areatype` will not be treated as complete design strata without official support.
- Registered hypotheses remain in their complete wave-specific multiplicity families. Do not remove pairs based on p-values or observed effect direction.

## Current verified progress

| Wave | Registered primary family | Status | Public status |
|---|---:|---|---|
| 2011 | K=240 (K=150 household environment + K=90 heating route) | Historical community-cluster result is retained as sensitivity; county-stage rerun is queued. | Existing aggregate remains labeled approximate; no new release. |
| 2013 | K=75 household environment × anthropometry | Historical community-cluster and age-bound sensitivities retained; county-stage reruns are queued. | Existing aggregate remains labeled approximate; no new release. |
| 2015 | K=225 household environment × blood outcomes | Historical community-cluster and settlement-context sensitivity retained; county-stage reruns are queued. | Existing aggregate remains labeled approximate; no new release. |
| 2018 | K=140 | Historical community-cluster primary and secondary runs retained; county-stage rerun is queued. | No results published. |
| 2020 | K=165 | Historical community-cluster primary and secondary runs retained; county-stage rerun is queued. | No results published. |

Exact QA and support diagnostics remain private. The 2013 finalization used an explicit internal hash-bound scope audit; this is not represented as an external scientific review. The aggregate payload contains only the existing allowlisted result fields, preserves the approximate-variance label, and keeps the three wave-specific multiplicity families separate. The 2013 aggregate family was deployed in commit `9fc2ba1`; live JSON and home-page content were verified after deployment.

## Next execution queue

1. Continue the source inventory in [`official_design_variance_review_2026-11-01.md`](official_design_variance_review_2026-11-01.md): re-read official CHARLS guides for all waves and extract the exact documented target frame, weight, sample flags, PSU stages, split-community treatment and any variance instruction. The NHANES paper/repository may inform reproducibility/software structure only; do not transplant NHANES sampling formulas to CHARLS.
2. The householdID county/community segments are validated against the protected person tables for all five waves. Continue searching official codebooks for a split-subcommunity assignment, released stratum, and PPS/FPC field.
3. The server synthetic trial confirms the documented householdID county key accepts valid mappings and rejects inconsistent household/community mappings. A separate R `survey` mechanics check confirmed that `ids=~county+community` without FPC uses the first-stage cluster for variance. These checks validate implementation behavior only. Freeze exact wave-specific target flags, weights and county-stage WR Taylor settings; retain earlier community-only runs as sensitivity.
4. Rerun the five registered primary families using the official weights/sample flags and county-stage variance setting. Reconcile all 845 hypotheses, unavailable fits, variance estimates, target populations and family-level multiplicity. Compare against prior community-cluster results, and retain all files privately.
5. Reassess public results under the official-design run. Keep the existing approximate-labeled site content clearly identified as historical until the replacement families pass full review; publish only complete, disclosure-cleared families and verify deployment.
6. Write the final completion record with official sources, exact design implementation, rerun totals, sensitivity inventory, release state and live-site hash.

## Remaining-time estimate

The previous 2–4 day estimate assumed the variance setup remained fixed. The methods reset adds a source/design audit and a full rerun. Estimate **3–6 active workdays** if the needed official design fields are present in the downloaded files; add time if they are not immediately traceable or if the site needs a revised release flow. Computation is expected to be short; source reconciliation, design implementation and wave-by-wave validation are the time drivers. Manuscript writing and journal peer review are outside this estimate.

## Completion criteria

The analysis milestone is complete when every available registered wave family has a frozen source/estimand/design record, reproducible complete-family output, and wave-specific QA. The public-atlas milestone additionally requires disclosure-cleared aggregates for all released waves, correct family-level multiplicity, a successful site build/deployment, and a live-site content check. Journal submission and peer review are separate work and are not included in this analysis completion estimate.
