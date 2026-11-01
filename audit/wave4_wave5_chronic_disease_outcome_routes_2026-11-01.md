# Wave 4 / Wave 5 chronic-disease outcome route review (2026-11-01)

## Purpose and scope

This is a questionnaire/codebook route review for possible cross-sectional disease outcomes in the 2018 and 2020 waves. It uses the official files already archived under `sources_official/`; it does not read participant records or report codebook frequencies. It creates no analysis-ready outcome and authorizes no cross-wave pooling.

The Wave 4/5 release review found no venous-blood laboratory module in these waves. A future later-wave atlas block therefore needs to use survey-measured outcomes such as self-reported disease history, with the phenotype explicitly described as doctor-diagnosed disease history rather than a laboratory-confirmed condition.

## Source-confirmed route facts

| Wave | Prior-wave state | Current-wave question | Response rule | Evidence |
|---|---|---|---|---|
| 2018 / Wave 4 | Questionnaire carries forward `Zdiagnosed[i]`, indicating a doctor-diagnosed disease at the last interview. | `DA007_i` asks whether a doctor has diagnosed the listed disease. The procedure routes this question to new respondents and returners not previously diagnosed; a prior positive is retained through the carried-forward state. | `1=Yes`, `2=No`. Use a routed current answer or a prior positive state; do not code a blank/skipped answer as No. | `CHARLS_2018_Questionnaire_extracted.txt`, section D, pp. 64–67; `CHARLS_2018_Codebook_extracted.txt`, `da007_*` and `zdiagnosed_*` labels. |
| 2020 / Wave 5 | The questionnaire preloads `ZDisease[i]` from the last interview. Previously diagnosed diseases follow the comparison route; diseases not previously diagnosed proceed to the new diagnosis question. | `DA003[i]` asks whether a doctor has diagnosed the disease. The official flowchart routes prior-disease cases through `DA002` and no-prior-disease cases through `DA003`. | `1=Yes`, `2=No`. A prior positive is retained; only an explicit routed `DA003=2` supports a No for a condition not previously reported. Other missing/routed states remain missing. | `CHARLS_2020_Questionnaire_English_extracted.txt`, DA Health Status section; `CHARLS_2020_Flowchart_Chinese_extracted.txt`, DA route; `CHARLS_2020_Codebook_extracted.txt`, `da003_*` and `zdisease_*` labels. |

The official route is the reason that a single current-wave question field is insufficient for a cross-sectional “ever doctor-diagnosed by this interview” variable among returning respondents. A carry-forward field alone is also insufficient because it misses new diagnoses reported since the prior interview. In Wave 5, `DA002=99` is a route-consistency flag requiring special treatment when a prior positive is also present.

## Codebook value-label cross-check (2026-11-01)

The archived official Wave 5 Codebook gives `DA002` labels `1=Better`, `2=Worse`, `3=Same`, and `99=Never Had the Disease`; it gives `DA003` labels `1=Yes` and `2=No`. Its carried-forward `ZDisease_i` entries are labeled as prior doctor-diagnosed disease and list the positive value `1=Yes`; they are not a two-category current-wave question. The Wave 4 `Zdiagnosed_i` entries likewise identify the carried-forward positive state as `1=Yes`, while `DA007_i` is the current routed yes/no item. These value-label checks agree with the route logic in the questionnaires and flowchart. In particular, only a routed current `DA003/DA007=2` supplies a No; a blank carried-forward field is not itself emitted as a negative outcome by the derivation utility.

This was a source-document check only. The later protected run separately verified the prepared-table hashes and source headers before deriving outcomes; exact respondent-level route counts remain on the server.

## Disease-slot reconciliation

The existing official concept crosswalk resolves the inserted 2020 Parkinson's item. Use disease labels, not matching slot numbers, to pair fields:

| Disease concept | 2018 current / prior field | 2020 current / prior field | Cross-wave treatment |
|---|---|---|---|
| Hypertension through memory-related disease (concepts 1–12) | `DA007_1_`–`DA007_12_` / `Zdiagnosed_1_`–`Zdiagnosed_12_` | `da003_1_`–`da003_12_` / `zdisease_1_`–`zdisease_12_` | Candidate label-matched set; confirm each source label and route before modeling. |
| Parkinson's disease | Included only in the 2018 memory-related disease wording/examples; no distinct 2018 diagnosis item. | `da003_13_` / `zdisease_13_` | Wave 5 standalone phenotype only; do not map to 2018 memory-related disease as equivalent. |
| Arthritis or rheumatism | `DA007_13_` / `Zdiagnosed_13_` | `da003_14_` / `zdisease_14_` | Same concept with shifted slot. |
| Asthma | `DA007_14_` / `Zdiagnosed_14_` | `da003_15_` / `zdisease_15_` | Same concept with shifted slot. |
| Prostate illness excluding cancer | Male-only `DA029` with separate new/returner routes | No equivalent standalone field identified | Keep as a Wave 4-only candidate, with its route-specific fields; exclude from a shared Wave 4/5 family. |

