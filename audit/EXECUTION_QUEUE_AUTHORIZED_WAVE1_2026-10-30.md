# Authorized Wave 1 execution queue and current gates

**Status date:** 2026-10-30  
**Purpose:** Operational queue after the user confirmed ownership/authorization of CHARLS items 123/117/118/201, selected the community-clustered no-strata Taylor approximation (Option A), and authorized private-server analysis.

## Controlling decisions

- Official Wave 1 inputs are authorized for this project. Their identity and metadata preflight are recorded in the private source manifest. No access credentials are stored in the repository.
- Individual-level data, pair-level counts, exact QA and model results stay under the server's owner-only `private/` tree. Only reviewed, disclosure-cleared aggregates may be copied to the public site.
- Option A is the user's chosen **approximate** variance plan: released `communityID` PSU, no invented strata or FPC, with-replacement Taylor linearization. It omits known features of CHARLS's multistage PPS design and the respondent-to-final-subcommunity membership map. It is not the full CHARLS design and is not known to be conservative.
- The operational pilot registry is the fixed 105 coefficients: one `i017` contrast plus six `i022` fuel contrasts, each across 15 routine blood outcomes. Outcome handling is outcome-specific: the seven glucose coefficients remain registered but blocked until authoritative Wave 1 fasting coding is documented; the seven triglyceride coefficients are candidates for an all-observed-blood-sample lipid estimand under non-fasting lipid guidance, pending methods approval; the other 91 coefficients remain pending their own outcome-rule and methods review. The pilot is nested inside K=150; final multiplicity counts all 240 prespecified K150/K90 hypotheses once, including non-estimable hypotheses in family size K (which receive no adjusted p value). A numeric `p=0` remains a valid p value for adjustment.
- Keep the **target population** distinct from the **observed design sample**: the official guide describes a target of 17,708 baseline main respondents and spouses, while 11,847 blood samples were collected. The released Blood records with finite positive `bloodweight` form the observed weighted respondent sample; `bloodweight` adjusts toward the stated target. Do not construct a 17,708-row model design by inserting nonrespondents without observed outcomes.
- Age-domain implementation uses the observed positive-`bloodweight` sample as the survey design data, estimates the lower-bound age-45+ domain as primary, and predeclares upper-bound age-45+ plus all observed blood respondents as sensitivities. Age-domain membership is separate from age-midpoint model adjustment. This requires a frozen plan and methods review and is not a claim about all Chinese adults aged 45+.

## Completed prerequisites

1. Source identity confirmed by the user and stored in the protected manifest; metadata-only preflight succeeded.
2. The Wave 1 person table and Blood-to-`bloodweight` linkage were reconstructed and source-bound in private storage.
3. The lunar date converter was compared against the official CHARLS mapping tables. A private age-interval candidate and aggregate QA exist; uncertain ages are not silently assigned to either side of 45.
4. The 105-coefficient availability audit was run privately. It is availability QA only, not model N, valid-outcome screening, or association evidence.
5. Header review found no attached value-label sets on the planned Blood outcome fields or `qc1_va003`. The official materials reviewed do not map Wave 1 fasting numeric codes. This blocks glucose and fasting-restricted sensitivities, but does not automatically block outcomes that do not require fasting; triglycerides have a separate all-sample candidate rule that still needs methods approval.
6. Static registry review confirms 150 K150 + 90 K90 = 240 unique coefficients and the pilot is nested in K150.

## Work queue and stop conditions

### W1 — Outcome data-quality profile (complete; private only)

Read only the 15 predeclared outcome columns from the authorized Blood file. The restricted aggregate profile is at `private/qa_outputs/wave1_biomarker_value_profile_private.json` on the server (mode 600). The scan found no negative values, nonfinite values, or numeric parsing failures; some outcomes have observed extremes beyond a limit in the Guide assay-method table. Those are diagnostic flags only, and no observations were filtered. Exact field summaries remain private. No identifiers, weights, or association models were used.

### W2 — Freeze source-based outcome rules and age/frame semantics

