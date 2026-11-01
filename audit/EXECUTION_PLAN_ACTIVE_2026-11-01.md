# CHARLS ExWAS Atlas — active execution plan

**Updated:** 2026-11-01 (UTC)  
**Status:** The official-guide county-stage primary analysis has completed for all five waves (complete primary family K=845). The exact output, full QA, support counts and result-bound disclosure review remain on the user's private server. The allowlisted Pages payload now carries the complete K=845 family: numerical results are shown only for rows passing the internal disclosure screen; suppressed rows remain in the family with no estimate, P/q value or sample size. Public-site validation and the deployment workflow pass. The homepage identifies 845 as registered hypotheses, not respondents or fitted models.

This plan supersedes earlier active-plan snapshots where their status statements conflict. It separates model execution, method/sensitivity QA, disclosure review, public aggregate release and journal publication. User-authorized server analysis is active; publication is limited to aggregate results screened against CHARLS terms and the project's disclosure rules.

## Analysis design and data boundary

- Follow official CHARLS wave guides, sample flags, weights and documented multistage hierarchy. The available file release does not provide the implicit variance strata, county PPS probabilities/FPC, or complete split-subcommunity assignment needed to reproduce every design component.
- The current primary variance approximation clusters the with-replacement Taylor variance at the documented county stage, derived from the first six householdID characters and validated against communityID. It is labelled approximate. The former community-only cluster runs remain method-comparison sensitivities. County is not used as a stratum.
- Use each wave's official target flag and corresponding personal or biomarker weight. Estimates remain wave-specific; no cross-wave pooled coefficient is produced.
- Keep respondent data, exact QA, cell counts, result CSVs, local paths and private hash manifests in server `private/`. Publish only the allowlisted aggregate payload after row-level disclosure review. No respondent-level material goes to GitHub, OneDrive or Pages.
- Retain every predeclared hypothesis and full multiplicity K. Never remove a contrast because of p-value, sign or effect size.

## Verified primary-analysis progress

| Wave | Registered primary K | Current status |
|---|---:|---|
| 2011 | 240 = K150 household-environment + K90 heating-route | County-stage run complete; hash-bound QA passed. |
| 2013 | 75 household-environment × anthropometry | County-stage run complete; age-bound/support reconciliation and QA passed. |
| 2015 | 225 household-environment × blood outcomes | County-stage run complete; 2015-specific heating route retained. |
| 2018 | 140 environment × cumulative doctor-diagnosis outcomes | County-stage run complete; unresolved/inestimable rows retained. |
| 2020 | 165 environment × cumulative doctor-diagnosis outcomes | County-stage run complete; unresolved/inestimable rows retained. |
| **All waves** | **845** | Global BY and Bonferroni recomputed over complete K; no effects pooled across waves. |

The all-wave result table contains 820 estimable model rows and 25 inestimable hypotheses. A private disclosure screen has bound row decisions to the exact K845 file. The public payload contains all 845 hypotheses; 136 rows have their numerical values and sample size withheld, and 709 retain aggregate estimates. The internal 10-person/10-county-PSU cell screen and N=500 model support threshold are project screens, not numerical rules issued by CHARLS. Exact counts and decisions remain private.

The complete-K845 global-BY sensitivity output is now present in the server's private QA directory. Its manifest had an invalid trailing literal escape; the original was preserved, and a versioned corrected manifest now parses and matches the result CSV's recorded SHA-256. This repairs artifact integrity only; it does not change estimates or replace the remaining sensitivity-family review.

An independent calculation from the active county-stage K845 table reproduced its full-family BY and Bonferroni fields, including the conservative p=1 treatment for non-estimable rows. The separate `allwave_primary_models_global_BY_sensitivity_private.csv` artifact has K=845 but its analysis IDs and scientific-key groupings do not reconcile with the active county-stage table. It is retained in private storage but excluded from row-level comparisons until its source lineage is reconstructed; this does not affect the independently verified correction fields in the active primary table. Corrected Wave 4/5 community-cluster sensitivity runs at commit `09e00b0` now match their county-stage primary families by the full scientific key, retain all registered rows, and pass within-family BY/Bonferroni recalculation. A follow-up compared the schema-v3 county outputs with the sensitivity outputs: coefficient estimates agree exactly; raw status-label differences are solely the two run paths' distinct labels for non-estimable rows, and all normalized estimability classes agree. Exact counts and QA remain private.