The Wave 4/5 field names above follow the archived official codebooks and are catalog candidates, not a substitute for verifying the actual protected release headers. The full legacy cross-wave mapping and caveats remain in `chronic_disease_concept_crosswalk_v2.csv`.

## Candidate, not yet frozen, derivation

For each disease concept and within each wave, build an explicit outcome with Yes, No, missing, and route-conflict states from the official prior-positive indicator and current routed answer:

1. **Yes:** prior-wave carry-forward indicates the disease, or the current routed doctor-diagnosis question is explicitly `1`.
2. **No:** the respondent is on the documented no-prior-diagnosis/current-question route and explicitly answers `2`.
3. **Missing/unknown:** neither a prior positive nor an eligible current yes/no response is established. Do not convert skip, absent module, proxy nonresponse, refusal, or unknown to No.
4. **Route conflict:** in Wave 5, a prior positive `ZDisease` paired with `DA002=99` (“did not have the disease in last interview”) contradicts the preloaded history. Keep this state separate for protected review; do not silently assign Yes or No until field semantics and the route are reconciled.

Harmonize by the official disease label and wording, never by the numeric slot alone. The Waves 4 and 5 questionnaires have separate disease lists and route variables; retain wave-specific source fields and a disease-by-disease wording crosswalk. Do not claim that the outcome is newly incident: the combined Yes state is prevalent cumulative self-reported doctor-diagnosed history as of the wave interview.

## Analysis-frame implications

- Preserve `Sample_Infor.crosssection` as the frame indicator and apply the verified wave-specific individual weight, `INDV_weight_ad2`, for a cross-sectional representative-sample analysis. The official guides state that released cross-sectional weights cover the main respondent/spouse sample, including proxy and partial interviews; missing outcome response still remains pair-specific missingness.
- The official guides say the released PSU information is continuous with earlier waves, while the protected metadata review found no released stratum or split-community final-PSU key. Under the user's selected working design, use the available `communityID` cluster with no invented strata and label WR Taylor variance as approximate.
- Derive age at the wave-specific interview date from source-verified fields; do not apply a blanket age cutoff unless the outcome/estimand requires a prespecified domain.
- Before model fitting, run a metadata-only input and field check, then protected outcome-state QA by route, cross-sectional eligibility, weight applicability, PSU support, and pairwise completeness. Keep exact counts and all row-level output in server-private storage.

## Protected derivation status (2026-11-01)

The route-aware derivation was run for the protected 2018 and 2020 prepared tables. The 2018 table retains 14 source-aligned disease concepts; the 2020 table retains 15, with Parkinson's disease kept wave-specific. A protected readback validator confirmed source ID order and uniqueness, cross-sectional frame, individual weight, community PSU, output hashes, and consistency between route status and emitted binary outcome. Exact counts and row-level outputs remain private. These are prepared outcomes, not association estimates or evidence of incident disease.

The next step is to register the 2018/2020 association families, including exposure crosswalk, age adjustment/domain, missingness rules, covariates, and complete-family multiplicity. The Wave 4/5 association families must be fitted and reported separately by wave; any atlas-wide multiplicity correction must include every prespecified hypothesis from all completed waves.

## Official source links

- [2018 CHARLS Wave 4 data and questionnaire](https://charls.charlsdata.com/pages/Data/2018-charls-wave4/en.html)
- [2018 CHARLS Wave 4 household questionnaire](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2018-charls-wave4/application/CHARLS_2018_Household_Questionnaire.pdf)
- [2020 CHARLS Wave 5 data and questionnaire](https://charls.charlsdata.com/pages/Data/2020-charls-wave5/en.html)
- [2020 CHARLS Wave 5 questionnaire](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_Questionnaire_English.pdf)
- [2020 CHARLS Wave 5 questionnaire logic flowchart](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_Flowchart_English.pdf)
- Wave 4/5 weight and frame details: `multwave_official_weights_blood_source_review_2026-10-29.md` and `multwave_frame_spine_build_gate_2026-10-30.md`.
