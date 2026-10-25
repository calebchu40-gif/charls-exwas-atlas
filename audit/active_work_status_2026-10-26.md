# CHARLS ExWAS Atlas active work status — 2026-10-26

## Latest local state (2026-10-26; Part C commit 4b257aa is live, Part A JA042 update pending)

The 2011 Community Questionnaire Part C population-source review added 24 mappings across five provisional community-context E concepts; JC014/JC016 open-text group names and JC026 community-informant role remain C-only metadata. The follow-up Part A JA042 review added 12 candidate mappings across six leadership-profile concepts; the fifth age/tenure slots remain C-only because the questionnaire names only four positions. No respondent text, respondent records, Codebook frequencies, or association results were used. Details: [`community_part_c_population_source_coverage_review_2026-10-26.md`](community_part_c_population_source_coverage_review_2026-10-26.md) and [`community_part_a_leadership_profile_source_review_2026-10-26.md`](community_part_a_leadership_profile_source_review_2026-10-26.md).

Full metadata finalization completed 159/159 steps in 7.6 minutes. Current shards: E/P/C=6,128/2,116/989; E/P concepts=1,582 (E=1,276, P=331, including dual-role concepts); E/P concept-source mappings=8,138; C catalog rows=989. Metadata co-availability pairs are 137,788 / 141,920 / 143,137 / 105,493 / 21,630 for 2011/2013/2015/2018/2020. They are not analytic sample sizes. Formal association models and pairwise-complete analytic N remain 0; the exact 92 analysis locks are unchanged.

Full local unittest suite: 494 tests pass after the Part A update and questionnaire-derived category synchronization. Public-payload validation, exact 92-lock validation, JavaScript syntax, and `git diff --check` pass. Commit `4b257aa` is pushed to `main`. Part C live Pages deployment is verified at app v128: the homepage serves `app.js?v=128`, the E shard has 6,116 rows, and `community_exposures_v1.json` includes `community_population_hukou_profile`. The current JA042 output changes the app bundle and is not yet deployed; local public-payload, exact 92-lock, JS syntax, and diff checks are being completed before push. The public Actions API returned HTTP 403 rate-limit exceeded, so the run record itself was not independently checked.

## Whole-project progress and remaining work

The candidate metadata catalogue and interactive prototype are approximately 85–90% complete; remaining catalogue work is final module-coverage and presentation review, followed by push/deploy/live verification. The result-producing atlas remains approximately 50–55% complete because formal models are still zero. These percentages are milestone estimates, not fractions of variable counts. The former multi-month estimate conflated a near-finished catalogue deliverable with downstream inferential analysis; it should not be used for the website-only schedule. A result-producing atlas is a distinct several-week work package once official design inputs and authorized files are available.

The process was slowed by scattered field discoveries and repeated full finalizations. Use module-batched source audits, targeted validation while a batch is being edited, and one full finalization after a coherent batch. Avoid launching another full build for documentation-only changes.

## Next source audit

Inspect the raw metadata-only field inventory and current crosswalk by complete community module before selecting the next review. Do not repeat Parts C/H/J/K or claim a module is complete based only on candidate count; every official field needs a mapped or explicitly excluded disposition backed by questionnaire/Codebook evidence.

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