The release is at `https://calebchu40-gif.github.io/charls-exwas-atlas/`. On 2026-11-01, the all-wave payload deployed successfully and the homepage KPI was corrected from the obsolete 540 to 845 registered primary hypotheses. The CI failure on the first payload commit was a stale homepage test; the homepage and test were corrected, all 636 local unit tests passed (28 skipped by design), and the validation and Pages workflows passed at commit `a9216a6`. A live check after commit `1504288` returned HTTP 200 for the site and result payload, confirmed all 845 hypothesis IDs are unique, and confirmed every withheld row has blank estimate, SE, CI, p/q, Bonferroni and model-N fields. GitHub validation run `41281971509` passed for commit `1504288`.

## Remaining execution queue

1. **Complete:** Confirm the live K845 payload and deployment after commit `1504288`; the site and payload return HTTP 200, all 845 IDs are unique, withheld numerical fields are blank, and GitHub validation run `41281971509` passed.
2. **Complete (official release feasibility review, 2026-11-01):** the Wave 1–5 guides, design/release notes, and metadata for the released PSU, sample-information and weight files were checked for county PPS ordering/size measures/inclusion probabilities/FPC, explicit variance strata, split-community respondent mapping, and replicate weights. The reviewed release materials do not expose those inputs or prescribe a replicate variance file; therefore an SDR/replicate estimator cannot be reconstructed faithfully from the available release, and none was fabricated. Retain county-stage WR Taylor as an approximation supported by the documented county-first design, with community-cluster sensitivity; reopen only if an official design supplement containing the missing inputs is found. Details and sources are in [`official_design_variance_review_2026-11-01.md`](official_design_variance_review_2026-11-01.md).
3. Complete one versioned private result-review package: exact inputs/config/code hashes, per-wave family completeness and status counts, coefficient-range and interval checks, county/community sensitivity comparisons, age/settlement/fasting sensitivity inventory, nonconvergence and sparse-category review. Keep all exact QA private.
4. **Complete for primary K845 and Wave 4/5 community sensitivity:** independent full-family BY/Bonferroni recomputation passed; Wave 4/5 community results match county-stage results by scientific key and their sensitivity-family corrections pass. Recover provenance for the unlinked K845 sensitivity export or keep it excluded; reconcile any remaining registered sensitivity families and compare coefficients/uncertainty rather than hit counts.
5. Review interpretation wave by wave: no cross-wave causal claim, no incident-disease wording for cumulative self-reported diagnosis, no extrapolation from blood-response complete cases to the full population, and no precision claim beyond the released design variables.
6. Refresh the release audit and user-facing methods page against the exact deployed payload hash; rerun validators and the full regression suite after any changes.
7. Write a private completion ledger with the analysis, sensitivity, disclosure and deployment checkpoints. Mark the project complete only after all items above pass; keep this automation active until then or the user's explicit pause.

## Remaining-time estimate

The primary all-wave execution and first release are complete. Remaining work is results-integrity review, method/sensitivity reconciliation, final documentation and a final end-to-end deployment check; current estimate is **about 1–2 active workdays**, excluding manuscript writing and journal peer review. If a sensitivity rerun or material design discrepancy is found, the estimate will be revised based on that concrete issue.

## Completion criteria

The analysis milestone is complete when all five registered primary families and the planned sensitivity families have complete hash-bound outputs, reconciled wave-specific denominators/weights/PSUs, corrected multiplicity and private QA. The public-atlas milestone is complete when only disclosure-cleared aggregates are present, all 845 hypotheses remain represented, validation and CI pass, and the live site matches the reviewed payload. Manuscript submission and peer review are separate work.
