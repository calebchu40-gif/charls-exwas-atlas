# CHARLS ExWAS Atlas active work status — 2026-10-26

## Latest local state (2026-10-26, pending push)

The Part H/J/K source review batch is complete locally. The 230-step full build and 159-step finalization both completed. Final shards are E/P/C=6,092/2,116/984; 1,571 E/P concepts; 8,102 E/P concept-source mappings; 3,754 labelled E/P rows; generic pending E/P/C labels=0. The candidate-pair index has 135,445 / 141,920 / 143,137 / 105,493 / 21,630 metadata co-availability pairs for 2011/2013/2015/2018/2020; these are not analytic N. Formal models and pairwise-complete N remain 0; exact 92 analysis locks unchanged.

Part H has 75 inventory fields: 60 mapped across eight new community-history concepts plus the pre-existing primary-school concept (including the newly added JH016 year), and 15 explicitly excluded as interview logistics, informant attributes, or open-text history. Part K JK001–JK006 are mapped; JK007 is excluded from cohort E/P because it measures the community-questionnaire informant's Mandarin fluency without a verified CHARLS participant link. See [`community_part_h_source_coverage_review_2026-10-26.md`](community_part_h_source_coverage_review_2026-10-26.md) and [`community_part_k_source_coverage_review_2026-10-26.md`](community_part_k_source_coverage_review_2026-10-26.md).

Verification after the latest builder correction: all 487 tests pass. Public payload validation, do-not-analyze triage validation, JavaScript syntax, and `git diff --check` pass. No new analysis results or respondent data are included. This metadata/site update is not yet committed or deployed.

## Whole-project progress and revised remaining time (2026-10-26)

The earlier multi-month estimate incorrectly treated source-catalogue completion and the downstream result-producing ExWAS as one undifferentiated task. Progress should be reported in two scopes:

- **Interactive candidate catalogue/site:** approximately 85–90% complete. The live site, query/navigation, source-linked E/P/C catalogue, candidate-pair index, licensing limits, and automated validation already exist. This local Part H/K source batch passes 487 tests but still needs commit, deployment, and live verification. Remaining work is a bounded final coverage sweep, presentation/wording review, and handoff update; estimate 2–4 focused days, assuming no newly discovered major source family or CI/deployment failure.
- **Full NHANES-style association atlas (the whole scientific computing deliverable, without manuscript writing):** approximately 50–55% complete. Metadata discovery, harmonization and the website shell account for substantial completed work; participant-level association models and result integration remain at zero. Remaining work is to close the source inventory, freeze estimands/covariate and survey-design rules, resolve wave-specific weight/PSU/strata and blood-sample eligibility, execute/review the prespecified models and multiplicity control, then integrate approved summary results and verify the public site. Estimate 3–6 focused weeks after all required access and design inputs are available; official response or access delays are additional and cannot be estimated from repository work.

These are milestone-based subjective estimates, not percentages of variable counts. The short remaining time for the catalogue is not the same thing as time to produce a true association atlas. The immediate schedule improvement is to batch source audits by whole questionnaire module, run one full build after each coherent batch, and use targeted checks for documentation/UI-only changes; this avoids serial one-field turns and repeated full builds.

## Previous verified source-review state (2026-10-26)

Commit `62c1fa7` is pushed to `main`; GitHub Pages Deploy #252 succeeded and published the FN097 and metadata-propagation update. Validate #509 was still in progress at the last status check. This entry is now historical relative to the Part K audit in commit pending after it.

The full local rebuild completed all 230 steps in 8.1 minutes. The catalogue is E/P/C=6,034/2,116/984 rows, with 1,563 E/P candidate concepts, 8,044 E/P concept-source mappings, 3,774 explicitly labelled E/P rows, and zero generic `not yet reviewed` E/P/C value-label statuses. Metadata co-availability is a catalogue index, not analytic N; formal models and pairwise-complete N remain 0. The exact 92 analysis locks are unchanged.

This batch source-reviewed the 2013/2015/2018 `fn097_w2` old-age financial support item and fixed its questionnaire-derived response labels so they persist after a full rebuild. It also repaired propagation of 15 continuous 2011 community household-count fields and post-rebuild alcohol C metadata. Full local unittest suite: 483 passed; public payload validation, exact 92-lock validation, and JS syntax validation passed. Detailed FN097 evidence: [`old_age_financial_support_source_review_2026-10-26.md`](old_age_financial_support_source_review_2026-10-26.md). The update is in commit `62c1fa7`; Pages Deploy #252 succeeded.

## Community Part K coverage update

