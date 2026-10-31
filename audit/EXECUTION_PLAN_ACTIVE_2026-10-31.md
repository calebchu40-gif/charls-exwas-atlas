# CHARLS ExWAS Atlas — active execution plan (2026-10-31)

This plan supersedes the pre-analysis status and stop conditions in the 2026-10-29/30 snapshots. The user confirmed that the Wave 1 files were obtained under their authorized CHARLS account, authorized analysis on their private server, selected the `communityID` / no-strata with-replacement Taylor approximation, and asked work to continue without waiting for another device or reviewer. Analysis is underway and the main Wave 1 block has completed.

## Current status

- **Wave 1 primary block:** the registered K=150 household-environment and K=90 heating-route block completed: 240/240 model fits succeeded on the private server. A second run from the current code and retained authorization configuration reproduced all 240 estimates, standard errors, confidence intervals, and p-values within numerical tolerance; the comparison and run files remain private.
- **Sensitivity work:** completed three full 240-model specifications (county-prefix clustering, removal of urban adjustment, age/sex-only adjustment) and 48 uric-acid renal-adjustment fits (creatinine, self-reported kidney disease, both). These are private analyses and do not replace the registered primary family.
- **Multiplicity:** the primary family is the complete registered K=240 set. Final BY-FDR and Bonferroni values are computed over all 240 rows, not selected findings. The complete adjusted result table is now normalized and published as an aggregate payload.
- **Interpretation:** estimates use the user-selected unstratified WR Taylor approximation clustered by `communityID`; the released files do not provide the split-community PSU map or official strata. Results are within-wave weighted associations, not causal effects. This is a limitation of the available design fields, not an authorization restriction.
- **Public site:** the complete 240-row aggregate result payload is live at the GitHub Pages site. The page and JSON both returned HTTP 200 after commit `74e9d0b`; the live JSON contains one complete K=240 family. It contains estimates, 95% CIs, complete-family BY/Bonferroni values, model N and registered contrasts; it omits respondent records, IDs, cluster-support counts, paths and exact private QA.
- **2015 blood wave:** all 225 crosswalk-available household-environment × blood-phenotype models have run in the authorized server workspace, with the 2015-specific `i020=1` route for heating-source item `i021`; the full family was adjusted together. The original 2015 questionnaire differs from the 2011/2013/2018 route. A corrected source note and reproducible runner/release update are in progress. The 2015 model currently uses age and sex covariates with community-cluster WR Taylor variance because the prepared frame lacks the 2011 urban and education fields; it remains a separate wave-specific estimate.
- **Reproducibility follow-up:** the original run manifest referenced a configuration hash whose exact file was not retained. A full 240-model rerun now preserves its exact configuration binding; the reproduced results match. Use the retained rerun for schema normalization and release review.

## Work in progress

1. **Complete:** normalize the retained full240 run into the project's schema-v3 private result table. The run manifest, exact configuration, intake manifest, pair QA, scope manifest and technical-review record are hash-bound in private server storage. The configuration is explicitly marked `user_authorized_internal_analysis`.
2. **Complete:** review all 240 rows against the saved results and pair QA. All registered rows are retained; BY-FDR and Bonferroni are calculated across the complete K=240 family.
3. **Complete:** review the payload as one aggregate disclosure unit. The site receives only allowlisted fields; respondent data, local paths, cluster-support counts, exact private QA and private review records stay on the server. The page labels the variance as approximate and identifies the configured observed-blood/age-domain/complete-case target.
4. **Complete:** publish the result-browser update through GitHub Pages; the live page and JSON are confirmed HTTP 200 with all 240 rows. Continue checking interaction/filter behavior as site work proceeds.
5. **In progress:** finish the reproducibility record and aggregate release of the 2015 K=225 family, then continue with available later waves. The old 2015 route description is corrected; the previously run 2011 K90 route remains supported by the 2011 questionnaire and is unchanged.
6. After the available waves are complete, assemble the full registered atlas family, recompute atlas-wide multiplicity over that complete family, conduct the same aggregate release review, and update the site. No publication writing is included in this execution plan.

## Execution record and user-facing language

Use “user-authorized primary analysis” for the registered Wave 1 models. Do not call them “exploratory” solely because the analysis ran on the private server. Do not describe the variance approximation as the full official CHARLS design, and do not describe the cross-sectional estimates as causal. Keep analysis execution, final multi-wave atlas completion, public aggregate release, and journal peer review as separate milestones.

The public repository documents methods and workflow status and contains only the reviewed aggregate JSON. Participant-level data, the private result CSV, exact QA artifacts and review records remain on the private server.
