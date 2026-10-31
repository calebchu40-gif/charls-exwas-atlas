# CHARLS ExWAS Atlas — active execution plan (2026-10-31)

This plan supersedes the pre-analysis status and stop conditions in the 2026-10-29/30 snapshots. The user confirmed that the Wave 1 files were obtained under their authorized CHARLS account, authorized analysis on their private server, selected the `communityID` / no-strata with-replacement Taylor approximation, and asked work to continue without waiting for another device or reviewer. Analysis is underway and the main Wave 1 block has completed.

## Current status

- **Wave 1 primary block:** the registered K=150 household-environment and K=90 heating-route block completed: 240/240 model fits succeeded on the private server. A second run from the current code and retained authorization configuration reproduced all 240 estimates, standard errors, confidence intervals, and p-values within numerical tolerance; the comparison and run files remain private.
- **Sensitivity work:** completed three full 240-model specifications (county-prefix clustering, removal of urban adjustment, age/sex-only adjustment) and 48 uric-acid renal-adjustment fits (creatinine, self-reported kidney disease, both). These are private analyses and do not replace the registered primary family.
- **Multiplicity:** the primary family is the complete registered K=240 set. Final BY-FDR and Bonferroni values are computed over all 240 rows, not selected findings. Exact values and pair support remain on the server until the aggregate table is normalized and reviewed.
- **Interpretation:** estimates use the user-selected unstratified WR Taylor approximation clustered by `communityID`; the released files do not provide the split-community PSU map or official strata. Results are within-wave weighted associations, not causal effects. This is a limitation of the available design fields, not an authorization restriction.
- **Public site:** source/catalog pages remain online. The homepage has been updated to report 240 completed Wave 1 models. The browser result table is still empty because the normalized 240-row aggregate payload has not yet been generated and deployed. No user action or second device is needed for the remaining work.
- **Reproducibility follow-up:** the original run manifest referenced a configuration hash whose exact file was not retained. A full 240-model rerun now preserves its exact configuration binding; the reproduced results match. Use the retained rerun for schema normalization and release review.

## Work in progress

1. Normalize the retained full240 run into the project's schema-v3 private result table. Keep the exact run manifest, configuration, intake manifest, pair QA, and scope manifest hash-bound in the private server directory. The configuration is explicitly marked `user_authorized_internal_analysis`; do not relabel it as externally reviewed or as a separate human approval.
2. Complete the 240-row technical estimability review from the saved results and pair QA. Preserve all registered rows, including any non-success status if one appears. Recompute BY-FDR and Bonferroni across the complete K=240 family.
3. Review the proposed browser payload as an aggregate disclosure unit. Publish only the allowlisted fields; keep respondent data, raw files, local paths, exact private QA, and private review records on the server. Label the variance as approximate and identify the target as the observed positive-bloodweight sample within the configured age domain and pair-specific complete cases.
4. Update the result browser with the complete Wave 1 family, run the site's strict payload validator through the existing GitHub workflow, wait for Pages deployment, and verify the live page and JSON URL.
5. Continue with available later-wave inputs, one wave at a time: check the protected intake manifest, then verify each wave's source, frame/age eligibility, weight, PSU/variance, measurement compatibility and registered family before fitting. Keep wave-specific estimates separate unless comparability has been demonstrated.
6. After the available waves are complete, assemble the full registered atlas family, recompute atlas-wide multiplicity over that complete family, conduct the same aggregate release review, and update the site. No publication writing is included in this execution plan.

## Execution record and user-facing language

Use “user-authorized primary analysis” for the registered Wave 1 models. Do not call them “exploratory” solely because the analysis ran on the private server. Do not describe the variance approximation as the full official CHARLS design, and do not describe the cross-sectional estimates as causal. Keep analysis execution, final multi-wave atlas completion, public aggregate release, and journal peer review as separate milestones.

The public repository may document methods and workflow status. It may receive only the site's reviewed aggregate JSON; participant-level data, the private result CSV, exact QA artifacts and review records remain on the private server.