Audited all seven substantive items in the 2011 Community Questionnaire Part K against the official questionnaire, Codebook and metadata-only inventory. JK001–JK006 remain separately represented as one-wave community-context E candidates. JK007 measures the Mandarin fluency of the community-questionnaire informant/respondent, not an established CHARLS cohort member; it is therefore excluded from E/P concepts unless authorized person-level linkage and target identity are independently verified. Details and tests: [`community_part_k_source_coverage_review_2026-10-26.md`](community_part_k_source_coverage_review_2026-10-26.md), `tests/test_community_interviewer_observation_review.py`.

## Current public state: app v127; Pages Deploy #250 includes the economic/housing/credit batch; JJ005 local update pending

v127 (commit `7b00491`) is deployed. GitHub Validate run [`40213942542`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40213942542) and Pages Deploy run [`40213942548`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40213942548) completed successfully. The public site is verified at app v127 and pair-index v5. It contains source-reviewed 2013/2020 death and end-of-life candidate metadata, no participant-level records or computed associations.

## Mortality field review

- Added 11 source-field mappings: 2013 `Exit_Interview` (year/month of reported death, calendar selector, expectedness) and 2020 `Exit_Module` (year/month/day, calendar selector, expectedness, final-illness interval and its conditional year detail).
- Classified date, expectedness, and final-illness candidates as provisional P; the solar/lunar date selector is C metadata. The C display labels are localized in the browser catalog.
- 2013 response category labels are withheld because this pass verified official field labels but did not recheck the response-code sets. 2020 category labels are copied from official questionnaire wording, without frequencies.
- Exit-module information comes from decedent/proxy pathways. It does not define non-death as zero, an all-cohort event indicator, risk denominator, follow-up completeness, or censoring. 2013 has year/month fields; 2020 adds day. Solar/lunar calendar conversion and release-specific special/missing values require separate review before date pooling.
- 2018 cover-screen alive/dead routing was kept distinct from exit-module outcomes. No 2015 counterpart was inferred from neighboring waves.

Audit source: [`mortality_endpoint_mapping_review_2026-10-25.md`](mortality_endpoint_mapping_review_2026-10-25.md); source mappings: [`mortality_endpoint_crosswalk_v1.csv`](mortality_endpoint_crosswalk_v1.csv).

## Rebuild and current counts

The previous public v127 build completed 157 metadata-finalization steps. The current local rebuild completed 158 steps and contains E/P/C=6,034/2,116/984 rows; 1,563 E/P candidate concepts, 8,044 E/P concept-source mappings, and 3,742 explicitly labeled E/P rows. Generic `not yet reviewed` value-label rows are 0 for E/P and C. The analysis lock gate remains exactly 92 locks. The 2011 community reviews added six provisional concepts and 26 source fields across elder-care service context, local economic/fiscal context, housing-market context, and formal-credit access; see [`community_eldercare_context_source_review_2026-10-26.md`](community_eldercare_context_source_review_2026-10-26.md) and [`community_economic_housing_credit_source_review_2026-10-26.md`](community_economic_housing_credit_source_review_2026-10-26.md).

The current local pair index contains 133,741 / 141,920 / 143,137 / 105,493 / 21,630 metadata co-availability pairs for 2011/2013/2015/2018/2020. These are not participant counts, eligible analytic N, or association results. Formal association models and actual pairwise-complete N remain 0. The economic/housing/credit batch is live from Pages Deploy [#250](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40219607092); the newly mapped JJ005 machinery-origin concept and Part J inventory audit remain local pending another deployment. The earlier elder-care update was live from Pages Deploy [#249](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40217511361); the expanded economic/housing/credit update remains local pending validation and deployment. Application cache identifiers remain v127/v5 because application code did not change. The follow-up CI test fix passed Validate [#505](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40217765152).

## Verification

- Current rebuild: all 158 finalization steps completed. Full local pytest suite: 485 passed, 90 subtests passed; public payload and exact 92-lock checks pass.
- Public-site payload validator passed.
- `validate_do_not_analyze_triage.py` passed: all 92 catalog locks match the triage inventory.
- JavaScript syntax and deferred-loader checks passed; candidate pair cache key remains v5 and page entry point remains app v127.
- GitHub Pages Deploy #250 published the prior economic/housing/credit update; Validate #507 and Deploy #250 succeeded. The JJ005 update has not yet been pushed.

## Next work

Commit and publish the source-reviewed JJ005 machinery-supply-origin mapping and Part J coverage audit after full-suite validation; then continue systematic source-variable family coverage, retaining explicit mapped/excluded/unresolved dispositions. Maintain separate readiness gates for official weights, special values, linkage, and survey design; catalog availability does not imply analysis eligibility.