For every outcome record source field, unit, storage type, Stata missing handling, any documented special codes, measurement/assay caveat, transformation (default none), and unresolved issue. If official sources do not define a numeric validity boundary, retain that uncertainty explicitly; do not invent one from quantiles or assay detection range. Reconcile the age target and frame against the frozen 45+ domain decision. Keep glucose coefficients blocked until an authoritative Wave 1 fasting mapping is available; evaluate triglycerides under the explicitly non-fasting lipid candidate estimand, subject to methods review. Do not transfer Wave 3 fasting codes to Wave 1.

Before freezing M1/M2, reconcile them to the covariate DAG. The current candidate primary adjustment set must evaluate age nonlinearity, sex, education, and verified community `urban_nbs`; the older draft that reserved education/urban context for M2 is not the freeze candidate. Verify education coding/routes, community linkage, and complete-case estimand before freezing. Keep SES, migration, smoking/diet, BMI, diagnosis and treatment out of the generic core unless a pair-specific, predeclared causal rationale supports them.

A protected aggregate-only support audit has been added for the blood-weighted observed sample and the candidate lower-age-bound domain. It reads only `rgender`, `bd001`, `urban_nbs`, `communityID`, `bloodweight`, and age interval keys; it writes category/cluster counts only to the server's mode-600 QA path. It does not read biomarkers, write respondent rows, or estimate associations. Review its private output before selecting education categories or freezing complete-case rules.

**Official covariate coding review (2026-10-30):** visual inspection of the relevant CHARLS Codebook/questionnaire pages confirms `rgender` documents codes 1 (male) and 2 (female), and the education item documents integer response codes 1–11. Treat values outside those documented mappings as unclassified/missing for candidate modeling; do not infer an additional sex category from a raw numeric value. The PSU release labels `urban_nbs` 0/1 as rural/urban; this is community context, not a variance stratum. A five-level education grouping is being evaluated only as a sparse-category support candidate: codes 1–3, 4, 5, 6–7, and 8–11. It is an analytic recoding, not an official CHARLS category and is not frozen. The private audit now reports joint age/sex/education/community-context completeness and group-level cluster support; inspect only the private report before deciding whether it is stable enough to present for independent review.

The scale-up runner now accepts explicitly grouped categorical covariates as `groups` plus a `reference_group`, while retaining the original exact-level format. It rejects overlapping codes and an undeclared reference group. This makes the provisional education grouping executable without hand-editing respondent rows; approval and final coding remain separate gates.

**Outcome header follow-up (2026-10-30):** the private metadata-only audit found no attached value-label sets and no declared Stata tagged-missing metadata for the 15 planned biomarkers or `qc1_va003`. This does not rule out finite numeric sentinel codes and does not establish valid-value boundaries. Continue to keep numeric validity/special-code decisions unfrozen unless an official Wave 1 source rule is located or a reviewer approves the explicitly conservative raw-finite candidate rule.

**Official source review (2026-10-30):** the 2011 Blood Users' Guide states that participants were asked to fast overnight, non-fasting samples were still collected, and fasting status was recorded, but the reviewed official 2011 materials do not map `qc1_va003` numeric codes. The 2015 release note lists Wave 3 `bl_fasting` and a triglyceride top-coding flag; these cannot be carried back to Wave 1. A private, 15-outcome handling-candidate JSON records raw field/unit, assay metadata, unresolved finite-sentinel question, and provisional raw-finite/no-range-filter proposal. The updated policy blocks the seven glucose coefficients pending authoritative fasting-code mapping; seven triglyceride coefficients are all-observed-sample candidates under non-fasting lipid guidance, pending methods approval; the other 91 remain pending outcome-specific value-rule review. Nothing is approved or frozen. See [`wave1_fasting_status_source_reconciliation_2026-10-30.md`](wave1_fasting_status_source_reconciliation_2026-10-30.md).

### W3 — Freeze estimator and diagnostic rules

