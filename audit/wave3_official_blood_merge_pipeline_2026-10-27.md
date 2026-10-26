# Wave 3 official blood merge pipeline review (2026-10-27)

## Purpose and scope

This implementation prepares a verified local Wave 3 person table by joining the separately released CHARLS 2015 Blood Data to a prepared Wave 3 respondent frame. It is data preparation only. It does not define an analytic cohort, fit an association model, estimate a result, or authorize public release.

## Source and design constraints

- The CHARLS 2015 data page publishes separate All Data and Blood Data artifacts with SHA-1 values. The merge runner pins those expected values and validates both before loading participant-level records.
- The existing Blood intake audit checks the separate artifact identity and the Stata header's row count/required fields without reading respondent values.
- The separate Blood release note distinguishes the overall Wave 3 interview frame, cross-sectional frame, and blood responders. It reports 13,420 blood responders overall and 13,013 cross-sectional blood responders, and describes `Blood_weight` as a cross-sectional weight with response adjustment and 99th-percentile truncation. Panel blood weights are not provided as a universal weight; construction depends on the analysis purpose.
- Accordingly, this merge retains `crosssection`, does not filter records based on an inferred code, and records explicitly that `Blood_weight` is cross-sectional only. Before a blood analysis, the analyst must establish the exact cross-sectional eligible frame/codes, target estimand, applicable blood response weight, PSU/strata/variance design support, and treatment of missing/nonresponse according to official documentation.

## Implementation safeguards

1. Requires explicit CLI `--merge` and all necessary source files in protected, non-synchronized storage.
2. Requires the exact official 2015 All Data archive and Blood artifact SHA-1s.
3. Requires the existing metadata-only intake audit to pass on the separate Blood file.
4. Requires manifest SHA-256/size records to prove the prepared base table came from that exact archive and still matches its recorded output. Legacy derived tables without this provenance must be rebuilt from the official archive first.
5. Requires complete unique respondent IDs in both inputs, all blood IDs to exist in the prepared frame, and a one-to-one left join. Row count/order and the full base frame are preserved; nonresponders retain missing blood values.
6. Writes the merged participant-level file, updated protected manifest, and aggregate QA only under the private local root. No participant-level file or result is added to the repository or Pages payload.

## Validation and present status

Five synthetic regression tests cover frame retention, the cross-sectional flag, out-of-frame IDs, duplicate IDs, required metadata, and source/output provenance checks. The full Python test suite passes (571 tests); Python compilation, CLI help, and `git diff --check` pass. No CHARLS values were used in these tests.

The current protected intake contains only the directory README for the separate 2015 Blood Data. The official Blood download artifact, Stata file, and official 2015 All Data archive were not found. Therefore this pipeline has not been run on participant data, the old prepared table remains unauthenticated for this merge, no pilot model has been fit, and formal association count remains zero.

## Next sequence when files are available

1. Verify received official files against current official listings and keep them in protected local storage.
2. Run the metadata-only Blood gate and rebuild the 2015 base table from the exact verified All Data archive if the source/output manifest does not match.
3. Run the merge, then reconcile record counts against official release documentation using the correct cross-sectional flag and response definitions; do not use the total blood row count as the analytic N.
4. Review the pilot estimand, survey design/variance variables, missingness, weights, multiple testing family, and disclosure rules against CHARLS guidance before modeling.
5. Run one predeclared 2015 cross-sectional pilot only after all gates pass. If stable and valid, expand to additional predeclared pair families and waves with wave-specific harmonization; run the public aggregate disclosure gate before adding any result to the site.

## Official references

- [CHARLS 2015 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html)
- [CHARLS 2015 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf)
