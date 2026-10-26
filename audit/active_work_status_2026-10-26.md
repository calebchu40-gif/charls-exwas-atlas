# CHARLS ExWAS Atlas active work status — 2026-10-26

## 2015 pension payer context audit (local, pending publication)

Reconciled the 2015 payer-related variable families against the official Wave 3 questionnaire (printed pages 178, 180–181) and Codebook. The source labels were similar enough to invite false pooling. The catalog now keeps four contexts separate: FN074 option 28 (“Other People,” excluding its separate write-in); FN076 plan-routed multi-response option slots; FN075_W3_5 payer of annual contributions continued after a supplementary repayment; and FN072_W3_5 explicitly “Last Year.” All 174 related source rows are represented in the pension crosswalk, and a focused test verifies the 84 FN076 slots, 84 prior-year FN072 slots, and six plan-specific parent/option rows. No response frequencies or respondent-level data are included. Full audit: [`pension_2015_payer_item_context_review_2026-10-26.md`](pension_2015_payer_item_context_review_2026-10-26.md).

The source-specific builder and the 159-step finalization now complete successfully. Final local shards: E/P/C=6,278/2,116/1,013; E/P concepts=1,622 (E=1,316; P=331, including dual-role concepts); E/P concept-source mappings=8,288. Metadata co-availability pairs are 145,456/141,920/143,854/105,493/21,630 for 2011/2013/2015/2018/2020 and are not analytic sample sizes or results. All 517 tests, public-payload validation, exact 92-lock validation, JavaScript syntax and `git diff --check` pass. The 2015 count changed because item families that had been collapsed into a generic payer concept are now distinct. Local update is not yet pushed or deployed; the public site remains app v132 (Pages Deploy #259). Formal association models remain 0.

## Part A community source coverage (2026-10-26; deployed)

The 2011 community Part A review reconciles all 80 JA-prefixed inventory fields against the official questionnaire and Codebook: 69 are mapped to candidate concepts and 11 have explicit C-only/measurement-metadata/unresolved dispositions. It adds administrative establishment, boundary-change, urban-transition, land-rights certification, land development/consolidation, expropriation, homestead allocation policy and surname-concentration context. JA012 remains unresolved because the questionnaire says paddy-field area but the Codebook says irrigatable area. JA045 surname strings and JA052_1 open text are excluded; JA001/JA003/JA006 selectors, JA048 informant identity and unidentified JA042 fifth slots remain metadata. Full audit: [`community_part_a_exposome_context_review_2026-10-26.md`](community_part_a_exposome_context_review_2026-10-26.md).

The 159-step finalization completed in 6.7 minutes. Local shards E/P/C=6,278/2,116/1,013; E/P concepts=1,618 (E=1,312; P=331, dual-role included); E/P concept-source mappings=8,288. Metadata co-availability pairs are 145,456/141,920/143,137/105,493/21,630 for 2011/2013/2015/2018/2020; these are not analytic N or results. Generic pending label state=0 across roles; exact 92 analysis locks remain; formal association models=0. The complete local test suite passes (513 tests), including the 186 community baseline concept list; public payload, 92-lock, JS and deferred-loader checks pass. GitHub Validate #522 and Pages Deploy #259 both succeeded for commit `e4ab297`; the updated catalogue is live.

The clean-checkout CI fix is committed as `e490a81`; Validate #521 succeeded. The Part A batch is committed as `e4ab297` and deployed by Pages Deploy #259.

## Clean-checkout CI repair (2026-10-26)

GitHub Validate #520 failed because seven community source-review tests opened the ignored local-only `audit/raw_variable_catalog_v1.csv`; the artifact is intentionally excluded because it includes module row counts and local source archive names. Do not add that file to Git. Replaced test inputs with `audit/community_field_inventory_2011_v1.csv`, a 719-row sanitized 2011 community inventory containing only wave/module, CHARLS variable code and field label. Added a test asserting its four-column schema and absence of count/frequency fields. All 508 local tests, payload validation, exact 92-lock check, JavaScript/deferred-loader validation and diff checks now pass. The corrective commit is awaiting remote Validate confirmation. Part E site content was separately published in successful Deploy #258 (app v132).

## Newer local update: Community Part E migration review (2026-10-26)

Part E reconciles all 46 JE-prefixed fields in the metadata-only 2011 inventory: 44 questionnaire-anchored fields are mapped across eight community-context E concepts; JE014 informant identity and Codebook-only JE016 remain C-only. JE016 conflicts with the official questionnaire (Part E ends at JE015) and its direction/meaning is unresolved. JE013/JE015 name and telephone prompts are excluded. Added questionnaire-defined five-bin labels for JE003–JE006, Codebook response labels for 32 province slots and the two occupation fields (frequencies omitted), and explicit unresolved status for JE007S33 (“No Observations”). The Codebook-label builder previously omitted the `JE` prefix; this is fixed.

The 159-step finalization completed in 6.7 minutes. Local E/P/C shards=6,236/2,116/1,004; E/P concepts=1,610 (E=1,304; P=331; dual-role concepts included), E/P concept-source mappings=8,246. Metadata co-availability pairs are 143,752/141,920/143,137/105,493/21,630 for 2011/2013/2015/2018/2020; these are not analytic sample sizes or results. Generic pending label state=0 across all roles; exact 92 analysis locks remain. The focused Part E tests (3), full local suite (507), public-payload validation, exact 92-lock validator, JS syntax/deferred-loader checks, and `git diff --check` pass. This local update is not yet pushed/deployed; the public site remains at the previously verified version.

## Latest state (2026-10-26; Community Part B, D, and F updates pending deployment)

The Part D audit reconciles all 18 raw JD-prefixed inventory fields: 17 enterprise/employment/wage source fields are mapped as community-context candidates, while JD014 informant position is C-only. Questionnaire name/phone prompts are excluded. JD004 multi-response field-slot encoding is unresolved pending authorized-release QA and no categories are inferred. Part B reconciles all 127 raw JB fields: 122 candidate mappings include 42 JB029 facility fields and three infrastructure years; five other-text/informant fields are C-only. Part F adds two aggregate mortality-context candidates without denominators; unstandardized disease names/counts and informant identity remain C-only. Part C, Part A JA042, Part H and Part K reviews remain incorporated. No respondent text, respondent records, Codebook frequencies, or association results were used. Details: [`community_part_d_enterprise_wage_review_2026-10-26.md`](community_part_d_enterprise_wage_review_2026-10-26.md), [`community_part_b_infrastructure_timing_review_2026-10-26.md`](community_part_b_infrastructure_timing_review_2026-10-26.md), [`community_part_f_mortality_source_review_2026-10-26.md`](community_part_f_mortality_source_review_2026-10-26.md), and [`community_part_c_population_source_coverage_review_2026-10-26.md`](community_part_c_population_source_coverage_review_2026-10-26.md).

Full metadata finalization completed 159/159 steps in 7.7 minutes. Current shards: E/P/C=6,192/2,116/1,002; E/P concepts=1,602 (E=1,296, P=331, including dual-role concepts); E/P concept-source mappings=8,202. Community crosswalk=170 concepts/534 source-field mappings. Metadata co-availability pairs are 142,048 / 141,920 / 143,137 / 105,493 / 21,630 for 2011/2013/2015/2018/2020. They are not analytic sample sizes. Formal association models and pairwise-complete analytic N remain 0; the exact 92 analysis locks are unchanged.

Full local unittest suite: 504 tests pass. Public-payload validation, exact 92-lock validation, JavaScript syntax, and `git diff --check` pass after the 159-step build. The current local payload is app v132 and has not been pushed/deployed; current public site remains app v129 pending publication.

## Whole-project progress and remaining work

The candidate metadata catalogue and interactive prototype remain approximately 85–90% complete; this is a milestone estimate, not a fraction of variable counts. The broader result-producing atlas is substantially earlier because formal models remain 0. The earlier several-month estimate was not supported by a phase-level schedule and conflated catalogue completeness, analysis and downstream publication work. Re-estimate after establishing a valid first analysis specification and confirming the authorized data inputs; do not represent metadata co-availability as sample size or association results.

The process was slowed by scattered field discoveries and repeated full finalizations. This latest 159-step finalization itself completed in 7.5 minutes; future changes should be batched by module, validated incrementally during edits, and followed by one full finalization. Do not rerun full builds for documentation-only changes.

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