Bind the observed finite-positive-`bloodweight` respondent sample, domain indicator, community PSU, no-strata WR Taylor approximation, coefficient IDs, M1 primary formula, M2 sensitivity formula, full prespecified multiplicity family, singleton-PSU rule, degrees-of-freedom handling, effect scales, and sensitivity analysis to source and prepared-table hashes. Record the 17,708 target population separately from the observed Blood sample. Add a clear caution that results are approximate and that the final subcommunity PSU map is unavailable.

Static runner review found and corrected two mismatches: the previous code reused one age field for domain classification and model adjustment, and its generic eligibility field did not encode the observed blood respondent sample. The runner now reads age-interval lower/upper fields separately, derives a midpoint for model adjustment, applies age domains independently, and selects observed blood respondents by finite positive `bloodweight`. Target population and observed sample are recorded separately. The rule still needs to be frozen and reviewed.

**Age-frame wiring correction (2026-10-30):** the Wave 1 model runner had inherited an obsolete age-table path. The official source-bound interval candidate is a separate private file. The runner now points to the source-reviewed Wave 1 rebuild and the official age-interval candidate, while the provenance gate checks the candidate against the current manifest, prepared person hash, Weight hash, official age-input QA and interval-derivation QA. The age-candidate hash is included in the model-config binding. The aggregate-only frame audit now reports lower-bound 45+ and upper-bound 45+ domains separately, along with threshold-crossing intervals and unmatched join keys. This fixes plumbing; it does not substitute for review of the age method or target estimand.

### W4 — Review gate before association fitting

**Draft prepared** at `private/analysis_review/wave1_preanalysis_review_packet_20261030.md` (mode 600 on the server and stored in the local protected review directory). It summarizes decisions, evidence and open review items without participant values or exact QA counts. Complete it with final source/table/config hashes after W2/W3. Association fitting remains fail-closed until all computational gates pass and an independent methods review is recorded. An internal code check is not represented as independent review.

### W5 — Pilot and expansion

After W4 approval, fit the fixed 105-coefficient pilot privately, run model/weight/PSU/singleton/influence diagnostics and predeclared sensitivities, then review reproducibility. If sound, run remaining K150/K90 coefficients without duplicating the pilot; apply the frozen family-wide correction once. Continue wave-specific source/frame/weight/design review before adding other waves.

### W6 — Release

Prepare only disclosure-cleared aggregate outputs for the site. Confirm result files, cell thresholds, suppression and metadata before enabling the public result endpoint. Validate the deployed pages and record the public commit and URL.

## Immediate schedule

- **Completed in the current execution block:** visually reviewed official Codebook/questionnaire coding for sex and education; added and ran the private, outcome-free audit of joint core-covariate completeness and candidate education-group cluster support; documented the count-free review in the protected packet. No participant-derived counts or models were committed.
- **Next execution block:** complete the outcome-rule review against the private candidate JSON, inspect design/weight diagnostics, and bind proposed rules to source/table hashes in the draft model. The Wave 1 fasting code remains unresolved; do not transfer Wave 3 coding. The candidate support audit is complete, but outcome validity, age target, covariance/variance specification and pilot configuration remain subject to independent methods review. No association fitting while those gates or independent review remain pending.
- **After review approval:** first model run and full QA; then K150/K90 expansion. Server compute time is not expected to dominate; official documentation gaps and review decisions are the uncertain calendar-time items.

## Progress reporting

Keep the project goal and recurring continuation active. Report only material advances, a gate that requires the user's action, a failure, or completion. Do not label data preparation, synthetic runs or value profiles as fitted CHARLS associations. Current public formal-association count remains **0** until W4 is approved and a real model completes.

### 2026-10-30 current reconciliation

The outcome-specific fasting policy above supersedes older notes in this file that described all 14 glucose/triglyceride coefficients as blocked. The current candidate state is: glucose 7 blocked pending an authoritative Wave 1 `qc1_va003` mapping; triglycerides 7 all-observed-blood-sample candidates pending methods approval; other 91 pending outcome-specific validity review. No coefficients have been approved or fitted. The server's private review packet reflects this same candidate rule, but the hash-bound readiness approval is still absent. Do not infer that the source or design gate passed merely because the user confirmed source identity and selected Option A.
