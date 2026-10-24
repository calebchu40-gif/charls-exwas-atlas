# CHARLS ExWAS Atlas current work status

Updated 2026-10-24. Project repository: <https://github.com/calebchu40-gif/charls-exwas-atlas>. Public metadata prototype: <https://calebchu40-gif.github.io/charls-exwas-atlas/>.

Latest continuation: synthetic survey-domain and pairwise-complete software checks are complete, but they do not authorize or validate CHARLS models. A repository privacy-inventory regression test now blocks tracked licensed respondent-data formats and local pairwise/QA count outputs; the local `core_pairwise_complete_n_v1.csv` is ignored and untracked. All 266 local tests pass, and GitHub Validate [#248](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40058708473) succeeded for commit `d6e7f87`. Formal models and actual analytic pair Ns remain 0 while official wave/sample flags, weights, PSU and variance-design fields, and module eligibility are unresolved.

The 2026-10-24 private core-coverage refresh is recorded in [`core_coverage_gate_refresh_review_2026-10-24.md`](core_coverage_gate_refresh_review_2026-10-24.md). Its pair-level availability outputs remain under the local protected QA root. The missing 2013 official sample flags continue to gate that wave; no refreshed private counts are included here.

The protected five-wave table integrity check was rerun on 2026-10-24: 2011, 2015, 2018 and 2020 passed structure/ID checks; 2013 remains `CHECK` because the required official `crosssection` and `longitudinal` flags are absent. A recursive filename check found no incoming official Wave 2 `Weights.dta`; the local intake folder remains empty. Aggregate validation output stays under `%LOCALAPPDATA%/CHARLS_ExWAS_Atlas/qa_outputs/` and is not part of the repository.

Latest analysis-pipeline work: result rows can no longer be labeled `success` with `not_applicable` design fields. The validator now requires a verified weight choice and verified PSU use; when no official variance stratum is available, `variance_design` must include explicit `approximate method:` and `limitation:` labels (or Chinese equivalents). This is a release-state safeguard, not evidence that any wave is ready for modeling. Commits `733be9f`, `44218ad` and `cbf6a53` document the rule and handoff. Commit `1339afd` removes pandas 3.1 deprecated in-place drops in the guarded 2013 weight-merge code; the merge safeguards and behavior are unchanged. Current local verification: all 263 Python tests pass under both pytest and the repository's CI `unittest` command, with no pandas deprecation warnings; all 89 formal analysis locks match the triage inventory, Python compilation and JS syntax checks pass. GitHub Validate run [#236](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40056492623) succeeded. No association model was fitted.

The C-catalogue display now translates all 83 unique metadata subcategories into Chinese while keeping the original English classification available on hover and searchable. Commits `7e71278` and `6f2afa6` contain the localization and cache-key bump; live HTTP checks confirmed the homepage, versioned app bundle and C catalogue, with all 83 translations present. This is a presentation-only update; catalogue source records, model eligibility and association counts are unchanged. Regression tests ensure every current C subcategory has a Chinese label, the original source text remains accessible, and the page references the bumped app script cache key; the full suite now contains 264 tests.

The public methods panel now clarifies the age-domain boundary: CHARLS interviews the age-eligible main respondent and spouse, while Wave 4 individual weights apply to both. A `crosssection` flag alone therefore does not mean each row is age 45 or older; analyses must define the age domain and spouse-record handling from official release fields. The source and exact scope are documented in [`wave_specific_target_population_and_age_coverage_2026-10-22.md`](wave_specific_target_population_and_age_coverage_2026-10-22.md), and a public-page regression test protects this disclosure. This wording change uses official manuals only; no age distribution or individual record was inspected.

The age-domain update is live at the public site. GitHub Validate [#240](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40057380931) and Pages Deploy [#117](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40057380880) succeeded; direct HTTP verification confirmed the homepage and disclosure. The full local Python suite now passes 264 tests.

Survey-engine selection remains preliminary. A synthetic-only comparison using isolated local `svy` 0.35.0 showed that omitting the actual stratum changes SEs and design degrees of freedom. Independent hand calculations match the engine's one-stage with-replacement PSU Taylor SE for the weighted mean and coefficient covariance in this Gaussian identity-link model; a Student-t reference calculation reproduces its p-value from the engine-reported df. See [`survey_engine_synthetic_trial_2026-10-24.md`](survey_engine_synthetic_trial_2026-10-24.md) and its synthetic code. This does not validate other model families or whether the selected df is appropriate for a real design, uses no CHARLS records, and does not authorize fitting real models. The machine has no R installation, so the package's publisher-reported comparison against R's `survey` has not been independently reproduced here.

The synthetic engine probe also demonstrates why pairwise-complete or age-domain rows must not be physically filtered before declaring the survey design: the test domain has one in-domain PSU per stratum, `where=` preserves the original PSUs, and its Gaussian coefficient/SE match a full-design hand calculation, while pre-filtering triggers singleton-PSU errors. With one missing exposure/outcome inside the domain, `drop_nulls=True` gives `n=47` while keeping all 96 design rows and matching a manual full-design coefficient/SE calculation; null analysis fields outside `where=` are also accepted by the pinned engine. This is software behavior only. Pair-specific analytic eligibility, complete-case estimands and missingness assumptions still require CHARLS release and protocol review; do not interpret the demonstration as authorization to fit any real model.

The Chinese pre-analysis protocol now states that survey domains and pairwise-complete model rows must retain the full eligible survey design for variance estimation; it separately records pairwise exposure–phenotype availability N and covariate-complete model N. It also cautions that correct domain variance does not make complete-case estimates unbiased or resolve CHARLS module eligibility. Protocol cross-reference: [`CHARLS_ExWAS分析规约_v0.1.md`](CHARLS_ExWAS%E5%88%86%E6%9E%90%E8%A7%84%E7%BA%A6_v0.1.md).

To close the remaining official-design questions without inferring unreleased fields, a bilingual inquiry draft is prepared at [`charls_survey_design_support_inquiry_draft_2026-10-24.md`](charls_survey_design_support_inquiry_draft_2026-10-24.md). It asks about wave-specific variance strata/replicate weights, Wave 2 `Weights.dta` identity and join key, and measurement-specific biomarker eligibility/weights. It is a draft only and has not been sent; no official account was accessed.

## Current deliverable

The public site is a metadata catalogue and candidate-pair browser. It is not yet a results atlas: formal association models and pairwise complete sample-size calculations are both 0. Pair counts describe only source metadata available in the same wave. No CHARLS respondent-level data or descriptive frequencies are stored in the public repository/site.

Latest finalized field-wave catalogues contain E=4,739, P=2,113 and C=992 rows. The E/P source crosswalk covers 1,438 unique candidate concepts (1,150 E, 297 P, including nine concepts with both roles) and 6,652 concept-source rows. Wave-level metadata pair counts are 121,318 (2011), 132,082 (2013), 130,608 (2015), 101,757 (2018), and 13,906 (2020); these are source-concept combinations, not people, eligible samples, complete-case pairs, or results. The 2013 yesterday-affect set now lists all 11 separate WB05–WB15 items with official 1–5 labels and same-day/no-denominator caveats. The 2013 and 2015 physical-activity assignment markers are now searchable as C-only design metadata; their code meanings remain unresolved and must not define analytic eligibility. The 2011 community catalogue has 104 concepts and 198 mappings; the housing/food environment catalogue has 29 concepts and 161 mappings across waves. The latest complete Python suite passes 256 tests; the 89 formal analysis locks remain unchanged. These are metadata-field/concept counts; split indicators, repeated waves and concept mappings mean they are not counts of independent constructs or statistical tests.

## Scientific interpretation and governance

- 2020 DA029 asks the respondent’s subjective likelihood of reaching an age-specific threshold generated by XFAgePossibility. That threshold depends on age bands; preserve it in any future model or stratify by it. Do not treat DA029 as survival or combine it with earlier-wave DA029, which refers to prostate illness.
- CHARLS 2020 is the regular Wave 5 core survey with an added COVID module, rather than a COVID-only standalone survey. Its younger-cohort representativeness restriction and field-coverage caveats remain documented separately; the public methods panel now states the survey scope explicitly.
- The digital follow-up items are routed. Never recode skipped or structurally missing responses as “No”; derive eligible denominators from the authorized release and official routing. “Other” write-in text is not standardized and is excluded from the public catalogue.
- Main heating-energy and cooking-fuel candidates have now been checked against all five official questionnaires and Codebooks. The review preserves 2011–2018 heating-route differences, the 2018 questionnaire/Codebook label difference for heating code 8, the 2020 XFinancialResp household referent, and the 2018/2020 no-cooking options plus the 2020 solar-code shift. These are household context proxies, not measured pollutant doses; details are in `audit/housing_fuel_source_review_2026-10-24.md`.
- XFAgePossibility is generated question-target metadata. DC030 is interviewer-observed interview language. Neither is an automatically approved adjustment covariate. The C catalogue is a source/design aid; the adjustment set must be chosen for a defined estimand and causal structure.
- Official sources used for the 2020 update and cross-wave review are the extracted CHARLS English questionnaires and Codebooks in `sources_official/`. The 2018 DA056 routes and labels are verified; older-wave unselected checkbox storage remains unresolved and is not converted to “No”. No respondent-level observations or Codebook frequencies were used.

## Reproducibility and checks

The 2011 community water/fuel source-count catalogue now shows its questionnaire unit (`households`) and 2010 reference period. Because the source list does not establish mutually exclusive categories or give a total-household denominator, the site explicitly avoids percentage conversion or person-level interpretation. See `audit/community_environment_candidate_review_2026-10-22.md`; the incremental source is `scripts/build_community_exposure_crosswalk.py`.

The housing catalogue now source-reviews 2011–2020 heating availability and gas-supply fields wave by wave, plus 2020 tap-water access, waterworks treatment and air-cleaner presence. It preserves the 2020 questionnaire/Codebook wording mismatch for I019 (“house has heating” vs. “Centralized Heating”), the 2020 household financial-respondent referent, the air-cleaner observation/asking instruction, and Do-not-know on water treatment. This batch propagated through `python scripts/build_ep_atlas_metadata.py --finalize-only`; all 176 Python tests, JavaScript syntax and `git diff --check` pass. See `audit/food_environment_crosswalk_audit_v1.md`; incremental propagation is in `scripts/apply_housing_context_source_review.py`.

Cross-wave review also confirmed the same yes/no air-cleaner presence item I027_W3 in both 2015 and 2018. 2018 had previously appeared only as the separate automated concept `dwelling_air_cleaner_access`; an audited alias now brings it into `air_cleaner_home` with 2015 and 2020 while retaining source-wave provenance. It remains a household-presence proxy, with 2020's explicit XFinancialResp referent and interviewer-mode note preserved. The finalize-only rebuild has propagated this addition through the E/P concept index, wave-specific catalogue and public site JSON; all 176 tests pass.

The Wave 5 digital review lives in `audit/wave5_digital_behavior_and_life_expectancy_review_2026-10-24.md`; the 2011–2018 cross-wave review is in `audit/cross_wave_digital_behavior_review_2026-10-24.md`. Work Codebook identifier normalization is documented in `audit/work_codebook_identifier_normalization_2026-10-24.md`; the 2011 work questionnaire-only value review is in `audit/work_questionnaire_only_values_2011_review_2026-10-24.md`. The 2011 community education exact/fallback response formats and other questionnaire-only source checks are in `audit/community_education_and_context_review_2026-10-24.md`. The Harmonized CHARLS D codebook is now recorded as a secondary cross-wave reference in `audit/harmonized_charls_codebook_reference_review_2026-10-24.md`, with selected age, gender, rurality, self-rated health, BMI and ADL mappings in `audit/harmonized_charls_secondary_crosswalk_v1.csv`. It clarifies construction differences and missing-value categories, but does not authorize replacing raw CHARLS fields or close the variance-stratum gate. Crosswalk sources are `audit/behavior_exposure_variable_mapping_v1.csv` and `audit/health_symptom_variable_mapping_v1.csv`. The full metadata propagation pipeline calls the Wave 5 core demographic review and the digital-behavior review after the source catalogue rebuild.

Latest checks: `python scripts/build_ep_atlas_metadata.py --finalize-only` completed after rebuilding the community crosswalk; all 180 Python tests pass; `node --check site-prototype/dist/app.js` and `git diff --check` pass. The fixed 89-row `DO NOT ANALYZE` lock audit remains intact. The latest 2011 work review carries questionnaire wording/ranges to the public catalogue while preserving release-code uncertainty; detailed source notes are in `audit/work_questionnaire_only_values_2011_review_2026-10-24.md`. The community crosswalk now has 198 field mappings across 104 concepts; exact education percentages and conditional fallback brackets are kept distinct. Catalogue rebuilds now preserve the prior audit-row order and append newly discovered fields, keeping Git review diffs compact.

The public C metadata page was clarified on 2026-10-24 after review of its user-facing labels: “covariate candidate” is explicitly described as a search candidate, not a selected model adjustment; measurement/routing rows are described as interpretation metadata. The update is in commit `6966730` and is live on GitHub Pages. The Harmonized CHARLS age note now clarifies that its documented `RwAGEY` construction uses birth/interview year and month, not day-level birthday comparison; it remains a secondary comparison and does not replace wave-specific official fields. Official wave-specific weights, sample markers, PSU mapping fields, and the distinction between general and measurement-specific weights are summarized in `audit/prepared_wave_design_field_audit_2026-10-22.md`; the variance-stratum and source-release gates remain open. Formal association models remain 0.

## Next work, in order

1. Continue source-by-source exposure and phenotype expansion, using official wave-specific questionnaires and Codebooks; prioritize lab/biomarker and environmental/social domains with clear measurement units and routes. Cross-wave digital behavior has now been source-reviewed for 2011–2018 and reconciled to the dedicated 2020 module.
2. Reconcile cross-wave concept identity separately from raw field labels, especially code reuse and changes in questionnaire route. Do not count one-hot options or repeated waves as independent constructs.
3. Complete survey-design/source readiness: identify the official weight, strata, PSU and sample-eligibility variables by wave and analysis target. The 2013 official sample markers still need the authorized weights intake described in `audit/wave2_official_weight_intake_2026-10-23.md`.
4. Only after approved data, the target population, survey design, missingness rules and estimand are explicit, build a reproducible ExWAS model pipeline and generate aggregate, disclosure-safe results for review before publication.

For efficient progress, batch metadata extraction by questionnaire module, generate auditable source mappings, and validate in one pipeline run per batch. Keep ambiguous items as unresolved candidates with precise route notes instead of delaying a whole module or forcing harmonization.

## 2026-10-24 continued: BB004 deployment and BB005 review

GitHub Pages Deploy #90 for commit `bad4879` completed successfully. The BB004 C-metadata wording now uses `HOLD FOR SOURCE VALIDATION` without implying that the field was added to the formal E/P `DO NOT ANALYZE` lock list; that list remains 89 rows.

Reviewed the official 2011, 2013, 2015 and 2018 BB005 questionnaires and Codebooks. Added C-catalog records for all four waves; the earlier candidate seed contained only 2013/2015. The new records preserve the calendar-year measure, questionnaire bounds and conditional route, the 2018 XRType=2 new-interview restriction, and the 2018 current-address BB001_W3 reference versus 2011–2015 permanent-address wording. The 2011 Codebook's generic “Year” label is retained without overclaiming a more specific field label. Codebook means, ranges, OBS counts and participant data were not copied. These fields remain contextual metadata; no E/P concept or association model was created.

The finalize-only pipeline completed and regenerated the C shard to 980 rows. E/P concept and source-mapping counts remain 1,429 and 6,625. All 191 Python tests pass; every static JSON parses, the JavaScript syntax check passes, and `git diff --check` is clean. The new audit is `audit/residential_history_bb005_source_review_2011_2018_2026-10-24.md` and its idempotent updater is registered in both metadata pipeline modes. Commit `0136957` is pushed; Pages Deploy #91 succeeded. A cache-busted live C shard returned HTTP 200 and confirmed all four BB005 waves, their continuous-year/no-label treatment, and the 2018 route/reference notes.

Next source batch: review adjacent BB003 county/city/district move-in year fields by wave. These are distinct from BB005 village/community move-in year and must preserve their own residence reference and questionnaire routes.

## 2026-10-24 continued: BB003 county/city/district move-in year

Reviewed the official 2011, 2013, 2015 and 2018 BB003 questionnaires and Codebooks. Added four wave-specific C metadata records, filling the 2011 and 2018 gaps in the prior candidate seed. BB003 records the calendar year first living/moving into the relevant county/city/district and stays separate from BB005's village/community year. The audit preserves the 2015 `BB001_W3`/`XRType=NEWIW` branch, the 2018 `XRType=2` new-interview scope, and the change from 2011–2015 permanent-address wording to the 2018 current-address reference. No Codebook descriptive statistics or respondent data were copied; special missing codes remain for authorized-release validation.

The full metadata rebuild passed; C rows now total 982, with BB003 and BB005 each represented in all four waves. E/P concepts and source mappings remain 1,429 and 6,625; formal E/P locks remain 89. All 194 Python tests pass, every static JSON parses, the JavaScript syntax check passes and `git diff --check` is clean. Commit `35861eb` is pushed; Pages Deploy #92 succeeded. The live C shard returned HTTP 200, contains 982 rows, and confirms both BB003 and BB005 in all four waves. Audit: `audit/residential_history_bb003_source_review_2011_2018_2026-10-24.md`.

Next, inspect adjacent migration-history items (BB007–BB009) and only add/source-label them where official question routes and codebook field identity are sufficiently clear.

## 2026-10-24 continued: BB007–BB010 alternate mobility branches

Reviewed the 2011 and 2013 questionnaires and Codebooks. The questionnaire routes BB001=1 or 2 to BB009/BB010; the alternate eligible path uses BB007/BB008. BB007 and BB009 are separate Yes/No gates, each routing to its own cumulative duration pair (years and months). Added the previously missing 2011 BB008_1/BB008_2 and BB010_1/BB010_2 C rows. Kept 2011 BB007's “present county/city” Codebook wording distinct from its questionnaire's “permanent county/city/district” wording and did not force a BB007/BB009 merge. Conditional absence is not zero; 2011 BB010 has a questionnaire check against `2013-BB003`. No Codebook frequencies, means or respondent records were copied.

The source updater is registered in both metadata pipeline modes and has regression coverage for branch logic, labels and duration units. The full metadata rebuild passed and the C shard has 986 rows; E/P concepts and source mappings remain 1,429 and 6,625, and the formal E/P lock audit remains 89. All 198 Python tests pass, every static JSON parses, the JavaScript syntax check passes, and `git diff --check` is clean. This batch is ready to commit and publish. Audit: `audit/residential_history_mobility_duration_review_2011_2013_2026-10-24.md`.


The 2011 Community Part K interviewer-observation block is now represented by four additional distinct context candidates: JK002 socioeconomic status, JK004 built-form organization, JK005 perceived crowding and JK006 disability accessibility. The questionnaire anchors for 1 and 7 are preserved; codes 2–6 are described as intermediate ordinal ratings, not assigned fabricated labels. They remain subjective community-level observations. The community crosswalk now contains 104 concepts and 198 fields; the 2011 E/P metadata co-availability count increased by 844 because four additional E concepts can pair with 211 phenotype concepts in that wave. This is a metadata count only, not sample size or association evidence. See `audit/community_interviewer_observation_review_2026-10-24.md`. The full finalize-only rebuild passed 179 Python tests, JS syntax and `git diff --check`; the 89-row `DO NOT ANALYZE` lock audit remains intact.

The five-wave household I025 cleanliness/tidiness and I026 temperature fields are now marked as interviewer-recorded ordinal observations, not indoor-pollution assays or measured temperature. Source review found a 2011 version difference: the baseline questionnaire includes code 6=Not applicable, while the household questionnaire and Codebook list only codes 1–5. The catalogue retains the Codebook-based 2011 labels and records the discrepancy for release-specific resolution. All 180 Python tests, JavaScript syntax and `git diff --check` pass. Details: `audit/housing_context_source_review_2026-10-24.md`.

The 2020 household floor-condition item I027 is now source-reviewed with its interviewer instruction and nominal categories (covered/flat, concrete, uneven). It is documented as a household context proxy, not a mobility/fall-risk test. This adds no new concept because the field was already present in the candidate catalogue. Validation is recorded with this source-review batch.

The adjacent 2020 I002/I003 move-in timing pair is now source-reviewed. Although the Codebook labels say “Time House Built,” the questionnaire asks when the Household Financial Respondent moved into current housing. The exact-year item (-1 if unable to answer) and six-level fallback bracket remain separate; they are not treated as building construction year. Codebook frequencies are omitted. See the same housing context source-review audit.

The combined 2020 housing-context batch passes all 182 Python tests, JavaScript syntax validation and `git diff --check`. I027 is live after Pages deploy #83; I002/I003 is live after commit `28e727c` and Pages deploy #84. Both public JSON entries were verified. Metadata counts and the 89-row analysis lock are unchanged.

The five-wave household food/eating-out spending source audit is synchronized across the main E catalog, its dedicated domain crosswalk and the nested domain-page JSON: all ten rows show reviewed past-week household Yuan scope, wave-specific own-production/exclusion caveats, official questionnaire source paths, and unapproved cross-wave comparability. Stale generic “questionnaire review pending” notes have been removed from those source-field rows. The finalize-only rebuild and all 183 Python tests pass; every site JSON parses, JS syntax and `git diff --check` pass. The 89 analysis locks and catalogue counts are unchanged. Commit `6e81c61` was deployed successfully by Pages #86; live cache-busted JSON verification confirmed all ten food/eating-out rows contain reviewed notes, source paths and Yuan/week units, with no generic pending notes.

The 2018 housing C-candidate review covers HA025_W4 property-roster location slots 1–11 and HA057_W3 monthly mortgage payment. The questionnaire defines four response categories for each HA025_W4[i] property; those slots are not a respondent's current residence or 11 independent observations. HA057_W3 is continuous 10,000 Yuan/month on the active-mortgage route, not individual income. No Codebook frequencies or extrema were copied. The 12 rows carry official-source citations and scope/routing caveats in the field catalog, C shard, and candidate-series summary; the generated pipeline reapplies this audit after catalog reconstruction. The C generic-pending queue falls from 199 to 187; E/P generic-pending remains 0. Commit `d6ac63b` deployed successfully by Pages #87.

Follow-up source reconciliation found that 2018 I000_W4_2 is the main respondent's current-residence context and must be distinguished from property-level HA025_W4[i]. The previous generic mapping caveat incorrectly described it as a repeated property slot. The source-review script now updates both existing E and C candidate rows, the housing mapping and concept-source audit, with the four Codebook labels and questionnaire-route distinction; it keeps cross-wave equivalence and analysis eligibility pending. Commit `1b5498b` contains the correction. Full finalize-only rebuild passed, all 186 Python tests passed, all site JSON parsed, JavaScript syntax and `git diff --check` passed. Pages #88 completed successfully; live E/C shards show the corrected current-home distinction, and all 12 audited property/mortgage C rows have reviewed statuses.

The next C review batch checked BB004 residential-history fields in 2011, 2013, 2015 and 2018. The 2011 questionnaire describes same-village/community residence, while the Codebook describes same county/city; the conflict is retained with blank response labels and a HOLD FOR SOURCE VALIDATION state. Later-wave 1=Yes/2=No labels are documented with their specific permanent/current-address reference and conditional BB005 year route; they are not assumed equivalent to 2011 or to current neighborhood quality. The C generic-pending count falls from 187 to 183. Full finalize-only pipeline passed, all 188 Python tests passed, all site JSON parsed, JavaScript syntax and `git diff --check` passed. The formal E/P DO NOT ANALYZE inventory remains at 89 rows; the C hold is a source-validation state outside that analysis-lock inventory. Pages #89 succeeded and live metadata showed the 2011 hold plus later wave-specific labels. The live review prompted a wording cleanup to keep the C hold distinct from the formal E/P analysis-lock label; that patch is tested and awaits Pages publication.


## 2026-10-24 continued: BB007–BB010 release verification

Commit `41bd6a3` is pushed to `main`; GitHub Pages Deploy #93 completed successfully (run `40018980973`). A cache-busted public `catalog_c.json` returned HTTP 200 and 986 rows; it contains the 2011/2013 BB007–BB010 gates and duration fields, including the four newly added 2011 duration components. The site remains a metadata catalogue; these residential-history fields do not become environmental dose measures. No E/P concepts or source mappings changed, and formal association models remain 0.

The next work shifts back to source-quality improvements for substantive environmental and objectively measured domains, using the already collected official questionnaires, Codebooks, biomarker guides, and domain crosswalks. Batch full modules where source definitions are clear; retain unresolved release-specific identities and survey design/weight gates.

## 2026-10-24 continued: blood pressure and pulse source review

Reviewed official 2011, 2013 and 2015 physical-examination/Biomarker questionnaires and Codebooks for systolic pressure, diastolic pressure and pulse. All list three repeated readings on the Omron HEM-7200 protocol; systolic and diastolic are explicitly in mmHg. The questionnaire writes the pulse unit only as “P”, so the catalogue leaves the unit blank. The 993/999 codes remain non-completion/status codes, separate from measurements; test arm, position, compliance and recent behaviors remain context fields.

The 2011 questionnaire uses LI identifiers while its Codebook lists QA candidate fields; one-to-one field identity is still unresolved. The 2013/2015 instruments identify exact QA fields, while release availability, valid-value checks and analytic eligibility remain open. The updater is registered in both metadata pipelines and propagates units and source caveats to the public P catalogue. Full finalization and 225 tests passed; all 89 formal analysis locks remain exact. Commit `0eaf332` is pushed; Pages Deploy #106 (`40044331718`) and validation run #195 (`40044331712`) succeeded. Cache-busted live assets confirm the new metadata. Audit: `audit/blood_pressure_pulse_source_review_2011_2015_2026-10-24.md` and `audit/public_site_deployment_verification_2026-10-24.md`.


## 2026-10-24 continued: objective measurement protocol source review

Added the official 2011 physical-examination questionnaire/manual and extracted text after discovering that the local official-source set lacked it. The manual confirms the 30-minute pre-blood-pressure behavior question (LI875), which the 2011 release Codebook labels QA017; source identity and the blood-pressure-only interpretation now appear in C metadata. The same manual calls the chair-height setup field LI007, while the release Codebook says QH006=Height. This item-code relation remains unresolved and is visibly held for release-identity reconciliation.

The 2013 questionnaire confirms QH006 as chair height in centimeters. For 2015, QH006 is a 42-cm-standard-chair/other-chair selector and QH006_1 holds the conditional other-chair height in centimeters. The site now lists those separately, preserving structural absence and excluding all protocol fields from E/P pairing. Audit: `audit/objective_measurement_protocol_source_review_2011_2015_2026-10-24.md`. The idempotent updater is registered in full and finalization pipelines. Full rebuild passed; all 200 Python tests, JSON parsing, JavaScript syntax, Python compilation, and diff checks passed. Directory size remains E=4,750, P=2,068, C=986; E/P concepts=1,429, source mappings=6,625; formal locks=89; models=0.


Deployment verification: commit `7903732` completed GitHub Pages Deploy #94 successfully (run `40021600663`). Cache-busted public C catalogue returned HTTP 200 with 986 rows. Live checks confirmed the 2011 QA017/LI875 wording and measurement-context status, 2011 QH006/LI007 identity hold, 2013 QH006 chair-height metadata, and separate 2015 QH006 chair selector/QH006_1 conditional-height field.

## 2026-10-24 continued: objective phenotype Codebook provenance

The 15-concept objective-measurement candidate crosswalk now records distinct official source sets for 2011, 2013 and 2015. Automated token-level validation found all 36 candidate field identifiers in each wave's extracted Codebook (45 concept-wave records). The public metadata clarifies that this establishes code-token presence only; item semantics, routing, units, valid values and release-file availability remain to be verified. In 2011, LI* protocol identifiers are explicitly not assumed to equal similarly worded QA*/QB*/QC* release fields. The crosswalk builder is included in full and finalize-only metadata pipelines. Full finalization completed; all 203 tests, 34 static JSON files, JS syntax, Python compilation and `git diff --check` pass. The source index now contains 6,631 E/P mappings for 1,429 candidate concepts (1,150 E and 288 P, with dual-role concepts); the generated site catalogue has 4,750 E, 2,110 P and 986 C field-wave rows. Metadata co-availability is not sample size or analysis eligibility. Formal E/P locks remain 89; models and pairwise complete Ns remain 0. See `audit/objective_measurement_crosswalk_source_review_2011_2015_2026-10-24.md`.

部署核验补充：提交`9b11898`由GitHub Pages Deploy #95（run `40023419731`）部署成功；缓存绕过的公开`objective_measurements_v1.json`返回HTTP 200、45条映射，波次来源和代码本代码存在说明均已上线。本地随后完成另一轮界面改进：将Codebook的108个波次字段标签显示于可搜索的体测表，2013 QL002标注提取文本被页边界截断；204项测试和静态资源检查通过。当前界面改动尚待提交与部署。

界面部署核验：提交`e8377e6`对应 GitHub Pages Deploy #96（run `40024182348`）成功。带缓存绕过读取公开主页确认新增“官方Codebook字段标签”列；线上app.js使用`objective_measurements_v1.json?v=2`并搜索`source_field_labels`；公开JSON HTTP 200、45条记录，2013 QL002保留经原始PDF页面确认的分页截断提示。该批不发布任何Codebook统计值或个体记录。

后续工作范围复核：实验室分析物目录已单独记录2011/2015血检和2013无实验室采血；客观现场测量目录当前限于2011/2013/2015对应体检/生物标志物问卷。对2018/2020官方Codebook没有检出本目录的QA/QB/QC候选字段代码，也没有找到同一原始题号；这只是当前源文件检索范围结论，不足以单凭缺码证明整波绝无类似测量，因此不补造后续波字段，等待完整的波次测量源目录/发布说明验证。

界面范围补充：客观体测页现明确仅列入目前已有对应官方问卷和Codebook候选映射的2011、2013、2015。2018/2020代码本未出现同一QA-QM候选代码，但代码名不同不能证明不存在可比测量；页面说明需先核对这两波专用测量模块和发布说明。页面同时区分2013现场体测与2011/2015实验室血液指标，并链接到单独的血液生物标志物目录。增加UI回归测试，专项测试5项通过，JS语法和diff检查通过；此轮页面修改待提交。

GitHub Pages #97（run `40024908402`，commit `80a88c8`）成功；缓存绕过的公开主页已核实显示2018/2020体测目录范围说明。用户长期目标当前状态为`active`，本轮继续工作不需手动恢复。


### 2026-10-24续：社区工业污染变量字段语义校准
依据官方2011社区问卷及Codebook，JB018为本村/社区主观有序等级，JB019为附近村镇等级且仅村级受访者进入该路线，JB027为村庄至最近工业污染源的公里距离；问卷明确污染源在本村时记0。三者作为不同的社区情境代理指标展示，不合成个人暴露剂量或污染评分；未复制受访者值或Codebook描述统计。字段级说明已进入社区网页、E目录及可重复构建流程。社区目录保持104概念/198字段映射；E/P概念1,429、来源映射6,631，正式分析锁89，关联模型与逐对样本量仍为0。全量生成和208项测试、静态JSON/JS检查通过。详见`audit/community_industrial_pollution_distance_review_2011_2026-10-24.md`。提交`2bcf2c7`已推送；GitHub Pages Deploy #98（run `40026396623`）成功。公开社区JSON HTTP 200、104概念，在线确认JB018/019的分档方向及村级路线、JB027单位km与本村污染源记0规则。


### 2026-10-24续：客观测量波次边界补充
审阅CHARLS 2018 Wave 4官方用户指南后，确认非血液生物标志物（人体测量、血压等）采集于Wave 1–3，血液生物标志物采集于Wave 1和3；2018 Wave 4因此不纳入这些客观测量目录。另区分官方数据门户的2020 Wave 5发布包与CHARLS公告中2021–2023第五轮常规调查（招募材料提及体检、生物样本和手环）。目前本项目未取得/验证2021–2023发布文件，不能把后续调查采集计划映射进2020文件。2020问卷中的“是否由医生/护士测量血压”“是否接受体检/化验”属于医疗服务/既往检查报告，不是现场直接测量。已更新体测页范围说明和来源审计；专项5项测试通过。审计：`audit/objective_measurement_crosswalk_source_review_2011_2015_2026-10-24.md`。


### 2026-10-24续：社区目录首页计数同步
发现社区页简介仍显示旧版100概念/187字段，与当前JSON的104概念/198字段不符。已同步首页数字，并在页首加入JB018/019/027的基本解释，增加回归断言；完整测试待复跑。


### 2026-10-24续：社区天气字段单位与参照期
按2011官方社区问卷补齐JA039_1最低温、JA039_2最高温单位“degrees Celsius (°C)”，JA040雨天数和JA041雪天数单位“days”；明确四项都是社区告知者对2010日历年的估计，不是气象站链接或个人温度暴露。单位和字段级边界进入社区crosswalk与JSON，并增加问卷文本回归测试。社区概念/映射仍为104/198。全量最终目录同步及测试待完成。审计：`audit/community_weather_estimate_source_review_2011_2026-10-24.md`。


### 2026-10-24续：社区天气单位完成与目录收尾
JA039_1/JA039_2显示°C，JA040/JA041显示days，参照2010日历年并标注为社区告知者估计。社区目录104概念/198源字段。完整finalize-only重建完成；最终站点目录E=4,750、P=2,110、C=986；E/P候选概念1,429（E=1,150、P=288，含9个双角色），来源映射6,631，正式分析锁89。此前流水线在后续C元数据传播前过早生成角色分片，造成中间值978；后续修复将C分片生成放到所有目录编辑之后。已运行全部209项测试、34个静态JSON校验、JS语法、Python编译和`git diff --check`，均通过。跨波E/P概念同波字段可共存计数为2011:121,107、2013:126,514、2015:130,376、2018:101,757、2020:13,906；这些不是有效样本数、分析资格或关联检验数。仍无正式模型或逐对样本量。社区天气审计：`audit/community_weather_estimate_source_review_2011_2026-10-24.md`。本批待提交/部署核验。


天气字段上线核验：提交`0a79030`对应GitHub Pages Deploy #100（run `40028365448`）成功。缓存绕过读取公开`community_exposures_v1.json`返回HTTP 200、104个概念；JA039_1/JA039_2单位为degrees Celsius (°C)，JA040/JA041为days，字段级天气代理解释均已上线。


### 2026-10-24续：概念来源索引角色覆盖同步
发现E/P概念源crosswalk尚未同步`catalog_role_override_review_v1.csv`中的七个2018 HA004总价/单位价格式选择器，错误保留E角色；主字段目录已正确将其作为C元数据。生成器按精确波次、字段、旧角色、审计概念及已存在C目录记录同步为C，并在专题概念映射连接后再次清除这些C-only字段的候选E/P概念ID。七条现为C且匹配C元数据；对应总价与单位面积价格金额变量仍保留为不同E候选。完整finalize-only重建后：候选概念1,428（E=1,149、P=288，含9个双角色）、E/P来源映射6,624；最终静态目录E=4,750、P=2,110、C=986；正式分析锁89。波次元数据共同可用配对数为2011:121,107、2013:126,514、2015:130,376、2018:101,551、2020:13,906，仅表示目录字段共存，不是样本量或分析/显著结果。210项测试、34个静态JSON、JS语法、Python编译及diff检查通过；没有关联模型或逐对完整样本量。详见`audit/ep_crosswalk_catalog_role_override_reconciliation_2026-10-24.md`。本批待提交与Pages部署核验。

### 2026-10-24续：最终目录角色分片顺序修复
复跑完整finalize-only流水线时确认，2018房屋登记与居住史等后续审计步骤会在初次生成`catalog_e/p/c.json`之后补充或修订目录行；流程中间曾打印C=978，最终主目录及公开C分片应为986。已把E/P/C角色分片重建追加到全量和finalize-only流水线末尾，并新增顺序不变量测试。完整最终化及211项测试通过，本地分片与最终主目录一致：E=4,750、P=2,110、C=986。公开资产沿用前一部署并已核验，后续仅构建器顺序修正不触发Pages路径过滤式部署。

网站部署核验：提交`4177ca4`由GitHub Pages Deploy #101（run `40030070302`）成功。缓存绕过读取公开`catalog_c.json`返回986行；7条2018 HA004格式选择器均在C分片，候选Concept ID为空；公开候选配对索引返回`metadata_candidate_pairs_only`，主页计数显示1,428。

### 2026-10-24续：首页候选范围计数拆分
首页原先把E/P角色合并为一个“候选概念”数字，难以直接看出暴露与表型规模。现按来源索引分别显示E=1,149、P=288、5个调查波次和正式关联模型=0；注释说明9个概念兼具E/P角色，去重后为1,428个唯一概念，6,624条概念—源字段映射只是目录链接，不是样本量或关联结果。统计由构建脚本生成，并新增断言核对首页卡片与机器可读范围JSON一致。212项测试、34个静态JSON、JS/Python语法和diff检查均通过。提交`62e80ff`由GitHub Pages Deploy #102成功；缓存绕过读取线上主页确认四项计数及概念映射说明均更新。

### 2026-10-24续：握力与呼气峰流速来源核验
依据CHARLS 2011基线用户指南、2011体检问卷、2013/2015 Biomarker问卷及波次Codebook，将握力和呼气峰流速并入客观测量来源审查及完整/最终化构建流程。握力为左右手各两次、明确kg，练习试测不作结果，993/999保留为状态码；2011 LI816/LI851–LI853与QC003–QC006精确对应仍未核实。峰流速为三次峰流速仪读数，不是完整肺量计；单位留空，30年龄标记及890/993/999均按官方路由/状态说明保留，2011 LI807–LI809与QB002–QB004映射仍待释放数据资料核实。波次字段仅为候选表型，不表示授权发布文件中已确认可分析。新增审计`audit/grip_strength_peak_flow_source_review_2011_2015_2026-10-24.md`和回归测试；客观测量JSON缓存键升为v4。完整finalize-only及225项测试、JS/Python编译、89条正式锁定清单和`git diff --check`均通过。当前目录E/P/C为4,739/2,104/990，候选概念E=1,150、P=288、唯一1,429，来源映射6,643；关联模型和逐对完整样本量仍为0。该批提交及部署核验待完成。
部署核验：提交`f4f3345`对应GitHub Pages Deploy #107（run `40045896267`）成功。缓存绕过读取公开客观测量JSON返回HTTP 200、45条概念—波次记录，其中握力/峰流速共6条；握力单位kg，峰流速单位留空，`app.js`使用v4缓存键。

### 2026-10-24续：站立平衡测试来源核验
复核官方2011体检手册、2011基线用户指南及2013/2015 Biomarker问卷和Codebook，覆盖半串联、全串联和并足站立。记录半串联/并足最长10秒；全串联按年龄分为70岁及以上目标30秒、较年轻目标60秒。完成状态、未达目标时间、代偿动作、同意/安全及前项测试路线分别保留；993/999不是秒数，未问或路由跳过不可当0秒。2011问卷LI题号与Codebook QD/QE/QF字段身份仍未精确核验；2013/2015问卷及代码本有对应字段，但未据此声称受访者发布文件已可用。新增`audit/balance_test_source_review_2011_2015_2026-10-24.md`、构建审查步骤及测试；不计算平衡分数或关联。完整finalize-only完成；229项测试、JS/Python编译、89条正式锁定清单及diff检查通过。概念来源映射6,643，站点E/P/C分片4,739/2,104/990，关联模型及逐对完整样本量仍为0。提交`2a7ca60`已推送，Deploy #108成功。后经线上核验发现专题JSON尚未同步审查结果，补丁提交`4bc7e25`的Deploy #109成功；线上JSON HTTP 200，已见9条平衡测试波次说明。

### 2026-10-24续：基础人体测量来源核验
复核2011体检问卷与基线用户指南、2013/2015 Biomarker问卷和Codebook，核对身高、上臂长、膝高、体重及腰围。明确cm/kg单位，保留侧别及鞋履/衣物/依从性等测量背景，体重150 kg资格路线及993/999状态值单独说明；未生成BMI。2011 LI011/015/019/841/907到发布Codebook QI/QJ/QK/QL/QM字段的精确身份仍未解决，2013/2015问卷代码只确认工具文本，不证明受访者释放文件可用。新增审计、构建器步骤及测试。完整finalize-only及233项测试通过；JS/Python编译、89条正式锁定清单和diff检查均通过。E/P/C目录分片4,739/2,104/990；E/P唯一概念1,429、来源映射6,643；模型和逐对完整样本量为0。该批提交与Deploy #110核验待完成。
部署核验：提交`94727b8`对应GitHub Pages Deploy #110（run `40047066433`）成功。缓存绕过读取客观测量JSON HTTP 200，共45条记录；公开表显示身高、上臂长、膝高和腰围单位cm，体重kg，并保留2011身份未核实提示。

### 2026-10-24续：重复椅子起立测试来源核验
复核2011体检问卷、基线用户指南和2013/2015 Biomarker问卷与Codebook。五次起立/坐下测试的完成状态、两种路线时长、完成次数(0–5)、躯干/手臂使用分别保留；题目前言“尽快”与结果题“通常速度”的官方英文措辞冲突记录为来源差异，不擅自统一。993/999是状态码，座椅高度/类型为测试设置元数据。2011 LI003–LI008与候选QH字段的精确发布身份未核实；未生成评分或关联。新增审计、构建步骤及测试。客观测量目录15类×3波次共45条，均已纳入来源审查；全量最终化、237项测试、JS/Python语法、89条正式锁定清单和diff检查通过。E/P/C目录分片4,739/2,104/990，E/P候选唯一概念1,429、来源映射6,643；正式关联模型和逐对完整样本量仍为0。该批提交及Deploy #111核验待完成。
部署核验：提交`101c3b1`对应GitHub Pages Deploy #111（run `40047594897`）成功。公开客观测量JSON HTTP 200，45条记录、15个概念；椅子起立五次测试措辞差异和分路线时长已显示。
### 2026-10-24续：值标签覆盖报告与最终目录对齐

发现值标签覆盖审计仍读取早期中间字段表，导致报告中的“未复核”状态分布与最终网站E/P/C分片及当前队列不一致。已改为在全量与finalize-only流程的末端，直接按最终角色分片重建覆盖CSV/Markdown；CSV保留原角色—类别—子类别字段级结构，并将队列快照中的E/P/C目录总行数同步为4,739/2,104/990，通用待审数为0/0/171。该修正仅更新统计口径，不改候选角色、来源映射、正式锁或分析结果。全量finalize-only重建完成，新增一致性回归检查后共239项测试通过，89条正式禁分析锁逐项一致。提交`99953f6`已推送；GitHub Validate run #205（`40048483905`）和后续测试提交的run #207（`40048680151`）均成功。该批只更新审计报告/构建脚本与测试，没有更改浏览器静态资产，因此不触发Pages部署。

同日再次在本机受控数据目录运行准备表结构验证：2011、2015、2018、2020通过结构检查；2013仍为CHECK，因为派生表缺`crosssection`和`longitudinal`两个官方样本标记。受控目录中的`incoming_2013_weights`当前为空，未发现可供重建验证的原始发行权重文件；因此未改写个人表，也未用非缺失权重猜测样本资格。该私人QA只更新本机输出，不复制个人记录、ID或权重值到仓库。官方 Wave 2 页面仍列出独立Weights文件，Release Note说明其中包含两类资格标志；原始文件须在获准门户下载后进入隔离目录再做版本/哈希与字段核验。

### 2026-10-24续：结果家族P值校正组件

新增`adjust_exwas_pvalues.py`，按单个预先冻结的检验家族计算Bonferroni调整值和Benjamini–Yekutieli q值。未估计/不可估计的预定义假设以`None`保留在K中、调整值留空；不允许基于效应结果或收敛状态事后缩小家族。新增参考值、顺序、0/1、非法P及空家族测试；全套243项本地测试通过。说明见`audit/multiple_testing_adjustment_utility_review_2026-10-24.md`。此组件不拟合模型、不读取CHARLS个体数据；主检验家族K尚未冻结，实际CHARLS模型仍为0。

### 2026-10-24续：正式结果来源追溯门槛

结果表验证器现在只允许成功结果行在`data_release`中包含至少一个官方发布文件SHA-256，并在`software_versions`中包含生成代码的Git提交哈希；家族标记采用`family_id;K=<正整数>`，发布表必须保留K条假设（包括不可估计行），且BY/Bonferroni值须与完整家族重算一致。新增合成测试覆盖缺来源/提交、家族行数、不可估计成员和错误校正值。全套246项本地测试、Python编译和`git diff --check`通过。该改动只强化结果留痕和全家族校正，不拟合CHARLS数据、不生成真实结果，也不更改网站静态文件。

### 2026-10-24续：2013睡眠钟点 AM/PM 组件标注

复核2013官方问卷WB03/WB04版式与Codebook字段后，将每题 `_1/_2` 标为AM行的小时/分钟、`_3/_4` 标为PM行的小时/分钟；主字段保留`1=AM; 2=PM`。拆分字段的Codebook标签文字重复，因此目录同时注明必须对获准发行文件的数据字典/实际存储复核后才能拼接钟点。候选仍限定为“昨天”的单日回忆，不能解释为通常作息、睡眠时长或多日均值；问卷同一“昨天”模块中的WB05–WB15情绪题与睡眠时点没有明确先后，相关联只能作同日探索解释。未使用Codebook频数充当本项目样本量。更新了复现构建器、残余暴露审计、公开E目录JSON、CHANGELOG和本地审计；新增4项组件映射、同日解释与网站传播回归测试。`python scripts/build_ep_atlas_metadata.py --finalize-only`完整成功；全套250项Python测试通过，89项DO NOT ANALYZE锁逐项一致，Python编译、JavaScript语法和`git diff --check`通过。无受访者记录参与本次审计，正式关联模型和逐对完整样本量仍为0。

### 2026-10-24续：补全2013昨日情绪候选结局

官方问卷和Codebook确认WB05–WB15是同一“昨天的感受”题组，共11个分别提问的情绪项目，且使用相同1–5程度响应卡。已将旧目录缺少的9项补为独立表型候选，不反向计分、不合成总分或冒称已验证量表。最终化快捷流程现会先重建症状及官方值标签，并恢复独立的2013平衡测试资格门；避免目录刷新时遗漏上游标签或`pd001`。最终网站分片含11/11条目、11/11条目均有值标签及同日/未验证分母提示；`pd001`保留。最终化后候选概念E=1,150、P=297（含双角色），唯一E/P概念1,438，来源字段波次映射6,652；2013候选组合数132,082仅为元数据交叉组合数，不是人数、完整样本对或统计结果。全套254项Python测试、89项DO NOT ANALYZE锁一致性、Python/JavaScript语法及`git diff --check`均通过。审计记录见`audit/2013_yesterday_affect_item_set_review_2026-10-24.md`；未读取个人记录或Codebook频数，正式关联模型仍为0。代码提交`758c37d`已推送；GitHub Pages Deploy #112（run `40051537557`）及Validate run（`40053128463`）均成功。缓存绕过读取线上`catalog_p.json`、`health_symptoms_v1.json`及候选组合JSON返回HTTP 200，11项情绪标签/同日提示和`pd001`已核验；三份线上静态文件与提交版本逐字节一致。


### 2026-10-24续：2013官方权重文件版本闸门

官方Wave 2数据页确认2015-11-18版`Weights.dta`的发布SHA1为`22c4fc89df2e55fa8faf051e88830eebe0e035c0`。私有合并脚本现会在读取DTA前比对该官方SHA1，文件不符即停止；汇总QA同时留存官方SHA1与本地SHA-256。README和隔离目录交接说明已同步。新增合成文件哈希通过/拒绝测试；本机隔离`incoming_2013_weights`目录仍为空，因此没有读取或合并任何新个人数据，2013样本资格与权重门槛仍开放。全套255项Python测试通过；GitHub Validate #217（run `40053376860`）成功。该提交只改本地入库脚本和说明，不含Pages静态资产。
