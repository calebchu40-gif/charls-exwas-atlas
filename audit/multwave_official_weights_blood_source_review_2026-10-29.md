# Multwave official weight and blood-source review (2026-10-29)

## Scope and privacy

This review records source-level facts from CHARLS's official Wave 2 release note, Wave 3 blood release note, and metadata-only checks of the corresponding account-gated archives. The archives and detailed machine-readable header report remain in the user's protected local/server intake. No participant-level records or derived association outputs were read, copied, or published. Stata header row counts are not analytic sample sizes and are intentionally omitted here.

## Intake status

The following account-gated official archives are present in protected local intake and were matched to the previously verified official source manifests:

| Wave/source role | Official document ID | Protected archive | Metadata-only finding |
|---|---:|---|---|
| 2013 weights | 318 | `incoming_2013_weights/2013_318_Weights.zip` | `Weights.dta`; separate cross-sectional/longitudinal sample indicators and weights; a cross-sectional biomarker weight is present |
| 2015 weights | 1152 | `incoming_2015_weights/2015_1152_Weights.zip` | `Weights.dta`; wave-specific household/individual and biomarker weight fields |
| 2015 blood | 2088 | `incoming_2015_blood/2015_2088_Blood.zip` | `Blood.dta`; includes `Blood_weight` and fasting-status metadata |

These archive/header checks establish file availability and metadata only. They do not establish respondent linkage validity, analytic eligibility, or a usable variance design.

## Official release-note implications

### 2013 follow-up

The Wave 2 release note distinguishes cross-sectional and longitudinal samples and weights. It warns that the two sample definitions are not interchangeable, describes separate cross-sectional weights with and without nonresponse adjustment, and states that the longitudinal weight adjusts follow-up participation conditional on baseline participation. It also releases a cross-sectional biomarker weight and explicitly does not release a longitudinal biomarker weight. A panel biomarker analysis therefore needs a separately justified target and nonresponse procedure; the cross-sectional biomarker weight cannot simply be relabeled as a panel weight.

The release note also documents Wave 2 identifier changes: baseline household and individual identifiers require specified padding/reconstruction to match Wave 2. Any linkage must implement and validate the official transformation wave by wave; direct raw-ID equality is not a safe join rule.

### 2015 blood follow-up

The Wave 3 blood release note says only cross-sectional blood weights are released because panel weights depend on analysis purpose. `Blood_weight` combines the individual cross-sectional weight with an inverse-probability adjustment for blood-collection response; the stated adjustment is capped at the 99th percentile. Thus it is the documented starting weight for a cross-sectional blood estimand, not a ready-made longitudinal blood weight.

The released blood variables include fasting status and the laboratory panel. The archive's metadata labels `bl_fasting` as 1 = Yes and 2 = No. This is verified for the 2015 field only; it does not resolve the undocumented numeric coding of Wave 1 `qc1_va003`. The Wave 3 note also specifies triglyceride top-coding metadata, which must be carried into outcome validity and sensitivity specifications.

## Analysis consequences

1. Keep each wave's source definition, sample flag, weight target, and blood-response adjustment explicit. Do not pool or harmonize weights by name alone.
2. Decide separately between a wave-specific cross-sectional estimand and a longitudinal/within-person estimand. For the latter, derive or justify follow-up and biomarker nonresponse adjustments using the relevant eligible frame; do not substitute a released cross-sectional biomarker weight.
3. Apply the age-45+ target as a survey domain where appropriate, preserving the full design for variance estimation. Confirm whether the chosen weight targets the intended cross-sectional population before fitting.
4. Reconcile official identifier transformations and blood-module joins before any merged analysis frame is accepted.
5. The currently unresolved PSU/strata/final-sub-PSU linkage and variance-method gate remains a stop condition. Availability of later-wave weights and blood metadata does not clear it, nor does it authorize association fitting.
6. Keep the Wave 1 fasting code unresolved until an official Wave 1 source is found. Never transfer the 2015 value labels backward.

## Sources

- [CHARLS 2013 Wave 2 data page](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/zh-cn.html) and the locally archived official Wave 2 release note (`sources_official/CHARLS_2013_Wave2_Release_Note.pdf`; extracted text is a search aid).
- [CHARLS 2015 Wave 3 data page](https://charls.charlsdata.com/pages/Data/2015-charls-wave4/zh-cn.html).
- [CHARLS Wave 3 Blood Data Release Note](https://charls.pku.edu.cn/en/data/Blood2015.pdf), version dated June 2019; locally archived as `sources_official/CHARLS_2015_Blood_Release_Note.pdf`.

## Gate status and next action

Wave 2 weights and Wave 3 weights/blood are now present and header-reviewed in protected storage. Source and measurement metadata have improved, but the project's real-data model gate remains closed pending the Wave 1/target-wave sampling-frame, age-domain, weight-applicability, respondent-to-final-PSU, variance, frozen-analysis, and independent-method-review decisions. Next, add explicit wave-specific weight/estimand entries to the locked analysis specification and crosswalk only the public field metadata; do not merge respondent records or fit associations until all preceding gates pass.
