# 2026-10-30 Clarify lunar DOB conversion uncertainty

- Read the pinned CHARLS-maintained `lunar2solar` ado/help. Its `leap` switch selects a separate table for the whole invocation, while the reviewed Wave 3 DOB route records solar/lunar basis but no per-person leap-month marker. Documented a candidate-set age-interval approach and validation gates; it remains unapproved and no participant DOB was read or converted. No age-specific domain or formal association model was produced.

# 2026-10-30 Withdraw preferred single-stage variance candidate

- Re-read the official CHARLS sample-design page and reconciled it with the 2015 release inventory. The design includes county-level stratified systematic PPS, community/neighborhood PSUs, and sampled sub-neighborhoods in split communities; public 2015 files reviewed here do not provide a complete respondent-level final-PSU/strata map.
- Retracted the earlier preference for county-prefix-only Taylor variance. Neither county-prefix nor parent `communityID` is currently an approved single-stage design. Formal association models remain 0 pending complete design review and other source/eligibility/method gates. No microdata were read in this documentation review.
# 2026-10-30 Refresh official methods inquiry draft

- Marked the older support draft as historical because its Wave 2 weight-file request is obsolete. Added a current unsent draft focused on unresolved Wave 1 variance/PSU, bloodweight target, fasting-code and lunar-age definitions, plus later-wave design fields. It contains no microdata or account credentials and was not sent.

# 2026-10-30 Correct conservative Wave 1 age interval bounds

- Broadened provisional year-only age lower bounds for lunar or calendar-unresolved birth dates to account for a possible one-year lunar-to-Gregorian birth-year offset plus unknown interview day. Regenerated the protected candidate age intervals; no participant-level output was added to the repository. Method and survey-design gates remain open.

# 2026-10-30 Recheck fasting-code source status

- Rechecked the live official Wave 1 documentation directory and Blood Users' Guide. The fasting-status variable is documented but its 2011 numeric mapping remains unpublished in the reviewed official materials; a third-party `1=Yes, 2=No` label remains a lead only. The glucose/triglyceride routing gate stays closed.

# 2026-10-30 Map variance candidate to current runner

- Statically confirmed the Wave 1 runner can represent the proposed county-prefix cluster, blood-specific weight, explicitly empty strata, and with-replacement Taylor approximation, with an explicit limitation label. This removes an implementation uncertainty only; survey-design approval and all model gates remain open.

# 2026-10-30 Align public disclosure with CHARLS terms

- Recorded CHARLS academic/noncommercial, no-microdata-publication/transfer, disclosure, acknowledgment, and citation terms in a public-safe audit note. Updated the site footer to the required Wave 1/2 acknowledgment wording and current official Wave 1 data-directory link; no microdata or association outputs were added.

# 2026-10-30 Reconcile current Wave 1 methods review packet

- Corrected the independent review packet so its current 105-hypothesis candidate uses the full official blood target and `bloodweight`, with age 45+ only as a secondary survey domain. The outdated age-45+ primary target, Harmonized CHARLS age, and community-only variance fit are explicitly historical and cannot be used to populate a current readiness record.
- Marked the 2026-10-26 follow-up plan as a historical snapshot and linked the active plan, because several old statements still said Wave 1 inputs were missing. No data or result files were read, copied, or changed; no association model was run.

# 2026-10-30 Clarify Harmonized CHARLS survey-design wording

- Rechecked the official Harmonized CHARLS Codebook statement that design-adjusted standard errors are supported “where provided by CHARLS.” The wording does not itself provide Wave 1 variance identifiers or an executable design declaration, so the Wave 1 variance gate remains pending independent review.
- Re-ran metadata-only intake gates for the local Wave 1 source set, Wave 2 weights, and Wave 3 blood archive; source/header checks passed without reading respondent values. Public site remains catalogue/methods only, with no association-results payload.

# 2026-10-30 Clarify Wave 1 blood outcome measurement rules

- Record that the official guide includes non-fasted blood samples and says fasting status is recorded, while reviewed sources do not decode 2011 `qc1_va003` values. Do not infer fasting exclusions, transformations, or extreme-value filters from guide distribution summaries. Keep continuous outcomes as the primary atlas candidates; guide clinical cutoffs are not default binary ExWAS outcomes. Keep Cystatin C eligibility separate. No respondent values or association results were used.
- Reconcile the older Wave 1 estimand-gate memo so the superseded age-45+ primary candidate cannot be mistaken for the current review proposal: full official blood target (main respondents and spouses) with `bloodweight`, and age-45+ as a secondary domain. This remains pending independent review and is not frozen.
- Mark the earlier 105-pair pilot specification and outputs as historical exploratory work; define the current 105-pair family and target only as a candidate for re-freezing after age, design, outcome-rule and independent-review gates pass.
- Refresh the multi-wave readiness matrix and older Wave 2 intake notes: official 2013 sample flags/weights are now in the protected Wave 2 rebuild, and 2015 Blood/Weights/Sample_Infor plus 2018/2020 Weights/Sample_Infor have passed source/header intake. These inputs do not resolve wave-specific eligibility or variance design.

# 2026-10-30 Refine Wave 1 variance review candidate

- Reconciled the county-prefix key evidence with the official four-stage, systematic-PPS sample description and documented the strongest remaining national-inference approximation for independent review: county-prefix as a top-level cluster with no invented strata/FPC, using the blood-specific weight only for its defined target.
- Added a separate selected-county conditional community-cluster sensitivity and stated its omitted first-stage variance. Both remain unapproved; the design gate remains closed, and no association model was run.
- Added explicit limits on national/design claims, split-community handling, complete-case weighting and the required independent decisions.

# 2026-10-30 Prepare direct synthetic parity audit for CHARLS lunar lookup

- Added a Stata-only synthetic date-grid exporter that invokes the pinned official CHARLS `lunar2solar` ado/Mata lookup without opening participant data, plus an aggregate-only Python comparison mode that validates source hashes, key coverage and table dimensions.
- Documented the execution boundary and protected-output handling. The workflow is prepared but not executed because a Stata runtime is not available on the checked workstation or private server; official matrix parity and the age-method gate remain unresolved.
- No participant data, age derivation or association model was used. Formal approved association count remains zero.

# 2026-10-29 Reconcile current input and public-site status

- Rechecked the protected Wave 1 local/server intake, server project plan, GitHub main, and deployed Pages. Server Wave 2 All Data/weights and Wave 3 sample-information/weights/blood inputs are present in private intake; this was a presence check only.
- Confirmed the public home and candidate-pair index respond with HTTP 200, the deployed app is v194, and the approved association-results payload is still absent (HTTP 404). The site continues to show zero formal association models.
- Clarified the README and active plan so present input/site status is distinct from earlier dated records. The Wave 1 age and survey-design gates remain open; no participant values, association models, or tests were run.
- Diagnosed the repository-boundary CI failure: a public metadata-only wave/module gate crosswalk was missing from the reviewed CSV/TSV path allowlist. Reviewed its schema and metadata-only generator, added that exact path, and confirmed the boundary guard now passes locally (1,292 tracked paths; 189 reviewed delimited-text files). No respondent-level content was inspected or added.
- The next CI stage exposed stale synthetic fixtures/expectations after the age-source readiness gate and 2013 source review were strengthened. Updated the synthetic age-gate fixture to include the required source/derivation evidence fields and adjusted existing anthropometry expectations to recognize the added official 2013 release-note anchor and the still-unapproved analytic status. No test suite was run locally.
- CI then identified that the K150 registry audit incorrectly required one route string for an entire family. The predeclared cooking-fuel rows carry a distinct missingness/eligibility caution, and K90 carries an explicit I020-to-I021 route. Updated the metadata-only audit to validate the route rule by registered source field and report route-rule coverage; the local registry audit now passes structurally, with every hypothesis still marked unapproved.
- Updated the companion public-metadata cross-check to apply the same field-specific K150/K90 route rules. Its local metadata-only run now passes: all 240 planned cells match the public biomarker/exposure metadata and routing notes, while model approval and results remain false/absent.

# 2026-10-29 Document Wave 1 age input sources

- Added a fail-closed protected preparation script that verifies reviewed source hashes and headers, checks respondent-key uniqueness, and joins only official Wave 1 birth-date/calendar/conditional-age fields with interview year/month. The person-level age-input file and exact QA remain in controlled private storage. Conversion and survey-design gates remain unresolved; no age or association model was fitted.
# 2026-10-29 Document Wave 2 anthropometry route and sentinel codes

- Rechecked the official Wave 2 Biomarker Questionnaire against the Codebook and protected bundle headers. Documented 993/999 as nonmeasurement statuses and kept QI/QJ/QK/QL/QM measurement context and the <150 kg weight eligibility route separate from the outcome values.
- Flagged the inconsistent QI001 “breathing test” stem within the standing-height section; it must not define the height denominator alone. Updated the public-safe metadata crosswalk and static JSON without exposing private counts or participant data.
- Final numeric validity, pair eligibility, age construction, design variance and methods review remain open; no association models were fitted.

# 2026-10-29 Rebuild the protected Wave 2 respondent frame

- Rebuilt the Wave 2 respondent-level preparation table from the checksum-verified official All Data bundle on the protected server. Unique-ID, source module joins, sample-flag/weight presence and anthropometry coverage QA were written only to protected storage; no person-level data or QA counts were added to the repository.
- Reviewed the official CHARLS sample description and Wave 2 questionnaire routing: the target includes 45+ selected respondents and their spouses, and Wave 2 adds the reserved 43–44-at-baseline refreshment respondents and partners. Do not apply a blanket current-age-45+ filter to all participants. `ba004` is asked only when birth date is unknown/refused and is not a universal age covariate.
- Updated the Wave 2 gate memo and active plan. Age construction, pair eligibility, weight target, survey variance, independent review and model approval remain open; no association models were fitted.

# 2026-10-29 Restrict permissions on private preparation outputs

- Tightened `prepare_charls_wave_tables.py` so POSIX-server private output and scratch directories use owner-only directory permissions, while prepared respondent tables, temporary Stata outputs, QA CSVs, collision maps and manifests use owner-only file permissions.
- Applied restrictive permissions to the Wave 2 artifacts already created. The age QA labels `ba004` as conditionally asked and not age-ready, rather than interpreting its structural skips as missing ages or an age-domain count.

# 2026-10-29 Verify the protected Wave 2 All Data bundle

- Located official release item 321 (2013 Wave 2 All Data, release 2015-11-18) in the server's protected raw intake, verified it against the official release checksum recorded in the verified manifest, and staged a permission-restricted copy in a Wave 2-specific private intake folder.
- Listed archive members and used metadata-only Stata header reads for the Biomarker, Weights, PSU and selected questionnaire modules. The Biomarker header contains the five documented anthropometry candidates; the bundled Weights header contains `crosssection`, `longitudinal` and `Biomarker_weight`. No participant values or IDs were read, no merge or association model was run.
- Updated the Wave 2 source/weight gate memo, active plan, and anthropometry catalog builder/status. Pair coverage, route/value validity, age/frame eligibility, variance design and independent review remain open. Formal association models remain 0.

# 2026-10-29 Verify Wave 2 anthropometry module and weight linkage

- Extended the anthropometry source updater to verify that the official Wave 2 Release Note identifies `Biomarker.dta` as anthropometric measurements; updated Wave 2 source statuses to distinguish official module documentation from unverified local release-archive/header provenance.
- Added a gate memo for the five Wave 2 anthropometry candidates and the document-backed cross-sectional `Biomarker_weight` target. Pair-level missingness, sample/age domain and survey variance remain unresolved; no models were fitted.

# 2026-10-29 Correct Wave 2/3 public wave overview

- The public wave timeline incorrectly said Wave 2 collected no biomarkers and Wave 3 blood data were locally absent. It now distinguishes Wave 2 anthropometric Biomarker measurements from venous-blood laboratory testing and reflects the protected Wave 3 archive intake/preflight without implying analysis approval.
- This is a documentation correction; no individual data or private intake identifiers were added.

# 2026-10-29 Clarify Wave 2 anthropometric biomarker weight target

- The official Wave 2 release note identifies `Biomarker.dta` as anthropometric measurements and describes a cross-sectional `Biomarker_weight` adjusted for biomarker response; it does not provide a longitudinal biomarker weight.
- Updated the wave/estimand matrix, module-level crosswalk and deterministic metadata builder to show this as the document-supported candidate only for Wave 2 cross-sectional pairs involving a Biomarker-module field. Pair eligibility, exact field placement, sample/age domain and variance remain open.
- No respondent values, merges, models or tests were run.

# 2026-10-29 Bound the CHARLS forum variance guidance

- Added a source-qualified note on the CHARLS data-user forum administrator's historical response: it describes multistage PPS and says the clustering level depends on the research question, but does not specify Wave 1 strata/PSU variables or endorse the proposed code in that thread.
- Kept the formal design gate closed; the forum post is contextual user-support guidance, not a complete variance specification or independent methods approval.

# 2026-10-29 Correct public blood catalog intake wording

- Updated the public blood catalog and its deterministic builder to reflect the verified protected-source intake and metadata-only preflight for 2011/2015, while keeping participant records, module weights, eligibility, valid values and transformations explicitly unreviewed.
- Removed a stale site statement that the 2015 blood archive was absent. No private path/hash, participant values or association results were added to the public bundle.

# 2026-10-29 Map the wave weight matrix to the current runners

- Added a static compatibility audit linking the wave-specific target/weight matrix to the actual Wave 1 pilot and K150/K90 runners, configuration templates, and the absent Wave 2–5 association runners.
- Clarified that the historical Wave 1 pilot is hard-coded and exploratory, the scale-up runner is fail-closed behind a frozen design/readiness record, and generic template fields do not constitute an approved analysis configuration.
- Updated the active plan and matrix cross-reference. No respondent records, private outputs, association models, or tests were read or run.

# 2026-10-29 Correct the Wave 3 blood catalog intake status

- The blood biomarker crosswalk still described the official 2015 blood archive as locally absent. Reconciled the catalog against the protected local intake and existing metadata-only preflight record, then corrected the status for its 18 Wave 3 analyte entries.
- Clarified in the active plan and runner compatibility audit that the source archive is present while analysis eligibility, weight applicability, and survey-design gates remain open. No respondent values or private result files were read.

# 2026-10-29 Build the wave/module estimand and weight gate crosswalk

- Added a deterministic metadata-only builder and 60-row wave/module crosswalk connecting candidate E/P/C source fields to wave-level sample-marker and weight starting points, plus explicit module-level review gates.
- Documented that catalog field counts are not participant N, complete-case pairs or model counts, and that repeated candidate weights do not establish module applicability. No CHARLS microdata, private outputs, association models or tests were accessed/run.

# 2026-10-29 Reconcile Wave 1 candidate sources and questionnaire routes

- Reconciled the 240 planned K150/K90 registry rows with the user-confirmed protected source-identity review, official Wave 1 questionnaire/Codebook and metadata-only prepared/Blood headers. Corrected source statuses to distinguish authenticated archive and header key presence from unreviewed response values, linkage, validity and eligibility.
- Clarified the `i020` heating route: Yes skips `i021`, No routes to it; K90 is restricted to that routed subdomain. Preserved the absence of an explicit 2011 no-cooking code for `i022`.
- All rows remain `planned_not_approved`. No participant values, models, tests or private results were accessed.

# 2026-10-29 Align the Wave 1 blood crosswalk with verified source metadata

- Matched all 17 Wave 1 blood-crosswalk field keys to the protected official Blood-file header using metadata-only reads and updated the outdated source-status text.
- Kept target/weight applicability, valid-value rules, special codes, transforms, age-stratified cystatin C selection and fasting-code interpretation explicitly unresolved. No respondent values were read.
- Rechecked the current official Wave 1 documentation inventory; it still lists the general Codebook and Blood User Guide without a dedicated `qc1_va003` codebook. The fasting mapping remains unresolved.

# 2026-10-29 Extend official Wave 1 fasting-code source review

- Searched the archived official physical-examination questionnaire text and the complete 2011 Blood Guide text layer for `qc1_va003` and fasting response codes. The questionnaire provides no numeric field mapping; the guide describes fasting status and non-fasting measurement risk without code definitions.
- Updated the fasting-source memo and active plan. The code mapping remains unresolved; no participant records were consulted and no analysis was run.

# 2026-10-29 Reconcile svy multistage and ultimate-cluster documentation

- Reviewed official svy documentation for GLMs and multistage designs. The package can construct three-stage sample/weight chains; its documented variance approach uses first-stage PSU totals within strata (ultimate-cluster), while lower-stage stratification affects weights rather than variance strata. GLM replication is opt-in.
- Clarified that this does not recover CHARLS county strata or split-community respondent linkage, and does not approve a community-level approximation. Updated the review matrix and active plan; no models or tests were run.

# 2026-10-29 Corrected the svy package versus project GLM capability statement

- Verified the protected local environment pins `svy==0.35.0`. Its `Design` schema exposes PSU/SSU, replicate-weight and two-stage population-size fields, and its GLM supports opt-in replication. This CHARLS runner still builds one PSU, hard-codes Taylor and rejects replicate weights. Static inspection shows the GLM Taylor backend receives a single stratum/PSU/FPC and the regression FPC path ignores SSU information. Official package docs confirm replication is opt-in and do not supply CHARLS design inputs.
- Corrected the earlier broad statement that the survey package itself lacks multistage structures. The remaining blocker is the released CHARLS design linkage plus this project's particular GLM path; no analytic model or test was run.

# 2026-10-29 Review Wave 1 runner survey-design limits

- Static review confirmed the scale-up runner takes one PSU field and supports Taylor linearization only; replicate-weight configurations fail closed. The current API path does not encode multistage PSU variance, stage-specific PPS, FPC, or phase variance decomposition.
- Documented that the community-cluster fallback is not automatically approved by runner compatibility, and that a methods reviewer must define its estimand and variance interpretation or request an approved multistage implementation. No model or tests were run.

# 2026-10-29 Complete Wave 1 biomarker outcome scale metadata inventory

- Added a 15-outcome readiness table with Wave 1 fields, units, guide-reported assay ranges, and explicit distinction between assay range and approved analytical validity limits.
- Corrected the stale 2026-10-27 intake statement via an addendum; all four official input roles are now present and source-confirmed, while survey-design and outcome-review gates remain unresolved.
- Reviewed Blood Stata variable/value-label metadata only; requested assay and fasting fields have variable labels but no attached value-label sets. No respondent observations or association models were read/fitted.

# 2026-10-29 Reconcile official Wave 1 sampling stages and weight scope

- Rechecked CHARLS's official sample-design page and Wave 1 User's Guide: confirmed county-level region/urban-rural/GDP sorting/stratification, PPS stages, 30 large communities split into sub-neighborhood PSUs, and the sub-neighborhood-share contribution to weights.
- Clarified that biomarker nonresponse weights support weight selection but do not supply respondent-to-final-PSU mapping or resolve design variance. Updated the independent review packet; no real-data associations were fitted.
- Added the county-level PPS stage as a separate review item; the PSU file's released metadata has geographic names and area classifications but no clearly identified sampled-county or variance-stratum code. Reassessed whether a nested county/community approximation can be justified before using community-only clusters.
- Protected PSU-key topology QA found province/city labels are not a one-to-one county sample-unit crosswalk. Exact aggregates remain only in the local restricted workspace; public methods docs record the non-identifying implication and reject deriving county strata from names.
- Cross-checked the 2011 official Codebook PSU section: it lists communityID, province, city, NBS urban/rural and area type, with no county sample-unit ID or explicit variance-stratum field. Added the precise scope and page reference to the official-design inventory.

# 2026-10-29 Review official fasting-code documentation for Wave 1 pilot

- The official Blood User Guide confirms that fasting status is recorded and that glucose can be higher in non-fasting samples, but the official source material reviewed does not map `qc1_va003` numeric codes. The released Stata field has no value-label set, and the searchable official 2013 CodeBook does not contain this Wave 1 blood field. The official 2015 CodeBook maps the analogous `bl_fasting` field to 1=Yes, 2=No; this adjacent-wave evidence is not assumed to establish 2011 coding.
- A third-party variable index suggests `1=Yes, 2=No`; recorded only as an unverified search lead, not used to decode CHARLS records or authorize model fitting. The gate remains closed pending an official mapping and frozen glucose/triglyceride handling.
- Added `audit/wave1_fasting_code_source_review_2026-10-29.md` and linked the finding from the active plan and independent review packet. No participant values were inspected; no association was fitted.

# 2026-10-29 Reconcile pilot and scale-up hypothesis-family scope

- Audited the public hypothesis register and runner: historical K=105 is the water plus cooking-fuel exploratory subset, while current registered scale-up consists of K=150 household environment and K=90 heating-route families (240 candidate hypotheses, not sample size).
- Clarified that exploratory M0/M1/M2 runs are documented historically, while zero refers to models that have cleared current source/design/frozen-plan/method review and are eligible for formal or public use.
- Documented runner gaps: only one primary model configuration is currently implemented; fasting adjustment is unsupported; batch-adjusted p-values are not final atlas-wide correction. No CHARLS records/results were opened or fitted.
- Added `audit/wave1_family_runner_scope_review_2026-10-29.md`; updated the active plan.

# 2026-10-29 Check official Wave 1 design-file inventory

- Reviewed the official Wave 1 baseline data/document page: it lists PSU, Weight, Community and Blood products but no separate baseline Sample Information, replicate-weight or variance-stratum file. Reviewed the later Wave 4 guide's definition of Sample_Info to avoid assuming that a later-wave status/date file is a baseline PSU crosswalk.
- Recorded scope limits and implications in `audit/wave1_official_design_file_inventory_review_2026-10-29.md`. The PSU/variance gate remains unresolved; no model was run.

# 2026-10-29 Review Wave 1 blood estimand and unresolved PSU variance design

- Added an official-source review of the Wave 1 blood target, dedicated `bloodweight`, 45+ domain estimation, unrestricted-age spouse enrollment, and the separate Cystatin C assay subsample. Non-blood phenotypes still require their own module-specific eligibility and weight review.
- Recorded that CHARLS documents 30 large communities sampled through sub-neighborhood PSUs, while the reviewed released fields do not identify respondent-to-sub-PSU mapping or an explicit variance stratum/replicate weight. The survey-design gate remains closed; no association model was fitted and no CHARLS-derived counts or output files were published.
- Updated the execution plan with the next concrete action: search for documented sub-PSU/variance fields, then have a clearly labeled community-PSU approximation independently reviewed if official details are unavailable.

# 2026-10-29 Make the active Wave 1 work visible and repair the protected rebuild

- Updated the linked execution plan to show the actual current stage: the Wave 1 protected preparation table has been rebuilt, and sample-frame/survey-design review is now underway. It lists the next gates through the 105-model pilot, K=150/K=90 expansion, multiplicity review, disclosure review, and site release.
- Fixed Stata export for entirely missing fields by retaining the fields and labels as numeric missing values; added a guard against empty respondent tables. The script was run against the user-authorized source files only in protected server storage. No CHARLS data, participant-level outputs, or association results were added to GitHub or Pages.
- Formal association models remain at zero until the survey design and analysis-plan gates pass.

# 2026-10-28 Harden generic real-data scan entry

- The generic ExWAS CLI now requires Wave 1 source/readiness gates and a protected authorization record bound to the exact registry and design file hashes. Other waves remain blocked pending wave-specific gates. No CHARLS records were read and no associations were fitted.
- GitHub Validate for `b505e16` succeeded ([run 40623368833](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40623368833)); this validates repository checks only, not CHARLS analysis eligibility. The Pages assets did not change.

# 2026-10-27 Fix and revalidate the analysis-plan fingerprint gate

- GitHub Actions for `211f219` exposed a `NameError` because the new fingerprint helper referenced `ROOT`, which is not defined in that module. Bound document hashing to the module-derived repository root in `f56d44d`.
- GitHub Actions run [#710](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40372408996) then reported both `validate` and `synthetic-survey-engine` jobs succeeded. No participant data were read and no model was run.

# 2026-10-27 Review Wave 1 household exposure wording and routes

- Audited the official baseline household questionnaire and the locally archived 2011 codebook text for `i016`, `i017`, `i019`, `i020`, `i021`, and `i022` to prepare the K=150 household block and separately routed K=90 heating block.
- Recorded the `i020` to `i021` routing and provisional category labels. A read-only Word rendering of the official August 2011 baseline household questionnaire (printed pp. 182–183) confirms `i020` is a heating-facility indicator that excludes earth-heating systems and heating-capable air conditioners; the extracted-text copy corrupts this Chinese wording. The easily found CHARLS-hosted PDF is the 2013 follow-up and is excluded as 2011 evidence. Released-file coding, linkage, and denominator checks remain pending.
- No respondent-level data were read, no model was run, and no result/site payload changed. See `audit/wave1_household_exposure_questionnaire_review_2026-10-27.md`.

# 2026-10-27 Refine cross-wave heating metadata from the 2011 source document

- Updated the public housing metadata wording from “self-made heating” to the questionnaire's exact scope, “earth-heating systems (土暖气),” for 2011/2018 and retained their distinct heating-source routes. Added the read-only Word-rendered 2011 source page to the audit trail; the 2013 follow-up PDF remains excluded as baseline evidence.
- Rebuilt the audited catalogue and public static metadata with the documented `--finalize-only` pipeline. The site now links the 2011 heating record to the original DOC and preserves the item wording; public payload validation passed and all 92 analysis locks still match their triage register. Candidate-pair counts remain metadata co-availability only (2011: 146,780; 2013: 142,774; 2015: 143,854; 2018: 106,204; 2020: 21,630), not sample-size or model results.
- No respondent-level data were read, no model was run, and no association results were added; the formal association result count remains zero.

# 2026-10-27 Bump the housing metadata cache key

- Increased the cache-busting query version for `food_environment_v1.json` so browsers fetch the newly reviewed 2011 heating-source text instead of retaining the prior cached payload.

# 2026-10-27 Record autonomous execution checkpoint

- Re-ran the metadata-only Wave 1 intake preflight; all four required official inputs are still missing/ambiguous. The report remains in protected local storage. No participant values were read and no model was fit.
- Revalidated the official CHARLS source pages and recorded the current gate plus the locked post-pilot path: complete the 105-coefficient pilot only after source/design readiness; if valid and reproducible, proceed to the predeclared K=150 household-environment family and separately adjusted K=90 heating-route subdomain; expand to later waves only after wave-specific design and measurement review; publish only disclosure-reviewed aggregate families.
- Reaffirmed that statistical significance does not define pilot success, and no geography field may be invented as a variance stratum. No site payload or restricted data changed. See `audit/execution_checkpoint_2026-10-27.md`.

# 2026-10-27 Separate current K=105 runner from planned K=150/K=90 scale-up

- Code inspection found the current household-environment runner and readiness plan cover only the exploratory water/cooking-fuel K=105 family; they do not implement the documented K=150 household block or K=90 routed heating block. Corrected the runbook and scale-up criteria and added an explicit implementation-gap audit plus an empty future scale-up readiness template.
- The future scale-up remains gated on authenticated release-specific coding/routing, a dedicated protected runner, a distinct analysis-plan gate and a reproducibility-reviewed pilot. No participant data were read and no K=150/K=90 models were run.

# 2026-10-27 Bind pilot approval to exact analysis-plan content

- Strengthened both Wave 1 model readiness checks: approvals now include a SHA-256 fingerprint over the exact pilot, success criteria, scale-up, and multiplicity protocol documents. Editing a plan document invalidates the approval even if its human-readable plan ID is unchanged; the verified fingerprint is recorded in the private run manifest.
- Updated the two protected-readiness templates and the existing synthetic fixture shape. This is a fail-closed provenance improvement and does not authorize analysis or publication. No model was run; no participant data was read.

# 2026-10-27 Reconcile staged corrections with atlas-wide multiplicity

- Audited the private result validator, public exporter, and browser payload validator against the atlas-wide multiplicity protocol. They can recompute a single complete declared family, but staged runners emit block-local q values and the exporter cannot establish that all planned waves/blocks are present. Marked block-level adjustments exploratory/private until a complete frozen-family manifest and independent scope review are available; clarified the release contract. No participant-level data were accessed and no results were changed.
- Added a protected finalizer that requires an exact frozen primary-hypothesis ID manifest, validates all supplied batches, selects one primary model, fails closed on scope/status discrepancies, recalculates atlas-wide BY/Bonferroni, and writes only to private local storage. Added a non-executable manifest template; the full research scope still requires independent methods review. The utility has not been run on CHARLS results.
- Tightened the finalizer so it also requires a separate scope-review record bound to the exact manifest hash; added a template. This prevents accidental finalization of an unreviewed or subsequently edited family list, while leaving substantive reviewer judgment outside the software gate.
- Added a consolidated Chinese project handoff and work log covering the objective, completed work, exploratory-versus-formal result status, current official-data blockers, protected intake instructions, analysis gates, and next steps. It contains no CHARLS microdata, private result files, local account identity, or server credentials.

- Reviewed the Nature Medicine article’s reported full computable association family (123,774 tests; Bonferroni and Benjamini–Yekutieli) against the project’s staged K=105/K=150/K=90 batches. Recorded that batch q-values are provisional and cannot stand in for final atlas-wide correction.
- Defined a CHARLS-specific final family over all predeclared, estimable, primary wave-specific hypotheses; M0/M2 remain descriptive/sensitivity unless separately declared co-primary. Kept repeated CHARLS waves wave-specific and prohibited NHANES independent-cycle pooling formulas. The staged heating subdomain remains a distinct estimand but also belongs in the atlas-wide superfamily when making atlas-wide discovery claims.
- Clarified that the existing water/fuel sequence is exploratory because some extension choices followed initial pilot inspection. The NHANES full adjustment model also differs from CHARLS's age/sex-only M1; the primary CHARLS adjustment set requires estimand/DAG review before the next fit. This changes interpretation/release, not the current closed source/design/readiness gates. Details: `audit/multiplicity_primary_family_reconciliation_2026-10-27.md`.

# 2026-10-27 Distinguish published Wave 1 denominators

- Cross-checked the CHARLS 2011 National Baseline User Guide, Blood Data User Guide and Codebook: they report 17,708 interview/blood-target members, 17,705 observations for the Codebook person `ID` field, and 17,708 observations for individual-weight fields. These file/field-specific counts must not be collapsed into one expected prepared-table size.
- Updated the protected 2011 aggregate preflight to report denominator references separately and treat row-count differences as diagnostic only. A count match no longer claims frame reconciliation; that gate stays false until authorized person, Weight, PSU and Blood files are authenticated and joined by documented IDs/eligibility.
- Refreshed preflight in the pinned local analysis environment. Formal model gate remains `not_passed`; no association was fit. Full 571-test CI suite, JS syntax, public payload validation, Python compilation and diff checks passed. Public sources: CHARLS [2011 wave page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html), [National Baseline User Guide](https://charls.pku.edu.cn/en/data/User2011.pdf), [Blood Data User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf).

# 2026-10-27 Prepare a provenance-gated Wave 3 blood merge

- Added `scripts/merge_2015_official_blood.py`, a protected-local preparation step that requires both exact official SHA-1s (2015 All Data ZIP and separate Blood Data artifact), the metadata-only Blood intake gate, and manifest hashes tying the prepared Wave 3 table to that exact archive and output.
- The merge is an ID-keyed one-to-one left join, preserves the prepared respondent frame/order and `crosssection` field, leaves nonresponders' lab values missing, and records that `Blood_weight` is cross-sectional only. It does not select an analysis sample or fit models. Outputs and QA must stay outside cloud-sync/public repository paths.
- Added five synthetic regression tests. Full Python suite: 571 tests passed; Python compilation, CLI help, and `git diff --check` passed. Tests used synthetic fixtures only.
- Protected intake inventory still contains only the 2015 Blood directory README; official Blood artifact/Stata file and the official 2015 All Data ZIP are absent. The old prepared wave table is not authenticated against the current source/output manifest, so no merge or formal model was run and formal association count remains 0.

# 2026-10-27 Specify Wave 3 blood-weight target before future modeling

- Rechecked the official 2015 Blood Data Release Note and Wave 3 data page. The release distinguishes the full Wave 3 interview frame from its cross-sectional sample and blood responders, releases a cross-sectional `Blood_weight`, and says panel weights depend on the analysis purpose.
- Added a wave-specific plan requiring separate cross-sectional eligibility, official weight/source checks, and frame/linkage reconciliation before any 2015 blood association. Recorded official SHA-1 values for the All Data ZIP, Blood Data artifact, and release note; no files were downloaded and no model was run.

# 2026-10-27 Record derived-table output and build provenance

- The private wave-table builder now records each output's byte size/SHA-256 and the build timestamp, Python/pandas/pyreadstat versions, builder-script SHA-256, and Git revision/clean-tree status in `prepared_data_manifest.json`.
- The private validator compares the current derived table to its recorded output hash separately from source-input completeness. Missing/changed outputs remain explicitly unverified; source hashes still do not authenticate CHARLS identity.
- Added two synthetic output-hash checks. Full Python suite: 566 tests passed; Python compilation and `git diff --check` passed. No CHARLS table was rebuilt or read in this change.

# 2026-10-27 Surface prepared-table source-record completeness

- The private prepared-wave validator now reports whether each wave's manifest records the source archive name, byte size and local SHA-256. Wave 1 additionally requires separate PSU, Weight and Blood source records. It explicitly states that local hashes do not verify official release identity.
- Current protected manifest metadata records no source archives for any of the five prepared wave tables. Added four synthetic tests for absent, incomplete, invalid and locally hashed-but-not-official provenance.
- Full Python suite: 564 tests passed. The new check reads only the local manifest when assessing provenance; it does not read participant records. No source identity or analysis gate is promoted.

# 2026-10-27 Add filters to reviewed association results

- The optional reviewed-results table now supports filtering by exposure concept, phenotype concept, survey wave, and model. Rows are constructed with DOM text nodes to avoid interpreting public payload text as markup; the page still shows no results when the reviewed JSON is absent.
- Hardened release generation against a result CSV changing between validation and export; such a change now requires disclosure review to be repeated.
- Added an end-to-end synthetic release test (v3 result validation → exact-file-hash disclosure approval → allowlisted JSON → Pages validator) and a Node browser test for loading/filtering a complete approved family. CI runs the browser test.
- Validation: 560 Python tests passed; browser filter test, deferred loader test, JavaScript syntax check, public payload validator, and `git diff --check` passed. Tests use synthetic fixtures only. No CHARLS source data were loaded and formal association results remain 0.
- Local app asset is v194. Deployment status will be recorded after live verification.

# 2026-10-27 Verify reviewed-result filters are live

- Commit `9e81ef7` was pushed to `main`. Direct cache-busted requests returned HTTP 200 for the homepage and `app.js?v=194`; the deployed script contains the new result filters. `association_results_v1.json` returns HTTP 404, as expected because no real result family has passed official source/design and disclosure review.

# 2026-10-27 Verify published disclosure-gated result browser

- After commit `b5856c0`, the live GitHub Pages homepage returned HTTP 200 and loads app v193; the live app.js asset returned HTTP 200 and contains the reviewed-results loader.
- The optional `association_results_v1.json` endpoint returns HTTP 404, as expected because no association family has source/design approval and disclosure review. No estimates or CHARLS microdata were published.
- The full repository CI unit suite passed (559 tests); `node --check` and the public payload validator passed before push.

# 2026-10-27 Add disclosure-gated public association results path

- Added a private review-manifest gate bound to the exact result CSV SHA-256. Every analysis row needs an explicit disclosure decision; if any hypothesis is withheld, its entire predeclared multiplicity family is withheld.
- Added an allowlisted public JSON exporter, strict Pages payload validation for complete approved families, and a browser loader for the optional reviewed result asset. No result asset was generated because no family has an approved review.
- Added seven release-builder tests plus stricter public payload tests. Targeted release/result tests passed (29); JavaScript syntax and site-payload validation passed. CHARLS source/design intake remains closed and formal results remain 0.

# 2026-10-26 Reaudit public release boundary after pilot CLI fix

- Scanned tracked repository paths for protected pilot outputs, intake manifests, and common microdata file extensions; none were present. The public site payload validator passed.
- The live GitHub Pages site returned HTTP 200 and serves app v192; this documentation/script-only commit did not alter the deployed site. GitHub Checks API requests were rate-limited, so no remote result is claimed for the newest commit.

# 2026-10-26 Require explicit opt-in before protected pilot execution

- Both Wave 1 pilot runners now parse `--help` before loading analytical dependencies and require an explicit `--run` flag before touching local data. This prevents an informational/default CLI invocation from unexpectedly refitting a private exploratory analysis.
- A `--help` query exposed the old pilot runner's ignored arguments and triggered a repeat 15-analyte exploratory run; its outputs remained in the protected local directory and the run itself explicitly reported non-release-ready status. No result or participant data entered GitHub or the public site.
- Added CLI guard tests for both pilot runners. The full CI unit suite passed (549 tests), both runners passed safe `--help` checks in the analysis environment, syntax checks and `git diff --check` passed; no further analytical run was made.

# 2026-10-26 Connect official-source review with private intake hashes

- The Wave 1 metadata preflight now reads the protected intake manifest and reports source identity separately from local hash evidence. It only accepts a reviewed source identity when official document/page, title, filename, download record, reviewer record, and reviewed local SHA-256 all match the received files.
- A byte change rotates the opaque source-manifest ID and reopens identity review. Missing/ambiguous inputs remain `unavailable_pending_authorized_file`; the gate stays closed.
- Added six synthetic source-manifest tests. All 21 focused source-manifest/result-schema tests passed; `git diff --check` passed. The metadata-only preflight still finds all four Wave 1 inputs missing. No participant data or models were used.

# 2026-10-26 Separate source identity from private file checksums

- Replaced the v2 success requirement for a public official SHA-256 token with the versioned v3 result schema.
- Successful rows now require independently verified official release identity, a documented hash-evidence status, and an opaque protected-manifest ID; private file hashes and paths stay local.
- Updated the validator, analysis protocol, handoff, and audit notes. Fifteen focused synthetic validator tests pass; no CHARLS records or models were used.

# 2026-10-26 Verify published catalog KPIs against current payload

- Rechecked the live Pages homepage (HTTP 200): 1,319 exposure-candidate concepts, 332 phenotype-candidate concepts, five regular survey waves, and zero formal association models.
- Confirmed the local source page carries the same KPI values and its 1,625 unique concepts account for 26 concepts with both E and P roles.
- Confirmed the deployed `app.js?v=192` contains the accurate no-formal-reviewed-results note and the E/P, candidate-pair, and Life History JSON endpoints respond successfully.
- Clarified the distinction between unique concept count and role-specific homepage counts in README. No site data or association result was changed.

# 2026-10-26 Remove personal workstation paths from public audit notes

- Confirmed the local collaborator handoff manual is ignored by Git and is not in the public repository; its server path is therefore not published.
- Removed the author's Windows profile/workspace path from tracked historical notes and marked the old uploaded-data inventory as superseded by the current protected intake checks.
- No server address, login information, microdata, or analysis result was added to GitHub.

# 2026-10-26 Recheck wave-specific official intake availability

- Ran the existing metadata-only available-intake gate for Wave 2 weights and Wave 3 blood data. Both expected authorized inputs are absent from their protected intake locations; the private report records `skipped_missing_input` for each.
- Together with the Wave 1 preflight, all three current official-source intake gates remain open. This does not imply other waves' source files were searched outside their protected project locations.
- Updated the README to distinguish existing wave-derived candidate tables from source-authenticated official releases. No participant values were read and no analysis was fitted.

# 2026-10-26 Refine official sampling-design evidence

- Rechecked the CHARLS official sample-design page and recorded the described first-stage county sorting/PPS, within-county community PSU selection, and 30 split communities in the survey-design review.
- The page clarifies sampling operations but does not provide a released variance-stratum field, replicate weights, or a recommended variance estimator. No design variable was inferred from the sorting descriptors.
- Expanded the unsent support-inquiry draft to ask how county/community selection and the split communities enter variance estimation. The official contact page currently lists `charls@whu.edu.cn` but is dated 2019; the sender must reconfirm it before use. No email was sent.

# 2026-10-26 Recheck protected pilot gates and live site

- Re-ran the private pilot output-integrity audit. It passed the table-integrity and independent multiplicity-recalculation checks; source provenance and survey-design validity remain unassessed.
- Re-ran the metadata-only Wave 1 intake gate. The official all-data archive, PSU, Weight, and Blood files are still absent, so no formal refit or scale-up was run.
- Verified the live GitHub Pages homepage returns HTTP 200 and loads `app.js?v=192`; the published text says no formal, review-approved associations are published.
- Updated the README's current live app version and recorded the no-go gate and next execution order. No participant data, pilot estimates, pair counts, or private QA outputs were added to GitHub.

# 2026-10-26 Clarify public association-result status text

- Corrected the public app's maintenance comment from the inaccurate claim that no CHARLS associations had ever been fitted to the precise status that no formal, review-approved associations are published.
- Bumped the static app cache tag to v192. No catalog data, displayed results, or analysis status changed.

# 2026-10-26 Clarify Wave 1 weighting versus variance design

- Re-read the complete official 2011 National Baseline User Guide's sampling and weight-construction sections and documented the specific page-level design facts in `audit/survey_design_weight_review_v1.md`.
- Clarified that community indicators used as predictors in the blood-response weighting model do not constitute released variance strata; county-level PPS/sorting and 30 split communities also prevent inferring a design stratum from the county/community hierarchy alone.
- No design variance method was added or inferred; official source and variance gates remain open, and no pilot estimates were promoted.

# 2026-10-26 Add protected pilot-output integrity audit

- Added `scripts/audit_private_pilot_output_integrity.py` to check protected exploratory result-table structure, duplicate analysis keys, required finite estimates/uncertainty, warning counts, and family completeness without opening respondent microdata.
- The utility independently recomputes the declared Benjamini–Yekutieli and Bonferroni adjustments and writes only an aggregate QA report under the protected local CHARLS root.
- Ran the audit on the existing private 15-outcome pilot and 105-coefficient extension: technical integrity checks passed, with no engine warnings; formal source/design validity remains explicitly unassessed and not passed. M0 is descriptive and is not expected to have multiplicity-adjusted values.
- No estimates, p-values, pair support, microdata, or private QA files were added to the repository or site.

# 2026-10-26 Add protected aggregate design-frame preflight

- Added `scripts/audit_2011_pilot_design_frame.py` to check local prepared-frame denominator, age-domain availability, candidate bloodweight coverage, and PSU-key mapping while emitting aggregate diagnostics only under protected local storage.
- The private report records its UTC audit time and the official Blood User Guide source for its denominator reference.
- The current local derived frame does not reconcile to the official Blood User Guide target count; candidate age/weight and source/design authentication remain unresolved. The detailed counts remain in a private report and are not published.
- Created a dedicated local analysis environment under the protected data root using the pinned requirements. No participant-level data or environment artifacts entered GitHub; no association model was rerun and the public site payload is unchanged.
- Added an explicit pilot success/scale-up decision framework. Progression is based on source, frame, survey-design, reproducibility, and disclosure gates—not on whether early p-values are significant.
- Re-checked the current CHARLS user agreement and documented the restriction against publishing microdata or granting another person access; only disclosure-reviewed, non-identifying aggregate results may be considered for the public site.
- Updated the protected Wave 1 table builder to accept explicit 2011 all-data ZIP/RAR, PSU, Weight, and Blood paths, preserve source hashes, and retain legacy input support; no source archive was available for a merge run.
- Constrained Wave table builder input/output and temporary extraction to the protected local data root so licensed source data do not spill into a generic temp or synchronized folder.
- Added the pinned pandas dependency required by the Wave table builder to the protected survey-audit environment.
- Removed historical hard-coded prepared-row/PSU-map sizes from the 2011 pilot input checks; manifests now record observed frame dimensions while the official denominator remains a separate unresolved reconciliation gate.

# 2026-10-26 Clarify CHARLS Wave 1 age-domain and variance gates

- Re-read the official 2011 National Baseline User Guide and Blood Data User Guide. The blood target is all main respondents and spouses, with `bloodweight` built from individual weights and a blood-response correction estimated on both groups.
- Specify the intended age-45+ estimand as a survey domain within the full blood-target frame. The current pilot keeps the full table in the survey object and applies `age >= 45` through `where`; this is methodologically appropriate in principle, pending verification of official age/relationship/weight fields.
- The public guides do not specify a variance estimator, replicate weights or an explicit variance-stratum field. Final PSU mapping (especially the 30 split communities) and variance method remain unresolved; no geography-based substitute is allowed.
- Analysis notes updated in `audit/pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md`, `audit/pilot_followup_execution_plan_2026-10-26.md`, and `audit/wave1_pilot_official_intake_runbook_2026-10-26.md`.
- Updated both 2011 pilot scripts so future private run manifests record the domain-estimation method and keep exact source/variance checks open. Existing protected pilot outputs were not rerun or promoted.

# 2026-10-26 Add Wave 1 pilot source-intake preflight

- Added a local-only preflight for the official 2011 all-data archive, PSU, Weight, and Blood files. It records local file hashes, ZIP member names, and Stata header fields without extracting the archive or reading respondent values.
- Created the protected intake folder and source manifest template. Current gate is not passed because the four official inputs are absent; source provenance, age-domain eligibility, and survey-design review remain separate required gates.
- Added the operational sequence and limitations in `audit/wave1_pilot_official_intake_runbook_2026-10-26.md`; code is in `scripts/audit_2011_pilot_intake_metadata.py`.
- Repository commit `858d658`; no site payload changed. GitHub Actions status has not yet been independently confirmed for this commit.

# 2026-10-26 Add respondent-specific sensitive social-context metadata (published and verified)

- Official P022–P024 questionnaire routes and Codebook identities distinguish five respondent-specific fields from spouse/partner slots. Added three metadata candidate concepts for respondent party membership, minority status/ethnicity, and religious affiliation.
- Spouse/partner and child sensitive-identity fields remain deferred. The 2014 Life History wave has no survey weight; these fields are metadata candidates only, with no individual values or frequencies published.
- Local catalog rebuild: 195 concepts / 6,103 mappings (E 6,042, P 61); 1,251 mapped DEMOGRAPHICBACKGROUNDS fields and 199 deferred sensitive-relative fields. Published as app v191 / JSON v57; Pages Deploy #323 and Validate #645 succeeded, and live homepage/JSON checks confirmed all counts and five source fields.
- Audit: `audit/life_history_respondent_sensitive_context_review_2026-10-26.md`.

# 2026-10-26 Add offspring military-service and sent-down category context

- Reviewed official Life History C040/C041 child-slot menus and questionnaire routes. Added 26 military-service and 27 sent-down/not-applicable option fields as two family-level historical-context candidates; exact start/end year fields (72) remain excluded. C041's agricultural-hukou not-applicable category remains distinct from none.
- Local catalog now has 192 concepts / 6,098 mappings (E 6,037, P 61), including 1,246 mapped DEMOGRAPHICBACKGROUNDS fields. Deployed as app v190 / JSON v56; Deploy #322 and Validate #643 succeeded and both public endpoints returned HTTP 200.
- Audit: `audit/life_history_offspring_historical_experience_review_2026-10-26.md`.

# 2026-10-26 Add adopted-child source-context candidate

- Reviewed the official Life History C019a categories and adopted-child C017/C018 routing. Added one family-context candidate with four repeated adopted-child source fields; retained five official response categories without response frequencies. Exact adoption-year items and child identifiers remain excluded.
- Local catalog now has 190 concepts / 6,045 mappings (E 5,984, P 61), including 1,193 mapped DEMOGRAPHICBACKGROUNDS fields. Deployed as app v189 / JSON v55; Deploy #321 and Validate #640 succeeded, and homepage/JSON returned HTTP 200.
- Audit: `audit/life_history_adopted_child_source_review_2026-10-26.md`.

# 2026-10-26 Add offspring first-marriage family-context candidates

- Reviewed official Life History questionnaire pages 23–25 and Codebook field identities for C034–C038a1. Added five family-context concepts (126 fields): offspring ever-married status; spouse relative-age response at first marriage; spouse education and hukou at first marriage; and continuity with the first spouse.
- Excluded 54 exact relative timeline fields: marriage year, spouse birth year, and relationship-breakdown/divorce year. Eligibility, conditional routes, child referents, and routed missingness are documented; no individual values, frequencies, names, or linkage keys are published.
- Local Life History catalog is now 189 concepts / 6,041 mappings (E 5,980, P 61), with 1,189/1,920 DEMOGRAPHICBACKGROUNDS fields mapped. Deployed assets app v188 / JSON v54; Deploy #320 and Validate #638 succeeded, with public homepage/JSON HTTP 200 verified.
- Source and interpretation audit: `audit/life_history_offspring_marital_context_review_2026-10-26.md`.

# 2026-10-26 Add offspring schooling and work-status family-context candidates

- Mapped official 2014 Life History C012a/C012c/C013 and adopted-child C020a/C020c/C020b item families as three separate intergenerational family-context candidates (36 source fields). They are not respondent education/employment or clinical outcomes; repeated child slots are preserved, routed blanks are not interpreted as No, and no individual responses, counts, or identities are published.
- Rebuilt local catalog to 184 concepts / 5,915 mappings (E 5,854, P 61), including 1,063 mapped DEMOGRAPHICBACKGROUNDS fields. Static assets are deployed as app v187 / JSON v53; public homepage and JSON both returned HTTP 200 and the published payload contains the new candidates.
- Official 2014 questionnaire and Codebook routes/categories were reviewed; see `audit/life_history_demographic_backgrounds_full_coverage_2014_v1.csv` and the active-work checkpoint.

# 2026-10-26 Map adoptive/step-parent birth-year context

- Reviewed official A4a/A4b routes and A5c-A5f field identities. Added one relationship-specific background candidate for four calendar birth-year fields; these are not measures of age at respondent birth or caregiving duration.
- Updated complete FAMILYINFORMATION disposition: 469 mapped fields, 3 linkage keys and 1 release-version field excluded, zero substantive fields deferred.
- Rebuilt and deployed Life History catalog: 181 concepts / 5,879 mappings (E 5,818, P 61), app v186 / JSON v52. Deploy #318 succeeded and public homepage/JSON returned HTTP 200. CI exposed stale expectations for parent coverage (47/0), E/P totals, E134 dispositions, and four-year college field count; corrected and verified by Validate #634 on `d5f8efa`.
- Audit: `audit/life_history_parent_module_review_2026-10-26.md` and `audit/life_history_family_information_full_review_2026-10-26.md`.

# 2026-10-26 Refresh Life History homepage counts and CI expectations

- Updated the static Life History overview to the generated directory totals: 180 concepts / 5,875 source mappings (E 5,814, P 61), plus current Education History, Work History and Family Information coverage.
- Corrected stale existing unit-test expectations for the three-year college pathway and Education History's 1,077 mapped fields; the homepage KPI check now reads the generated JSON instead of a hard-coded obsolete count.
- Homepage app cache is v185; Life History JSON remains v51. Commit `81884ce` is live: public homepage returned HTTP 200 and contains the current 180 / 5,875 count. GitHub Actions validation state was not independently confirmed because the anonymous API is rate limited.

# 2026-10-26 Map biological-parent birth-year derivation inputs

- Mapped A5a/A5b biological mother/father birth-year fields as inputs to a potential parental-age-at-respondent-birth estimand; the catalog explicitly says these are calendar years, not ages.
- Kept A5c-A5f adoptive/step-parent birth years deferred, since they do not define age at respondent birth or caregiving start by themselves.
- Rebuilt catalog: 180 concepts / 5,875 mappings (E 5,814, P 61); app v184 / JSON v51. Formal association models remain 0.
- Audit: `audit/life_history_parent_module_review_2026-10-26.md`.

# 2026-10-26 Map sibling survival gate with conditional death year

- Matched the B4_4 alive/deceased gate to the questionnaire route for B11 sibling death year; mapped all 30 repeated fields to one family-level survival/death history P candidate.
- The 2014 Life History B module now has explicit mappings for all 271 structured Codebook fields; sibling outcomes remain distinct from respondent mortality, and special-wave fields stay outside weighted regular-wave scans.
- Rebuilt catalog: 179 concepts / 5,873 mappings (E 5,812, P 61); app v183 / JSON v50. Deploy #315 succeeded; homepage/JSON HTTP 200 and remote JSON SHA-256 matches local.
- Audit: `audit/life_history_sibling_module_review_2026-10-26.md`.

# 2026-10-26 Add childhood caregiver relationship context

- Re-reviewed official Life History A4a/A4b. The two structured fields ask who spent the most time raising the respondent before age 17 and are now mapped to one early-life caregiving/family-structure candidate.
- Preserved sex-specific categories, route skips, and the boundary that open-text other-caregiver descriptions are not included. Six parent birth-year fields remain deferred pending validated derived estimands.
- Rebuilt catalog: 179 concepts / 5,858 mappings (E 5,812, P 46); app v182 / JSON v49. Deployment verified: homepage and JSON HTTP 200, remote JSON SHA-256 matches local. Formal association models remain 0.
- Audit: `audit/life_history_parent_module_review_2026-10-26.md`.

# 2026-10-26 Add sibling education context candidate

- Re-reviewed official 2014 Life History B4_5 and mapped 15 sibling education slots to one family-of-origin socioeconomic-context candidate; retained explicit limits on timing, sibling-slot dependence, roster identity and the no-weight special module.
- Kept 15 sibling living-status fields deferred because they describe relatives at an undated interview-time state and do not establish a respondent-level exposure or phenotype.
- Rebuilt the Life History catalog: 178 concepts / 5,856 mappings (E 5,810, P 46); app v181 / JSON v48. Deployment verified: homepage and JSON HTTP 200, remote JSON SHA-256 matches local. Formal association models remain 0.
- Audit: `audit/life_history_sibling_module_review_2026-10-26.md`.

# 2026-10-26 Map Life History skill-certificate acquisition years

- Reviewed E133–E134 against the official Questionnaire and Codebook. Mapped the five E134 year slots to a separate unspecified skill-certificate acquisition-year E candidate; the Codebook has no certificate-name field, so no credential type or name is inferred.
- Education History now has explicit disposition for all 1,105 Codebook fields: 1,077 mapped and 28 source/linkage/release/quality exclusions; generic deferred fields are zero.
- Local Life History catalog is now 177 concepts / 5,841 mappings (E 5,795, P 46); app v180 / JSON v47. Deployment pending.
- Audit: `audit/life_history_skill_certificate_year_review_2026-10-26.md`.

# 2026-10-26 Close 2014 DemographicBackgrounds field dispositions

- Source-reviewed and assigned an explicit unique disposition to every 1,920 `DEMOGRAPHICBACKGROUNDS` Codebook field. The ledger now has zero generic deferred fields: 1,027 candidate mappings plus reviewed sensitive, C-only, exclusion, linkage and survey-process categories.
- Added fail-closed builder rules for offspring referents, child dates, sensitive identities, child marriage/education/history, roster links and adoption metadata. No questionnaire-only C032 field is invented; no participant values/frequencies or association results are included.
- Added `audit/life_history_demographic_backgrounds_children_disposition_review_2026-10-26.md`. This is source/audit metadata only; the catalog counts and website payload remain unchanged at 176 concepts / 5,836 mappings (E 5,790, P 46; local app v179 / JSON v46).

# 2026-10-26 Map 2014 Life History hukou section

- Mapped all 270 official HK001–HK006 fields into respondent initial hukou context (2) and repeated hukou change/reason history (268). Preserved route and event-slot differences, including Codebook capacities 11/10/6/10/10; did not assume suffix alignment.
- Location fields remain coarse metadata only; no participant geography, values, frequencies, derived change count/duration, or association results are published. The unweighted special-wave design remains separate from regular-wave weighted analysis.
- Local Life History catalog is now 176 concepts / 5,836 mappings (E 5,790, P 46); app v179 / JSON v46. Deployment pending.
- Audit: `audit/life_history_hukou_section_review_2026-10-26.md`.

# 2026-10-26 Map additional offspring count fields

- Mapped C007/C009/C017 (five Codebook fields) as an additional biological/adopted child screen/count candidate. Labels state that these are additional to a preloaded roster, not total lifetime parity; the builder does not derive totals.
- Added source audit `audit/life_history_offspring_count_review_2026-10-26.md`; no child names, participant values or frequencies are published.
- Local Life History catalog is now 174 concepts / 5,566 mappings (E 5,520, P 46); app v178 / JSON v45. Deployment pending.

# 2026-10-26 Map 2014 Life History offspring care context

- Reviewed C034a1–C034g2 and mapped 529 official fields across maternal employment/leave at childbirth, early-childhood service availability, offspring preschool access, and offspring residence/caregiving before age two and at ages three to five.
- Preserved child referents, repeated slots, multi-select caregiver options, age/death eligibility and conditional locality routes. These are family/offspring-context E candidates, not the respondent's own childhood exposures or child phenotypes; no participant values or frequencies are published.
- Local Life History catalog is now 173 concepts / 5,561 mappings (E 5,515, P 46); app v177 / JSON v44. Deployment pending.
- Audit: `audit/life_history_child_early_care_context_review_2026-10-26.md`.

# 2026-10-26 Map 2014 Life History pregnancy history

- Reviewed the female-only pregnancy-history section against the official questionnaire and Codebook; added 109 source fields across pregnancy outcome history (31), termination timing/duration (24), and induced-abortion reported reasons (54).
- Preserved pre-first-birth, between-birth, post-last-birth and additional-event routes. Excluded 12 child-order fields as roster/linkage keys. Marked pregnancy fields as sensitive retrospective metadata and excluded participant values, frequencies, dates, derived event counts, and association results.
- The full 1,920-field `DEMOGRAPHICBACKGROUNDS` ledger remains exhaustive; 2014 Life History stays outside regular-wave weighted pair analysis because its release note states no weight is provided.
- Local Life History catalog is now 168 concepts / 5,032 field mappings (E 4,986, P 46); app v176 / JSON v43. Not yet verified on GitHub Pages.

# 2026-10-26 Map 2014 Life History spouse/partner context

- Reviewed the official spouse/partner questionnaire section and mapped 114 Codebook fields into six E-candidate concepts for marital history, non-marital cohabitation, hukou transitions, coarse relationship-linked residential transitions, and spouse/partner education.
- The full DEMOGRAPHICBACKGROUNDS coverage ledger now accounts for all 1,920 official Codebook fields: 114 mapped, 1,420 demographic/child-family fields deferred, 270 hukou fields deferred, 90 sensitive relative-identity fields held pending privacy review, and the remaining 26 fields explicitly marked as linkage, date-of-birth, interview/proxy, partner-loop, redundant-gender, or release metadata.
- Preserved conditional routes and repeated slots. Documented questionnaire P012c follow-up with no corresponding Codebook field; did not invent a stored variable. Excluded relative birth dates, open-text death causes, names and direct identifiers; no responses or Codebook frequencies were used.
- Updated the local Life History catalog to 165 concepts / 4,923 source mappings (E 4,877, P 46). The module remains a separate unweighted 2014 special-wave catalog, not part of regular-wave pair co-availability. Site build output is local; this change has not been published to GitHub Pages.

# 2026-10-26 Inventory 2014 Life History DemographicBackgrounds

- Confirmed a major unmapped Life History module: official Codebook `DEMOGRAPHICBACKGROUNDS` contains 1,920 unique field identifiers and currently has no rows in the Life History E/P crosswalk.
- Added a metadata-only inventory generator and source-review checkpoint. It records 1,917 fields pending questionnaire-level review and excludes the three individual/household/community linkage keys. Codebook frequencies, extrema and respondent values are not copied or parsed.
- The next mapping batches will follow spouse/partner, child and hukou questionnaire sections, preserving respondent/relative referents, repeated episode slots, conditional routes and sensitive data boundaries. This supplementary 2014 module remains separate from the regular-wave weighted pair matrix.

# 2026-10-26 Environment-to-phenotype metadata readiness inventory

- Added `scripts/summarize_environment_phenotype_readiness.py` and its generated audit to distinguish the CHARLS environment/housing proxy domain from NHANES-style measured chemical exposures.
- Current sanitized catalog metadata identifies 94 distinct environmental/housing candidate concepts across waves, with 21–63 E candidates per wave. Their metadata-only co-occurrence with P concepts ranges from 2,184 to 13,482 candidate pairs by wave; these are not sample sizes, eligible analysis pairs, or association results.
- Source rows preserve household/community/respondent measurement levels. The inventory explicitly keeps the 2018 subjective air-quality perception separate from monitored concentration and states that CHARLS 2011/2015 blood analytes are internal biomarkers/outcomes, not environmental exposure measures.
- No participant-level data, Codebook frequencies, or unverified associations were used. The report is reproducible from the sanitized concept-source crosswalk and does not change the public site payload.

# 2026-10-26 Review Community Questionnaire Part E migration fields (local update)

- Reconciled all 46 JE-prefixed raw inventory fields against the official 2011 Part E questionnaire and Codebook. Mapped 44 source-anchored fields across eight provisional community-context concepts; kept JE014 informant position and Codebook-only JE016 as C-only metadata. Direct name/phone prompts are excluded.
- Preserved the 2010 migration-work period, village-only route, nominal province/occupation categories, five ordinal geographic-share bands, Yuan/month wage units, and the separate since-2000 household-registration-transfer count. JE007S33 remains explicitly unresolved because its Codebook entry says “No Observations”; JE016 remains unresolved because no corresponding questionnaire item exists. No frequencies or participant data were used.
- Fixed the community value-label builder to include JE fields and added source-review tests. The 159-step build completed in 6.7 minutes. Local E/P/C=6,236/2,116/1,004; 1,610 E/P concepts; 8,246 source mappings; 2011 metadata co-availability=143,752 (not analytic N). Generic pending labels=0; formal association models=0. All 507 local tests and payload/lock/JS checks pass. Pending GitHub push/CI and Pages publication.

# 2026-10-26 Review Community Questionnaire Part D enterprise, employment, and wage fields (local update)

- Reconciled all 18 raw JD-prefixed metadata-inventory fields: mapped 17 substantive fields to a community-context candidate concept and kept JD014 informant position as C-only metadata. Questionnaire name/phone prompts are excluded from the public catalog.
- Preserved the 2010 reference period, household/person/firm units, enterprise definition (at least eight employees), village-only routes, sex-specific daily/monthly wages, and separate manual-labor/nanny wage concepts. JD004 suffix-slot encoding is explicitly unresolved pending authorized-release QA; no categories or participant data were inferred.
- Updated value-label propagation to carry reviewed measurement semantics rather than leaving numeric community measures in a generic pending state. Full 159-step finalization completed in 7.7 minutes. Local shards E/P/C=6,192/2,116/1,002; E/P concepts=1,602; E/P source mappings=8,202; community crosswalk=170 concepts/534 mappings. Metadata pair co-availability for 2011 is 142,048, not analytic N. Formal models remain 0. All 504 local tests, public-payload validation, exact 92-lock check, JavaScript syntax check, and diff check pass. Pending GitHub push/CI and Pages publication.

# 2026-10-26 Review 2011 Community Questionnaire Part B infrastructure and activity facilities (local update)

- Reconciled all 127 raw JB-prefixed inventory fields against the official questionnaire, Codebook labels, and metadata-only inventory. Mapped 42 JB029 presence/initiator/funder fields across 14 community facility/organization types and added distinct years for sewer start, sanitation reconstruction, and village electricity availability.
- Classified four unstructured other-specify text fields and JB040 informant role as C-only; direct identifier prompts JB039/JB041 are excluded. No respondent text, respondent records, frequencies, or descriptive extrema were used.
- Full 159-step finalization completed in 7.6 minutes. Local E/P/C shards=6,175/2,116/1,001; 1,601 E/P concepts; 8,185 E/P concept-source mappings; 2011 metadata co-availability=141,835 (not analytic N). Full suite: 501 tests pass; public-payload, 92-lock, JS syntax, and diff checks pass. Current public app remains v129; local cache is v132 pending publication.

# 2026-10-26 Review Community Questionnaire Part A leadership profile (local update)

- Reviewed JA042 against the official questionnaire and Codebook field labels. Added 12 community-context candidate mappings across four role-specific education concepts and separate age/tenure profiles. Preserved community-only versus village-only CAPI scope and role-specific slots.
- The Codebook includes fifth age and tenure fields, but the questionnaire table names only four roles; those two fields are C-only metadata pending source identity resolution. Education categories were synchronized from the questionnaire across all four roles because some Codebook slot summaries omit an option. No respondent values or Codebook frequencies were used.
- Full 159-step finalization completed in 7.6 minutes. Local shards E/P/C=6,128/2,116/989; 1,582 E/P concepts; 8,138 E/P concept-source mappings; 2011 metadata co-availability=137,788 (not analytic N). Formal models remain 0. Local suite passes: 493 tests; public-payload and 92-lock validations pass; JavaScript syntax passes. Commit `cdecd92` is pushed and live at app v129; published JSON was directly checked for the 6,128-row E shard, the JA042 field, and all seven questionnaire education labels.

# 2026-10-26 Review Community Questionnaire Part C population and hukou fields (local update)

- Mapped 24 official JC fields to five provisional community-context exposure concepts; kept JC014/JC016 open-text ethnicity names and JC026 informant role as C-only metadata.
- Added source coverage audit and regression tests. Full 159-step metadata finalization completed; local E/P/C shards are 6,116/2,116/987, with 1,576 E/P concepts and 8,126 E/P concept-source mappings.
- 2011 candidate-pair co-availability is 136,510 metadata pairs, not analytic N. No respondent data or association estimates are included. Commit `4b257aa` is pushed to `main`; Live Pages deployment is verified at app v128; the E shard has 6,116 rows and the community JSON contains the added Part C concept.

# 2026-10-26 Expand 2011 community history catalog and close Part K coverage

- Reviewed all 75 Part H community-history source fields against the official Questionnaire, Codebook and metadata-only inventory. Added 58 mappings across eight new provisional community-history E concepts; added the conditional primary-school merger year to the existing concept. Excluded 15 elicitation/informant/open-text fields from cohort E/P concepts with explicit reasons.
- Preserved the older-informant retrospective route, village-only restrictions, units, year/period slots, conditional policy routes, and community-level interpretation. JH026_1 is a reviewed continuous year field, not a response category. No Codebook frequencies or participant values were used.
- Audited all seven Part K items: JK001–JK006 remain mapped as community-context candidates; JK007 is excluded from cohort E/P concepts because it describes the community-questionnaire informant and no participant-level identity link is established.
- Full 230-step metadata build and 159-step finalization completed. Local E/P/C shards: 6,092/2,116/984; 1,571 E/P concepts; 8,102 E/P concept-source mappings; 3,754 labelled rows; zero generic pending E/P/C labels. 2011 metadata co-availability is 135,445 (not analytic N). Formal models remain 0; 92 analysis locks unchanged.
- Final complete test run: 487 tests passed. Public payload validation, do-not-analyze triage validation, JavaScript syntax, and diff checks pass. Current public site does not yet contain this Part H addition.
- Corrected project status estimate: the interactive candidate catalogue/site is approximately 85–90% complete (2–4 focused days remain); the complete result-producing association atlas is approximately 50–55% complete (3–6 focused weeks after analysis-design/access inputs are ready). The earlier multi-month figure conflated these separate scopes. Remaining work will be batched by whole source module to reduce repeated full builds.

# 2026-10-26 Review old-age financial support source and repair metadata propagation

- Reviewed official 2013, 2015, and 2018 FN097 questionnaires and codebooks. Added the five questionnaire response labels to each wave and recorded the construct as an expected/hypothetical old-age resource, not realized pension receipt or income. Preserved the distinct 2018 wording, pension screening route, and conditional child-roster follow-up; Codebook frequency summaries remain excluded.
- Added `audit/old_age_financial_support_source_review_2026-10-26.md` and regression checks. Fixed the pension label builder so questionnaire-derived categories survive a clean upstream rebuild.
- Repaired final propagation order for community continuous household-count metadata and reviewed alcohol C context fields. The final E/P/C shards now have zero generic `not yet reviewed` label statuses; continuous counts still have no fabricated discrete categories.
- Full metadata rebuild completed in 8.1 minutes (230 steps). E/P/C rows: 6,034/2,116/984; E/P concepts: 1,563; concept-source mappings: 8,044; explicit E/P label rows: 3,774. Metadata co-availability is not analytic N; formal association models remain 0; 92 analysis locks unchanged.
- Local verification: 483 unittest tests pass; public payload validation, exact 92-lock validation, and JavaScript syntax validation pass. Commit `62c1fa7` was pushed; GitHub Pages Deploy #252 succeeded and published this metadata update. The Validate #509 run was still in progress at the last check.

# 2026-10-26 Review CHARLS Community Questionnaire Part K coverage

- Audited all seven 2011 Part K items against the official questionnaire, Codebook and metadata-only raw-field inventory. JK001–JK006 already map as separate community-context candidates; JK007 measures the community-questionnaire informant's Mandarin fluency and is explicitly excluded from cohort E/P concepts absent a verified person-level link.
- Added a coverage audit and regression test so the item is not silently omitted or misrepresented as an individual-level measure. No response values or Codebook frequencies were used.

# 2026-10-26 Add Part J agricultural machinery-supply origin (local update)

- Reviewed the full 2011 Community Questionnaire Part J inventory. Added JJ005 as a nominal community agricultural-service-supply context candidate, conditional on JJ003=Yes; retained county/province categories and withheld interpretation of conditional locality text as standardized geography.
- Documented Part J coverage and exclusion of respondent identity/name/phone fields JJ033-JJ035. No respondent values or Codebook frequency summaries used.
- Full 158-step rebuild completed; local E/P/C rows 6,034/2,116/984, 1,563 candidate E/P concepts, 8,044 concept-source mappings, 3,742 explicitly labeled E/P rows; 2011 metadata co-availability 133,741, not analytic N. Formal models remain 0.
- The label propagation test exposed and fixed a generic pending label for the questionnaire-coded JJ005 category. Full pytest suite passed (485 tests and 90 subtests); public-payload and 92-lock checks pass. This JJ005 update is ready for commit and deployment.

# 2026-10-26 Add community economic, housing-market, and credit-context candidates (deployed in #250)

- Reviewed 2011 Community Questionnaire Part J and official Codebook; added three provisional E concepts with 13 fields: village/community economic and fiscal measures (JJ011-JJ016), housing-market context (JJ026-JJ030), and formal-credit access (JJ031-JJ032).
- Preserved reference periods and units (10,000 Yuan, Yuan, Yuan/m2, Yuan/month and percentages), village-only CAPI routes, JJ014's explicit distinction from household income, and the English/Chinese lender wording discrepancy for JJ032. These are one-wave community-level contextual candidates, not respondents' own income, housing, loans or debt. No Codebook frequencies/extrema or respondent data were used.
- Full 158-step finalization completed in 6.3 minutes. Local E/P/C rows are 6,033/2,116/984; 1,562 E/P concepts; 8,043 concept-source mappings; 3,741 explicitly labelled E/P rows. The 2011 pair count is 133,528 metadata co-availability pairs, not analytic N. Formal models remain 0.
- Targeted review tests and the 480-test unittest suite pass; public-payload, exact 92-lock, JavaScript/deferred-loader and diff checks pass. This batch was published by Pages Deploy #250 after validation. The live public JSON includes all three concepts; app code and its v127 cache identifier did not change.

# 2026-10-26 Add 2011 community elder-care context candidates (local update)

- Reviewed the official 2011 Community Questionnaire and Codebook for JB030–JB038 and added two provisional community-level E concepts covering elder-care service centers and family-based/home elder-care context (12 source fields). Community-only and village-only CAPI routes, skip patterns, units, free-service zero, and multi-response slots remain explicit; these are community context candidates, not participant service use or approved covariates.
- Added a source audit and a fail-closed test validating every mapped field against the official inventory, source wording, categories, units, and route notes.
- Rebuilt all 158 metadata-finalization steps. Local E/P/C rows are 6,020/2,116/984; 1,559 E/P concepts; 8,030 E/P concept-source mappings; and 3,740 explicitly labeled rows. 2011 metadata co-availability is 132,889, not analytic N. Formal models remain 0.
- Pages Deploy [#249](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40217511361) published the updated catalogue. The CI check initially exposed a test dependency on the ignored local raw inventory; the test now checks the committed official Codebook instead. GitHub Validate [#505](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40217765152) passed on the follow-up commit. App and data cache identifiers remain v127/v5 because application logic did not change.

# 2026-10-26 Add source-reviewed mortality endpoint candidates (v127 prepared)

- Added 11 official-wave field mappings for 2013 Exit Interview and 2020 Exit Module: death-date components, calendar basis as C metadata, reported death expectedness, and the conditional final-illness-to-death interval. Added explicit proxy/decedent-only caveats and a catalog synchronizer so the reviewed status survives finalization. 2015 was not imputed from neighboring waves; 2018 cover-screen status was kept distinct from exit-module outcomes.
- Rebuilt all 157 metadata-finalization steps. Final site shards contain E/P/C=6,008/2,116/984 rows; 1,557 candidate concepts; 8,018 E/P concept-source mappings; 3,733 explicitly labelled E/P rows; and zero generic pending value-label statuses across E/P/C. Metadata co-availability pairs: 2013 141,920; 2020 21,630. These counts are not analytic sample sizes or association results.
- The 2013 and 2020 death-date components differ (year/month versus year/month/day) and the solar/lunar selector must be resolved before date pooling. Exit-module reports alone do not establish non-deaths, risk denominators, or follow-up/censoring. Formal association models remain 0.
- Full 157-step pipeline passed. Local verification: 480 Python tests and 90 subtests passed; public payload validation, exact 92-lock validation, and JavaScript syntax passed. GitHub Validate run [`40213942542`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40213942542) and Pages Deploy run [`40213942548`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40213942548) succeeded for commit `7b00491`; live v127 assets were verified. Site cache prepared as app v127 and candidate-pair data v5.

# 2026-10-25 Fix social-transfer caveat expansion and remove a build dependency (v126 prepared)

- Fixed mutable concept caveats accumulating once per source-field row in `build_social_exposure_crosswalk.py`. The longest affected field caveat fell from about 28 KB to 515 characters; six transfer concepts remain separate and exact source-field mappings are unchanged.
- Rebuilt all 157 metadata-finalization steps (6.3 minutes). E/P/C remain 6,008/2,107/982; E/P concepts remain 1,554; E/P concept-source links remain 8,009; explicitly labelled rows are 3,763; the 92 analysis locks and metadata-only pair counts remain unchanged.
- The regenerated social crosswalk shrank by 19.5 MB, the candidate-pair explorer by 19.4 MB, and the E shard by 39.1 MB versus the prior v125 checkout. No participant data or Codebook frequencies were used.
- Replaced pandas `to_markdown()` in the pair-coverage report with a small built-in Markdown renderer, removing the undeclared `tabulate` build dependency that interrupted the first full rebuild.
- Updated public-site cache keys to v126 / v4. All 476 Python tests, public-payload validation, exact 92-lock validation, JavaScript syntax, deferred-loader check, and whitespace checks pass locally. GitHub Validate #500 and Pages Deploy #247 both succeeded. The live homepage/app and cache-busted social/pair JSON assets were verified; the Pages artifact is 2.07 MB.

# 2026-10-25 Complete COVID module field coverage and add omitted candidates (v124 prepared)

- Audited all 100 fields in the official 2020 `COVID_Module` inventory against the E/P crosswalk. Added `audit/covid_module_field_coverage_2020_v1.csv` and a fail-closed builder/test: 77 unique fields map to reviewed E/P candidate metadata; the remaining 23 fields each have a reasoned non-E/P disposition.
- Added the official derived `XQuarantined` any-quarantine E candidate, separate VA001 exclusive no-awareness and VA006 none-response candidates, and three VB002 relationship-specific social-network outcome candidates. VB002 is conditional on the confirmed/suspected-case screen and does not establish respondent illness or cause of death. Irregular Codebook labels remain source-faithful and flagged for authorized-release validation.
- Full metadata finalization completed in 10.4 minutes. Local E/P/C catalog rows: 4,977/2,107/982; E/P concepts: 1,548 (1,245 exposure and 328 phenotype, including 25 dual-role); E/P concept-source mappings: 6,978. E/P records/wave-fields/explicit labels: 7,084/6,871/3,731; generic pending label status remains zero. The 2020 metadata co-availability count is 21,006, not an analytic sample size or result.
- Exact 92 analysis locks remain unchanged; models, analytic Ns, and participant-level findings remain 0. No participant data or Codebook frequencies were used. Site cache key v124 is live; Pages Deploy #245 succeeded. GitHub Validate #495 failed in the unit-test step, while local Python 3.12 reran all 471 unit tests successfully. A follow-up commit will trigger a fresh remote validation.

# 2026-10-25 Add COVID testing utilization outcome and complete module pass (v123 prepared)

- Added 2020 `VB012` as one P candidate for “ever tested for coronavirus by interview,” classified as healthcare utilization rather than infection or positive diagnosis. The exact Codebook labels are `1=Yes; 2=No`; conditional last-test year/month remain timing metadata.
- Final 2020 pandemic module crosswalks contain 48 E fields/22 concepts and 22 P fields/22 concepts. Candidate field rows are 70 total; source coverage and exclusions are recorded in `audit/pandemic_context_candidate_review_2020.md`.
- Full metadata finalization completed in 9.2 minutes. E/P/C catalogue rows: 4,973/2,104/982; E/P concepts: 1,542 (1,242 E, 325 P, 25 dual-role); concept-source mapping rows: 6,971. E/P catalogue records/wave-fields/explicit labels: 7,077/6,864/3,724; generic pending label status is 0 for E/P/C.
- 2020 metadata co-availability is 20,088 candidate pairs, not analytic sample size or fitted results. Exact 92 analysis locks remain unchanged; formal models and participant-level results remain 0. No participant values, frequencies or distributions were published.
- Website asset cache key is v123. GitHub Validate #493 and Pages Deploy #244 succeeded; live homepage serves v123 and the P catalogue contains `covid_testing_utilization_2020`. Scope/timeline correction is recorded in `audit/project_scope_and_completion_estimate_2026-10-25.md`.

# 2026-10-25 Complete 2020 pandemic-context candidate coverage (v122 prepared)

- Completeness review identified two additional E concepts within the CHARLS 2020 COVID module: subjective evaluation of government containment strictness (VA007) and conditional quarantine location (VB009). The E crosswalk now contains 48 fields across 22 concepts; the P crosswalk remains 21 fields across 21 concepts.
- Preserved the VA007 questionnaire/Codebook wording difference for response 2 (“Appropriate” vs “Satisfied”) in the field review status. VB009's four location flags use only their exact Codebook yes/no codes and remain conditional on quarantine; blank values are not interpreted as nonselection.
- Final catalogue E/P/C rows: 4,973/2,103/982. Candidate concepts: 1,541 (1,242 E, 324 P, with 25 dual-role); E/P concept-source mappings: 6,970; E/P catalogue records/wave-fields/explicitly labelled rows: 7,076/6,863/3,723. Generic pending label states are zero for E/P/C. The 2020 candidate metadata-pair index contains 19,883 pairs; these are not sample sizes or fitted associations.
- Full metadata finalization completed in 9.6 minutes; exact 92 analysis locks remained unchanged. No participant-level data, Codebook frequencies, or association models/results were generated. Audit: `audit/pandemic_context_candidate_review_2020.md`.
- Local app asset cache key is v122; the prior v121 public page and validation status are recorded below. Pages and CI runs for this follow-up commit will be recorded after push.

## 2026-10-25 Add CHARLS 2020 COVID prevention/context candidates (v121 prepared)

- Added 43 E-side source-field mappings across 20 prevention, information, contact, quarantine, self-isolation, and residential-restriction concepts, plus 21 P-side mappings across infection-report, behavior/function change, emotional-response, and recreation-cancellation concepts. All mappings are tied to exact 2020 questionnaire and Codebook fields.
- Transcribed only field-specific category labels: numeric checkbox codes from the exact Codebook section, ordinal codes from the Questionnaire with Codebook wording checked, and no invented labels for continuous measures. The parser now stops at the next variable heading; frequency counts, percentages, extrema, participant values, and analysis Ns are excluded.
- Full metadata finalization completed in 9.6 minutes. E/P/C site catalogues contain 4,968/2,103/982 rows. The E/P metadata index contains 1,539 candidate concepts (1,240 E, 324 P, including 25 dual-role concepts); the 2020 candidate-pair index reports 19,689 metadata co-availability pairs, not fitted associations or sample sizes. Explicit label coverage is 3,718 of 7,071 E/P catalogue records; generic pending label status is 0 for E/P and C.
- The exact 92 `DO NOT ANALYZE` locks were validated unchanged. No association models or participant-level results were generated. Audit: `audit/pandemic_context_candidate_review_2020.md`.
- GitHub Pages Deploy #242 succeeded and the public page now serves v121. The first Validate run #489 exposed two stale documentation snapshots after the catalogue row-count update; the E/P/C totals and README snapshot were corrected. All 468 unit tests pass locally, and GitHub Validate #490 succeeded after the correction.

## 2026-10-25 Add community medical-insurance policy context (v120 deployed)

- Added 20 official 2011 Community Questionnaire fields in two separate concepts: urban-resident medical insurance (JF010 option 1; JF011–JF013; six year-indexed household counts for 2005–2010) and New Rural Cooperative Medical Insurance (JF010 option 2; JF014–JF016; eight year-indexed household counts for 2003–2010). The multiple-select routes, community aggregate level, year suffixes, and annual premium units are retained. These are not sampled-person enrollment or individual premiums.
- Continuous household-count items have explicit no-category-label review status; no response records or Codebook frequencies were used. Concepts remain candidate metadata with analysis eligibility pending. Models and analytic Ns remain zero; the exact 92 analysis locks are unchanged.
- Hardened `site_catalog_shards.py` to append newly audited E/P source rows that are missing from the existing master catalog before building role-specific payloads. This v120 payload was reconciled from the last verified catalogue plus the 20 audited fields; the full upstream metadata pipeline remains a separate follow-up because its repeated finalization path is not idempotent. All 468 tests and release checks pass.
- All 468 tests, public-payload validation, exact 92-lock reconciliation, JavaScript syntax, and whitespace checks passed. GitHub Pages Deploy [#241 / `40194622511`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40194622511) succeeded. The public homepage returns HTTP 200 with `app.js?v=120`; live data reports 125 community concepts, both insurance concepts with 9/11 fields, 4,925 E rows, and 131,185 2011 metadata pairs. Audit: `audit/community_health_insurance_policy_context_review_2026-10-25.md`.
## 2026-10-25 Add the slot-indexed other community subsidy roster (v119 deployed)

- Added 25 official 2011 community fields for the other poverty-subsidy roster: five repeat response slots, five nested open-text program-name fields, and five indexed fields each for start year, recipient-household count, and monthly standard. The questionnaire/Codebook do not fully establish the flattened slot-to-name pairing, so the public metadata calls for authorized-release validation; free-text names are not treated as standardized subsidy categories.
- E/P/C catalogue rows are 4,905/2,082/982; E/P concepts are 1,496 (1,218 exposure and 303 phenotype, including 25 dual-role concepts); E/P source mappings are 6,881. Baseline community candidates are 123 concepts and 330 fields. The 2011 metadata co-availability count is 130,759; models, analytic Ns and association estimates remain 0, with the exact 92 analysis locks preserved.
- The complete metadata rebuild and all 466 tests passed. Public-payload validation, exact 92-lock reconciliation, JavaScript syntax and whitespace checks passed. GitHub Pages Deploy [#240 / `40179595161`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40179595161) succeeded. The public homepage returns HTTP 200 with `app.js?v=119`; live metadata reports 123 community concepts, the 25-field roster, and 130,759 2011 metadata pairs. Audit: `audit/community_other_subsidy_roster_review_2026-10-25.md`.

## 2026-10-25 Add four community pension-policy context concepts (v118 deployed)

- Added official 2011 community-level metadata for the over-65 subsidy (JG025–JG028), over-80 subsidy (JG029–JG032), New Rural Pension System (JG033–JG036), and Old Rural Pension System (JG037–JG040). Preserved V-only restrictions, recipient units, year/month units and the questionnaire's routes. The unusual JG033 No→JG036 route is called out as an applicability ambiguity; none of these fields establishes individual enrollment or receipt.
- E/P/C catalog rows are 4,880/2,082/982; E/P concepts are 1,495 (1,217 exposure and 303 phenotype, including 25 dual-role concepts); E/P source mappings are 6,856. Baseline community candidates are 122 concepts and 305 fields. The 2011 candidate metadata pair count is 130,546, a co-availability count only. Formal models, analytic Ns and association estimates remain 0; the exact 92 DO NOT ANALYZE locks remain unchanged.
- Rebuilt the complete metadata pipeline. All 466 tests passed; public-payload validation and the exact 92-lock check passed. GitHub Pages Deploy [#239 / `40178721943`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40178721943) succeeded. The public homepage loads `app.js?v=118`, and the live 2011 pair index and community catalogue report 130,546 metadata pairs, 122 concepts and all four pension-policy concepts. Audit: `audit/community_pension_policy_context_review_2026-10-25.md`.

## 2026-10-25 Add community social-protection policy context (v117 candidate)

- Added 11 source-mapped 2011 Community Questionnaire fields in three candidate concepts: unemployment subsidies (JG001–JG004), minimum living allowance (JG005–JG007), and single-child-parent rewards (JG013–JG016). Preserved field-specific recipient units, monetary units, and skip logic. These are community policy/coverage reports, not household receipt, personal income or fertility history.
- Excluded JG008 from candidate mapping because its minimum-living-allowance location conflicts with the question prompt's unemployment-subsidy wording. Recorded the source conflict and preserved the JG005 No-skip to JG008. JG015 is marked as a continuous household count, with no category labels or Codebook frequencies.
- Local catalogue: E/P/C rows=4,864/2,082/982; 1,491 E/P concepts (1,213 exposure, 303 phenotype, 25 dual-role); 6,840 E/P concept-source mappings; 2011 metadata co-availability pairs=129,694. These are metadata counts, not participants, analytic Ns or association results. Formal models and pairwise Ns remain 0.
- Full validation: 466 unit tests pass; public payload, exact 92-lock triage, JavaScript syntax, and diff checks pass. Local site cache key is v117; commit `89ba8cf` is live: the homepage returns HTTP 200 with `app.js?v=117`; the live pair explorer reports 129,694 2011 metadata pairs and includes all three new concepts. Audit: `audit/community_social_policy_context_review_2026-10-25.md`.

## 2026-10-25 Add community agricultural subsidy context (v116 candidate)

- Added the 2011 village-level JG017–JG020 agricultural subsidy program as a separate policy-context candidate: program presence, start year, 2010 recipient-household count, and average Yuan/mu standard. Preserved the V-only route and No-skip logic. The concept explicitly does not represent household receipt, a specific fertilizer/pesticide measure, or individual exposure.
- Regenerated public catalogue assets and metadata pair explorer: E/P/C rows=4,853/2,082/982; E/P concepts=1,488 (1,210 exposure, 303 phenotype, including 25 dual-role concepts); E/P concept-source mappings=6,829. The 2011 metadata co-availability count is 129,055. These are catalogue counts, not analytic sample sizes or results. Formal models and pairwise analytic Ns remain 0.
- Full validation: 463 unit tests pass; public payload, exact 92-lock triage, JavaScript syntax, and diff checks pass. Deployment will run on push because public site assets changed. Audit: `audit/community_farm_subsidy_policy_review_2026-10-25.md`.

## 2026-10-25 Add community reforestation policy context (v115 candidate)

- Added 2011 village-level JG021–JG024 as a community environmental-policy context candidate: program presence, start year, 2010 recipient-household count, and subsidy standard. The catalogue distinguishes this policy context from forest cover, ecological outcomes, household receipt, or individual pollutant dose.
- Fixed the community value-label parser's omitted `jg` prefix, allowing the official JG021 Yes/No categories to be extracted while discarding Codebook frequencies. Rebuilt the E/P crosswalk and site assets: E/P/C rows=4,849/2,082/982; 1,487 E/P concept IDs; 6,825 E/P concept-source rows. Actual models and pairwise analytic Ns remain 0.
- Full validation: 460 unit tests pass, public payload validation passes, `node --check` and `git diff --check` pass. Commit `dba4685` is live: the public homepage returns HTTP 200 and contains the v115 script reference and updated scope note. Audit: `audit/community_reforestation_subsidy_policy_review_2026-10-25.md`.

## 2026-10-25 Add a single entry point for available CHARLS intake gates

- Added `scripts/run_available_charls_intake_gates.py` to check the protected intake locations for the 2013 official weights and 2015 standalone Blood Data, then run only the existing checksum/header gates when each full input set exists. It never downloads, unpacks, reads respondent values, merges records, or writes QA into the repository.
- Added synthetic tests for absent inputs, an incomplete blood-file pair, and sync-folder rejection. Instructions: `audit/combined_intake_gate_runner_2026-10-25.md`.

## 2026-10-25 Recheck published-wave boundary (v114 live)

- Rechecked CHARLS's current public catalog and official releases. It still lists the 2020 national follow-up as the latest downloadable regular-wave dataset, while 2021–2023 recruitment materials describe a fifth regular survey without a corresponding data package in that catalog. Kept the survey implementations separate by actual release documentation rather than merging on wave title.
- Refreshed the official-source audit and the objective-measurement page's as-of date/cache key. Public homepage returns HTTP 200, loads `app.js?v=114`, and includes the new release-boundary wording. GitHub Validate #474 and Pages Deploy #235 still show in progress on their public run pages, so workflow completion is not recorded as confirmed. No candidate mappings or analysis eligibility changed.

## 2026-10-25 Add a metadata-only intake gate for CHARLS Wave 2 weights

- Added `scripts/audit_2013_weights_intake.py` to validate the official CHARLS 2015-11-18 `Weights.dta` SHA1 before parsing its Stata header. The gate confirms `ID`, `crosssection`, `longitudinal`, and weight-field presence with metadata-only access; it does not read values, IDs, flag counts, or merge records.
- Added synthetic pass/fail tests and a bilingual handoff audit. The official file remains absent locally; existing protected merge and survey-design gates remain in force. No public website asset changed.

## 2026-10-25 Prepare a checksum-locked 2015 blood intake gate

- Added `scripts/audit_2015_blood_intake.py` to verify the official 2019-06-20 Blood Data download SHA1 and inspect only the Stata header. It checks the 13,420-row release count and ID, `Blood_weight`, 16 analytes, fasting and triglyceride top-code fields. It never merges or reads respondent values; aggregate QA stays under protected local storage.
- Added synthetic regression tests, documented the user-account download route and created the private `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\incoming_2015_blood` folder. The official file remains absent; no restricted portal access or credentials were used.

## 2026-10-25 Show 2014 Life History sample and source details (v113 deployed)

> Status refresh, 2026-10-25: v112 is live and verified (commit `fe3787e`, Validate #467, Pages Deploy #233). The homepage loads `app.js?v=112` and includes the 2011 baseline PSU split-community caveat. v111 separately surfaced the 2014 Life History directory (18 concepts, 471 field mappings; 466 E, 5 P), excluded from regular-wave counts and weighted analyses. The official 2014 release-note, questionnaire, and codebook PDFs have locally verified SHA1 matches to CHARLS posted checksums. v113 is being prepared to show the official 2014 sample and no-weight boundaries directly on the card. The current gate remains source/version and survey-design readiness, not site hosting.
- Recomputed local SHA1 values for the official release note, questionnaire, and codebook; all match CHARLS posted hashes. This verifies documentation versions only, not the identity of local microdata. Commit `16d8674` passed Validate #468 and Pages Deploy #234; the live page loads `app.js?v=113`.
## 2026-10-25 Publish the baseline PSU mapping caveat (v112 deployed)

- Updated the public survey-design note to explain that CHARLS reports 30 large baseline communities split into geographic subareas. `communityID` is therefore only a PSU candidate pending release-specific mapping; geographic fields are not used to invent variance strata. Linked interpretation remains consistent with the official design documentation and project audit.
- Updated the site cache key to v112 and added a regression check for this caution. Commit `fe3787e` passed Validate #467 and Pages Deploy #233; the live page loads `app.js?v=112`.
## 2026-10-25 Record metadata-only PSU file inspection

- Confirmed the official 2011 data page lists PSU and Weight files separately. A local authorized `psu.dta` header contains `communityID`, province/city and urban/type fields, but no explicit variance stratum, subcommunity mapping, or replicate weights. Protected aggregate joins cover the prepared-table community keys; release identity is still unverified, so this is not variance-design validation.
- No respondent values or private QA outputs were added to GitHub. See the dated sections in `audit/survey_design_weight_review_v1.md`.
## 2026-10-25 Clarify official baseline PSU mapping limits

- Added CHARLS official baseline details that 30 large communities were split into geographic subareas and six sampled communities were replaced. This narrows the unresolved design gate: `communityID` stays a PSU candidate until the released PSU file's keys, labels, and subcommunity mapping are verified; geography is not used to invent variance strata.
- Updated the five-wave readiness matrix and active status. This is a documentation-only methods clarification; no data or model outputs were added.
## 2026-10-25 Surface the separate 2014 Life History directory on the landing page (v111 deployed)

- Added a home-page entry for the special 2014 retrospective Life History catalogue: 18 concept groups and 471 source-field mappings (466 E, 5 P). The card states that this survey is separate from the five regular waves, has no official weight, and is excluded from regular-wave co-availability counts and weighted association models.
- Clarified the five-wave headline counts to prevent visitors from assuming that the special survey is included. Updated the app cache key to v111. The CSV contains exactly 471 mappings across 18 concept groups (466 E, 5 P); independent recount confirmed the figures. Commit `2d1d2ee` passed Validate #463 and Pages Deploy #232; the live page loads `app.js?v=111`.

## 2026-10-25 Link and publish the five-wave measurement schedule (v110 deployed)

- Added a direct link to the NIA Biomarker Network page where the 2018/2020 blood-collection claim appears, so visitors can inspect the source of the discrepancy. Updated the browser bundle cache key to v110. Commit `9053334` passed Validate #461 and Pages Deploy #231; the live index loads `app.js?v=110` and includes the NIA link.

## 2026-10-25 Add a five-wave measurement schedule to the landing page (v109 deployed)

- Added a responsive five-wave overview so visitors can see at a glance that measures do not appear in every wave. It distinguishes 2011/2015 blood assay releases from 2013 physical measurements, the age-limited 2018 HCAP, and the absence of separate Biomarker/Blood Data files in the current Wave 5 official inventory.
- Added direct CHARLS source links and a note that the NIA Biomarker Network's 2018/2020 blood-collection statement conflicts with the current official release inventory. Linked the panel to the detailed blood-marker catalogue. Commit `87c5d24` passed Validate #460 and Pages Deploy #230; live index loads `app.js?v=109` and contains all five wave cards.

## 2026-10-25 Clarify unresolved later-wave blood-collection source discrepancy

- Reconciled the Wave 4 User Guide and official 2018/2020 file inventories with a conflicting NIA Biomarker Network summary that reports 2018/2020 blood collection. The public catalogue remains limited to CHARLS-published, field-addressable assay files (2011/2015); the discrepancy is explicitly documented as unresolved pending an official release file, variable dictionary, and weight guidance.

## 2026-10-25 Add wave/module readiness matrix and private module-level header audit

- Added an evidence-linked five-wave matrix distinguishing catalogue coverage, exact column-name presence in the private prepared tables, and actual model readiness. The matrix documents the 2011/2015-only blood assay schedule, activity subsample caveats, separate roster/community modules, the missing 2013 official sample flags, and the Wave 5 age-domain limit.
- Extended the header-only audit to write a wave × role × source-module field-name summary in protected local QA storage; it never reads respondent values. Two focused tests pass. No public site assets, participant data, pairwise Ns, or association results were added.

## 2026-10-25 Replace stale residential-history keyword labels (v108 deployed)

- Reclassified 18 already source-reviewed 2011–2015 age and residential-mobility C rows from generic keyword-discovery labels to field-specific metadata labels. The label update preserves separate year/month duration fields and the distinct BB007/BB009 questionnaire branches. The two 2011 BB003/BB005 field-identity holds remain unchanged and locked.
- Added a fail-closed allowlist updater to both full and finalize-only builds, Chinese UI translations, and regression coverage. The C shard remains 982 rows; generic keyword-only C status and subcategory counts are now both zero. All 449 tests, public-payload validation, exact 92-lock validation, JavaScript/Python syntax checks and `git diff --check` pass. Commit `2a082f2` passed Validate #456 and Pages Deploy #229; the live homepage loads `app.js?v=108`, and the live C catalogue matches the local file byte-for-byte.

## 2026-10-25 Correct exact current-wave DA005 option links (v107 deployed)

- Rechecked the 2013 and 2015 official questionnaires and Codebooks after the prior review had misread the `da005_2_` entries. Both Codebooks contain exact current-wave `da005_2_` fields as well as distinct `zda005_2_` prior-wave fields; the questionnaires identify DA005 option 2 as brain damage/mental retardation, and the source crosswalk contains one exact same-wave phenotype mapping. Added the two C/P metadata links while retaining prior-wave preload, conditional route, and analysis-eligibility caveats.
- Refreshed the full metadata finalization pipeline; E/P/C field rows remain 4,845/2,082/982, concepts 1,208/303 with 25 dual-role concepts, and 6,821 E/P concept-to-source links. Metadata-only pair counts remain explicitly labeled as not computed analytic Ns. All 446 unittest cases, public payload validation, exact 92-lock validation, JS/Python syntax checks, and `git diff --check` pass. No respondent values, codebook frequencies, or model results used. Commit `77b0da2` passed Validate #455 and Pages Deploy #228.

## 2026-10-25 Add private header-only prepared-field availability audit

- Added a reproducible comparison of the public wave/role/code catalogue with the five local prepared Stata tables using column metadata only. It writes aggregate role coverage, absent source-code/module keys and available weight/sample-flag column names to the protected local QA directory. It does not read respondent values or compute non-missing counts, pairwise Ns, or associations. The local scan confirms the known 2011 community join hold, separate relationship rosters, missing independent 2015 Blood Data fields, and missing official 2013 cross-sectional/longitudinal flags. No private QA files or microdata were added to Git.

## 2026-10-25 Verify clinical Questionnaire loop aliases for remaining C/P hits (v106 deployed)

- Added seven exact-source C/P metadata links for brain/intellectual-disability and recurrent-stroke age fields. Exact Codebook field identifiers are paired with fixed Questionnaire item/option anchors where the data release flattens loop slots (e.g. DA005 option 2); conditional routes remain explicit. Two 2013/2015 `da005_2_` C rows remain unlinked because the Codebooks show only prior-wave `zda005_2_` entries, not exact current-wave fields. The remaining generic keyword hits are therefore 2. The full finalization build reproduces all 47 links; all 444 tests, public-payload validation, exact 92-lock check, JavaScript/Python syntax checks and diff validation pass. GitHub Validate [#452 / `40168479043`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40168479043) and Pages Deploy [#227 / `40168479027`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40168479027) succeeded. Cache-busted homepage, app, E/P/C shards, pair index and social-exposure JSON match the local build. No respondent data, Codebook frequencies or model Ns used.

## 2026-10-25 Correct 2011 Codebook suffix extraction and link social-activity metadata (v105 deployed)

- Confirmed that the 2011 Codebook text extraction represents suffix fields such as `da070_2` as exact bullet identifiers `da070 2`; added exact normalized-heading matching and five additional C/E/P links after validating both official Questionnaire and Codebook sources. Separately source-mapped the 2011 `da057_8_` activity-frequency C/E field. The Questionnaire and Codebook differ on category-3 wording (“Not regularly” vs “Less often”), and two questionnaire extractions differ on the loop range (1–11 vs 1–10); both discrepancies remain explicit, and no denominator or response recode is inferred. Updated the prior audit statement that had incorrectly said the Codebook field was absent. E/P/C=4,845/2,082/982; All 444 tests, public-payload and exact 92-lock checks, JavaScript/Python syntax checks and diff validation pass. GitHub Validate [#450 / `40167636492`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40167636492) and Pages Deploy [#226 / `40167636393`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40167636393) succeeded. All public homepage, app, E/P/C catalogue, pair-index and social-exposure assets match the local build.

## 2026-10-25 Link exact source-verified E/P overlaps in C keyword hits (v104 deployed)

- Replaced generic keyword-discovery status for 35 exact same-wave C/E or C/P field overlaps only after confirming each field code in both the official Questionnaire and Codebook and finding one exact E/P concept mapping. Kept existing response-label, unit, route, and mapping review untouched; the C row now identifies a metadata overlap and explicitly does not confer covariate eligibility. Fifteen other keyword hits remain unlinked where dual-source identity or unique mapping was not confirmed. Added a reusable updater to both build paths, a frozen key set, audit CSV/Markdown, and regression checks. E/P/C=4,845/2,082/982; all 444 Python tests, public payload validation, exact 92-lock check, JS/Python syntax and diff checks pass. No participant data, Codebook frequencies, models or analytic Ns were used. GitHub Validate [#448 / `40165651978`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40165651978) and Pages Deploy [#225 / `40165652042`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40165652042) succeeded. Cache-busted homepage, app, E/P/C catalogs and pair index match the committed v104 build.

## 2026-10-25 Link recent hukou-change C/E metadata with routed categories (v103 deployed)

- Linked 11 exact 2013/2015/2018 C rows for recent hukou-status/location changes and their conditional reasons to existing exposure concepts. Exact fields are present in each wave’s public Questionnaire and Codebook.
- Preserved the 2013 no-change categories inside reason items, the 2015 `ZBC001` nonresponse route that skips `BC002_W3`, the 2018 reinterview-only route, and the five-versus-six category difference in 2015/2018 location reasons. Raw codes are not pooled across waves; no self-adjustment or default covariate recommendation is made.
- Added a source-checking updater to both metadata pipelines, exact-row audit, UI subcategory label, and regression tests. E/P/C=4,845/2,082/982. All 441 Python tests, public payload validation, exact 92-lock reconciliation, JS/Python syntax and diff checks pass. No participant records, Codebook frequencies, models, or sample Ns were used. GitHub Validate [#446 / `40164627044`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40164627044) and Pages Deploy [#224 / `40164627071`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40164627071) succeeded. Cache-busted homepage, app, E/P/C catalogues, and candidate-pair index match the local v103 build.

## 2026-10-25 Link source-reviewed hukou life-course C/E metadata (v102 candidate)

- Linked 16 exact 2011/2013 C rows (`BC002`, `BC007`–`BC010`, `BC012`, `BC015`, `BC017`) to existing wave-specific E candidates after checking each field in its official Questionnaire and Codebook.
- Kept historical status/location and conditional history-item routes, wave-specific answer labels, and pending release/denominator QA. These records are search metadata only; no pollutant dose or default adjustment recommendation is implied, and a focal E must not adjust for itself.
- Added an idempotent source-checking updater and tests to both metadata build paths. Rebuilt the public field-wave shards from the existing source-checked catalog; E/P roles and pair index are unchanged. All 439 Python tests, public payload validation, exact 92-lock reconciliation, JavaScript syntax, Python compilation, and diff checks pass. No participant data or Codebook frequencies used. GitHub Validate [#444 / `40164311499`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40164311499) and Pages Deploy [#223 / `40164311578`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40164311578) succeeded. Cache-busted public homepage references `app.js?v=102`; app, E/P/C shards, and candidate-pair index match the local build. The C catalogue contains all 16 exact wave-field links with source-route and no-self-adjustment cautions.

## 2026-10-25 Link social participation/care C/E metadata with source caveats

- Linked four exact wave-field C rows (2011 `DA056S8`, 2020 `xsoctype_7_`, and two 2013 money-management helper fields) to existing social-exposure candidates. The 2011 unselected-state storage remains unresolved; 2020 `XSocType[7]` remains a source-defined string field and is not recoded to 0/1.
- For the two 2013 helper fields, retained the questionnaire's helper category 15 versus the Codebook field suffix `s64`, which is only a field identifier, and the Codebook's exact-field “No Observations” note. They remain conditional lookup candidates; no frequency or response coding is inferred. The 2011 `DA057_8_` C/E hit remains unmapped because the exact field is absent from the 2011 Codebook.
- Added a reproducible updater to both metadata pipelines, source-path checks, audit rows, and regression tests. Current local E/P/C counts are 4,845/2,082/982. All 437 Python tests, public payload checks, the exact 92-lock reconciliation, JS syntax, Python compilation, and diff checks pass. No participant data, frequencies, or association models were used. GitHub Validate [#442 / `40163665219`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40163665219) and Pages Deploy [#222 / `40163665220`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40163665220) succeeded. Cache-busted public resources match the local v101 build, including the homepage cache key, app bundle, E/P/C catalogues, pair explorer, and social-exposure source metadata.

## 2026-10-25 Link historical hukou/location C/E metadata and correct the 2011 source path

- Linked seven exact-wave C records for last/first hukou location relations, reason for location difference, and prior-interview hukou type to the existing source-reviewed E crosswalk. Conditional interview routes and wave-specific categories remain explicit; this is not current hukou, measured pollution, or a default adjustment recommendation.
- Corrected the social-context crosswalk builder to cite the real official `CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`; the previous generic 2011 filename did not exist. The updater now checks exact Questionnaire/Codebook files before propagation.
- Added a reproducible updater to both metadata-build paths, a field-level audit, and regression tests. E/P/C remains 4,845/2,082/982.
- Validation: clean finalization, all 435 Python tests, public payload, exact 92 analysis locks, JavaScript syntax, Python compilation, and diff checks pass. No participant data or Codebook frequencies were read; formal models and pairwise Ns remain 0.

## 2026-10-25 Link residential-settlement C/E metadata to reviewed sources

- Linked two exact-wave C rows (2015 `BB001_W3_2`, 2020 `BA008`) to the reviewed residential-settlement exposure concept and official questionnaire/Codebook sources.
- Kept seven 2015 versus four 2020 response categories and address/time-frame caveats; numeric codes must not be pooled. This is residence context, not hukou type or a measured pollutant, and C is not an automatic adjustment recommendation.
- Added an idempotent updater to full and finalize-only pipelines, row-level audit, regression checks and a Chinese category label. E/P/C directory counts remain 4,845/2,082/982.
- Validation: finalization, all 433 Python tests, public payload, exact 92 analysis locks, JavaScript syntax, Python compilation, and diff checks pass. No respondent data or Codebook frequencies were read; association models and pairwise Ns remain 0.

## 2026-10-25 Link household-electricity C/E metadata to official source review

- Linked the exact 2011/2013/2018 `I016` C catalogue rows to the existing wave-specific `electricity_access` candidate and official questionnaire/Codebook metadata.
- Preserved its household/residence-level meaning; personal dose, respondent-household linkage, eligible denominator, release special values, and cross-wave comparability remain unresolved. It is not a default covariate and cannot adjust for itself. 2015 and 2020 fields were not included because they are outside this exact E/C overlap set.
- Added a deterministic updater to both build paths, row-level audit, focused regression coverage, and a Chinese C-subcategory label. Final directory remains E/P/C=4,845/2,082/982.
- Validation: clean finalization, all 431 Python tests, public payload validation, exact 92-lock reconciliation, JavaScript syntax, and Python compilation pass. No participant data or codebook frequencies were read; formal association models and pairwise Ns remain 0.

## 2026-10-25 Link formal-schooling C/E overlaps to reviewed source fields

- Linked nine exact-wave C rows for age at starting/stopping school, a wave-specific schooling-years update, and educated-youth follow-up items to their already reviewed formal-schooling E candidates and official questionnaire/Codebook sources.
- Preserved the C role for lookup, wave-specific routes, and response wording; explicitly states that an E/C overlap is not an adjustment recommendation and must not adjust for itself.
- Added the review to both full and finalize-only builds and a Chinese C-subcategory label. The 982-row C directory now has 99 generic automated-discovery status rows (55 codes) and 117 keyword-only subcategory rows (64 codes). Formal models and actual pairwise Ns remain 0.

## 2026-10-25 Link adult-education C metadata to mapped candidates

- Linked 33 exact-wave participation-option and credential C rows to the existing adult-education candidate crosswalk and official questionnaire/Codebook sources. Route, denominator, and release coding remain pending; these fields are not default covariates or separate option-level exposures.
- Made the existing Wave 4 duration overlap updater idempotent and expanded regression coverage.
- Made the finalization-only build reapply alcohol route statuses after each master-catalog rebuild, so reviewed questionnaire metadata is not erased by downstream catalog propagation.
- Reconciled chronic-disease timing and adult-education C metadata after a clean catalog/shard rebuild. The 982-row C directory now has 108 generic automated-discovery status rows (60 codes) and 126 keyword-only subcategory rows (69 codes); these are independent review fields, not adjustment-ready counts.
- Validation: 425 Python tests pass; public payload validation, exact 92-row analysis-lock reconciliation, JavaScript syntax, and whitespace checks pass. Formal association models and actual pairwise Ns remain 0.

## 2026-10-25 Clarify chronic-disease diagnosis-age metadata roles

- Linked 56 exact-wave C rows for reported diagnosis/knowledge age to the existing chronic-disease phenotype crosswalk and official Codebook source metadata.
- Clarified that recalled diagnosis/knowledge age differs from biological onset and must not adjust for the same outcome; added public-directory regression coverage and a Chinese filter label. No participant records or Codebook frequencies were used.

## 2026-10-25 Sync alcohol route reviews to the C metadata directory

- Propagated the existing official questionnaire/Codebook review for past-year drinking thresholds, beverage-type selectors, retrospective alcohol history, and 2018 prior-wave carry-forward to the exact-wave C catalogue rows. Structural skips remain distinct from No/zero, and the metadata is not a covariate recommendation.
- Added Chinese labels and a regression check for the public C directory. No participant-level values were inspected.

## 2026-10-25 Wave-specific residential and housing C metadata status review

- Updated source-review states for 2011–2018 `BB004` residential-history fields; retained the unresolved 2011 identity conflict as a hold, and marked later waves as wave-specific residential-history context.
- Updated 2018 current-residence context, property-roster positions, and household mortgage-payment metadata with explicit remaining route/aggregation/release-value caveats. None is a default adjustment recommendation.
- Added regression assertions and Chinese category labels. No participant records or values were inspected. Audit: `audit/c_covariate_search_status_clarity_review_2026-10-25.md`.

## 2026-10-25 补充2013官方权重文件的替代来源与接收边界

- 核实北大开放研究数据平台也列有2013 Wave 2 `Weights.tab`，页面提供19字段、19,679行和MD5元数据，但文件页注明需要登录/获准访问并展示CHARLS学术用途条款。将其与CHARLS发布页的SHA-1固定版`Weights.dta`区分；现有DTA合并入口不会接受或改名替代TAB文件，避免来源与字段定义未核实时误恢复样本资格。
- 更新接收手册与活动状态：当前受保护目录只有准备后的2013/2015个体表，没有原始2013/2015发行包或权重文件；未使用账户、未申请访问、未下载受限文件。后续若经授权取得替代文件，需先比对版本、字段、样本标记定义及来源，再讨论新的接收流程。
- 来源：[CHARLS 2013 Wave 2发布说明](https://charls.pku.edu.cn/en/data/Release2013.pdf)，[北大开放研究数据平台Weights.tab文件页](https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=95&fileId=198)。

## 2026-10-25 2011 FM055职业分类编码来源补充与禁分析状态明确

- 阅读CHARLS官方2011 National Baseline User Guide第5节后，补充其劳动模块使用GB六位职业分类（含扩展类别）及两位行业分类的背景；问卷显示FM055为FM054=Yes后的当前带薪消遣工作开放文本。Codebook虽列出`fm055_gb`、`fm055_isco`、`fm055_indc`，但指南没有给出FM055对应的具体查找表/版本，也未解释ISCO字段映射，因此不把劳动模块层面的编码说明误当成该题的逐字段映射证据。
- 三个字段分别补充来源和审查说明，继续保留`DO NOT ANALYZE`；新增来源驱动回归测试。元数据最终化完成，E/P通用待审标签为0、禁分析锁定为92；全套421项Python测试、公开站点负载检查、JSON/JS语法检查均通过。未使用或公开参与者级数据、频数或关联结果。
- 官方来源：[2011 National Baseline User Guide](https://charls.pku.edu.cn/en/data/User2011.pdf)。审计记录：`audit/pastime_job_classification_review_2026-10-25.md`。

## 2026-10-25 2011 DA010选中项存储审核状态同步

- 将受控本地汇总QA支持的2011年32个慢性病治疗多选字段状态同步到来源交叉表、字段目录及网站目录；明确选中代码得到核对，但空白/未选中存储和路由分母仍未知，不能把空槽解释为“No”。
- 保留字段原有审查提示，正式分析锁清单仍为92条；最终化元数据流程和DA010专题快速刷新均通过，Python全套417项测试通过。未公开参与者数据、频数或关联结果。详见`audit/2011_chronic_treatment_selected_storage_status_sync_2026-10-25.md`。

## 2026-10-25 2011慢性病治疗多选字段受控存储审计

- 新增仅在本地受保护数据目录运行的DA010选项存储QA，限定读取32个字段，私有输出只保留8个病种组的布尔审核结果，不保存参与者ID、逐人值或频数。
- Codebook选项值与字段索引相符；7组有“以上皆无”与其他治疗选项并存的少量记录，且8组都存在DA007医生诊断回答为“否”但DA010有作答的记录。由于2011问卷的路由同时涉及DA007病种索引和仅对部分病种询问的DA008自知状态，现有字段不足以重建完整适用分母。8个“以上皆无”映射继续标记`DO NOT ANALYZE`，等待来源链、空白/跳题编码和路由澄清；未将个人数据或频数公开。
- 修订既有审核记录并增加合成数据测试。完整414项Python测试通过。

## 2026-10-25 GitHub回归测试可移植性修复

- 2018养老金月份字段审计测试改为只依赖仓库内允许公开的官方问卷、Codebook和概念交叉表，不再读取仅保存在本地的原始字段目录；本地验证原始字段清单的审计结论仍留在受控审计记录中。完整412项测试通过。
- 首次GitHub CI失败是因为测试引用了被`.gitignore`排除的私有审计文件。修复提交`36e4ffc`后，GitHub Validate #415 与 synthetic-survey-engine 均成功；完整412项测试通过。

## 2026-10-25 养老金起始领取年月来源审核

- 对照2013/2018官方问卷与Codebook审核36个养老金起始日期字段，并将年份/月字段语义、波次/计划槽位限制和来源状态写入站点概念—字段目录。
- 对2013 `FN081` 月份字段标记来源标识冲突；对 `FN095` 年/月字段保留Codebook `No Observations` 锁定。补查发现2018 `FN003` 问卷显示年月，但Codebook和官方原始字段目录目前都只列四个年份槽位；未猜测新增月份字段。没有使用参与者数据或Codebook频数，也未运行关联模型。
- 审核脚本已加入完整及finalization-only构建，配对浏览数据在最后审核后重建。审计：`audit/pension_receipt_start_dates_2013_2018_source_review_2026-10-25.md`。

## 2026-10-25 住房所有者关系标签状态同步

- 将224项已逐字段完成的2018住房所有者关系官方答案标签核对状态同步到源映射和ExWAS概念—字段表。状态区分了已完成的Codebook标签转录与仍待核验的授权发布版本、路由、特殊码、家庭/个人链接和分析资格。
- 将失败即停、可重复运行的同步步骤加入完整及finalization-only构建，并增加专项测试；没有添加参与者级数据或关联结果。
- 将83项已存在逐字段官方类别标签记录、但总状态仍标记为待核对的慢病辅助表型字段同步到概念—字段目录；保留发行版编码、路由分母和分析资格待核验，以及现存禁分析标记。审计见 `audit/chronic_ancillary_label_status_sync_2026-10-25.md`。
- 养老金/社会保障目录中23项已有明确官方标签记录的字段完成状态同步，462项缺少逐项标签证据的记录继续保持待核；未解除任何路由或分析资格限制。详见 `audit/pension_label_status_sync_2026-10-25.md`。
- 修复养老金Codebook字段定位：官方2011 PDF将复合变量名下划线抽取为空格，曾造成40个准确字段被误判为未定位。现按标准化字段键核查，1,086项为已定位但无离散类别，0项标题匹配不足；17项保留更具体的来源审核状态。不推造答案类别。详见 `audit/pension_codebook_empty_label_status_reconciliation_2026-10-25.md`。

## 2026-10-25 E类候选范围说明

- 首页明确说明1,208个E概念是广义解释变量候选，覆盖环境/住房、行为、社会经济/保障及内部生物标志物，不能解释成环境化学物数目。详细范围说明见 `audit/e_candidate_scope_definition_review_2026-10-25.md`。

## 2026-10-25 C类检索状态说明

- 将C类筛选标签改为“自动关键词命中（协变量未选定）”，明确官方值标签审核与模型调整资格是两回事；更新网站脚本缓存版本至 v87。目录及模型状态不变。字段状态盘点见 `audit/c_covariate_search_status_clarity_review_2026-10-25.md`。

## 2026-10-25 页面可读性改进

- 针对测量与设计元数据（C）页面的长文本表格明确了各列宽度；字段码列在横向滚动时固定显示，避免长说明挤压代码和概念列。保留官方标签、角色判断与适用范围原文，不改动目录映射或分析状态。详情见 `audit/metadata_table_usability_review_2026-10-25.md`。

- Corrected the self-rated-health phenotype crosswalk using the 2011/2013/2015 questionnaire text: `DA001`/`DA080` are grouped by the Excellent-to-Poor scale, while `DA002`/`DA079` and 2018 `DA002`/2020 `DA001` use the Very-good-to-Very-poor scale. Preserved randomized question order, end-of-section repeat, proxy restriction and unresolved release-level routing gates; no participant data or response frequencies were used. Full metadata rebuild and source-aware regression coverage are included; audit: `audit/self_rated_health_scale_harmonization_review_2026-10-25.md`.
- Corrected the Wave 5 self-rated-memory review propagator to avoid writing wave-specific notes into the compact website catalog, which merges same-named fields across waves (for example, 2020 `dc004` is Checking Day, while earlier-wave `dc004` is self-rated memory). The full rebuild exposed this existing ambiguity; the corrected finalization flow keeps the authoritative field review in wave-resolved catalogs.
- 2011社区暴露链接增加`communityID`/`sub_commuID`聚合核查：官方指南将`communityID`列为通用链接键；当前本机文件出现重复键及`sub_commuID`记录，必须结合准确发行版解释，在此之前不假定唯一键、不随意去重或对子社区取均值。新增受控本地QA脚本和合成测试；脚本不输出ID或源值。官方依据与链接限制见 `audit/community_2011_subcommunity_linkage_review_2026-10-25.md`。
- Reconciled blood biomarker roles across the exposure catalogue, phenotype catalogue, source crosswalk, and pair explorer: 16 officially documented analytes in 2011/2015 now have optional internal-biomarker E and P candidate mappings. They are explicitly distinguished from exogenous environmental chemicals; wave-specific blood weights, eligibility, non-directional same-wave interpretation, self-pair exclusion and assay comparability gates are documented. Rebuilt metadata: E/P/C=4,845/2,082/982 rows, 1,486 E/P concepts and 6,821 source mappings; formal association models remain 0.

## 2026-10-25 续

- 按 CHARLS 2013/2015 官方问卷与 Codebook 新增子女记录背景候选：19个 E 类波次—字段、12个概念；另将2015年两项年龄路由的子女健康/自理项目作为2个 P 类子女层表型候选，避免与受访者表型混淆。保留路由、波次编码差异、收入分档、极端距离值和2015活动字段未标注代码24等限制。官方原始字段目录显示两个 Child 模块均含 `ID`、`childID`、`HHmemberID`；需在获批发行版核验键、连接和聚类分析单位。未构造受访者层暴露或运行模型。审计见 `audit/child_roster_context_source_review_2026-10-25.md`。

- 结构复核更正：官方原始字段目录的 2013/2015 `Child` 模块均含 `ID`、`childID` 与 `HHmemberID`；目录改按受访者关联的子女记录描述，并保留发行版内核唯一性和连接验证门槛。家庭信息 Codebook 中的编号题目槽位是另一种表示，不再据此推断 Child 模块不存在 childID/长表。网站与审计同步更正。

- 扩展子女户口与居住史候选目录：新增2013/2015共13个波次—字段、10个概念，覆盖当前户口所在地、出生地类别、户口变迁及统一登记前后信息。波次选项分别保留；不展示地址写入和Codebook频数。官方字段目录与问卷/Codebook槽位尚无一对一公开交叉表，因此网站明确标注记录字段对应、编码和获批数据连接验证待完成。详见 `audit/child_hukou_location_history_source_review_2026-10-25.md`。

- 复核子女教育字段：新增4个2013在校/就读年数 E 候选，并将2013年级编码重复、2015识字与最高学历标签冲突的2个字段列为 C-only 元数据，暂不提供分类标签或关联角色。年龄路由、父级题目跳转、子女记录链接和聚类限制均写入审计。详见 `audit/child_education_source_review_2026-10-25.md`。其中 `cb060_w2_1` 来自 `Family_Information` 宽表，只在最高学历为私塾/家塾时提问；子女槽位与记录级链接仍需在获批发行版核验，未假定可直接匹配 `childID`。

- 依据客观测量来源交叉表修正角色边界：108个波次—字段键均保留来源支持的P映射；其中36条原自动双角色行不再被当作E暴露候选，13个交叉表以外的内源测量发现项仍待逐项复核。完整目录收尾重建后E/P/C分片为4,790/2,093/980；候选配对数量仍是元数据共现，不是样本量或统计结果。新增审计与回归检查见 `audit/objective_measurements_exposure_role_boundary_2026-10-25.md`。
- 提交 `53f40e5` 已推送至 `main`；GitHub Pages Deploy run `40122389529` 成功，公开主页 HTTP 200，线上E/P/C分片条数与本地一致。完整Python测试373项通过，34个静态JSON可解析，92条DO NOT ANALYZE锁匹配。

- 全目录复核发现还有 107 条带审计交叉表来源的 E/P 行保留自动发现状态。新增可重复运行的末端传播步骤，同步字段级 CSV、JSON、主目录和网页分片；现在 6,895 条带概念来源的 E/P 目录行均显示来源映射候选状态，并明确保留“候选不等于批准纳入分析”的提示。正式关联模型、逐对真实样本量仍为0。
- 继续修正已审查概念交叉表与主 P 目录之间的状态传播：同波次同变量的躯体功能映射不再残留自动发现状态，并确保保留的审核提示明确说明它不是已批准测试变量。目录中的来源字段与候选变量均予保留。最终 E/P/C 为 4,826/2,129/980，E/P 字段—类别行 6,955，已标记值标签 3,648 行，通用待审 E/P/C 均为 0；正式关联模型和实际逐对样本量仍为 0。

- 修复已审核体测/人体测量字段在主表型目录仍显示“自动发现、待审”的状态传播问题。总目录生成器现在会把官方来源审阅状态同步到已有自动发现记录，并保留波次字段链接、模块资格和分析限制；增加回归测试。
- 最终化重建后E/P/C目录行数为4,824/2,127/980，候选配对索引保持元数据可用性口径不变；Python全套371项、34个JSON解析、JS语法和diff检查通过。正式关联模型和实际逐对N仍为0。

## 2026-10-25

- Reviewed the five-wave subjective current-memory item: 2011–2018 `dc004` and 2020 `dc006` share five ordered categories; 2020 additionally lists `997=Don't Know`. Updated the topic and phenotype metadata while retaining release-level missing-code, eligibility, and pooled-analysis gates. Removed 16 fully identical catalog rows with a reproducible exact-row deduplication step; no unique field mapping or result was removed.

- Reviewed past-year alcohol-frequency routing across all five waves. Preserved 2011–2018 beverage-specific frequency fields and the distinct 2020 overall-frequency measure; kept the Wave 1 liquor-frequency denominator unresolved pending authorized-release QA. Propagated reviewed labels and caveats to the field catalog and pair explorer, versioned the behavior asset cache, and added regression coverage. No respondent records or Codebook frequency summaries were used.

- 将2011 `flda081_1` 从自动关键词协变量搜索提示改为C类主观预期年龄题目上下文元数据；根据官方CodeBook显示75–115岁年龄档，不展示频数。问卷`DA081`目标年龄在提取文本中仍为占位符，故两字段直接链接继续标为未证实，`flda081_1`不进入E/P或模型。
- 修正角色覆核构建器，使已有C类记录可原位套用新元数据审查，不会被误当重复项删除；新增来源状态回归检查并刷新公开目录资源缓存键。
- 目录终结重建通过：E/P字段—类别行6,951、C字段—波次行980、E/P候选概念1,458、概念—来源映射6,751；通用未审核标签 E/P/C 均为0。正式模型数和实际逐对样本量仍为0。

# Change log

## 2026-10-25

- Resolved the 2020 `DA035` 30-hours/30-minutes translation discrepancy using the official Chinese questionnaire and Chinese flowchart; the Chinese questionnaire and Codebook both say minutes, and the flowchart shows `DA034<2 hours → DA035`, `DA034≥2 hours → DA036`. Restored reviewed response labels in the metadata crosswalk and documented that authorized-release value-storage/special-code QA is still required before analysis. Kept activity intensity and conditional routing separate; no dose or weekly total is derived. Added the official Chinese source PDFs, checksums, source review and regression coverage. No respondent records or Codebook frequencies were used.
- The full finalization run also refreshed 14 Wave 5 household-expenditure source references to cite the now-included Chinese questionnaire alongside the Codebook; no household responses were read.
- Audited alcohol-history `DA069` across 2011/2013/2015/2018 and morning-drink `DA078` in 2011/2013. Preserved the three historical DA069 categories and prior-wave carry-forward/skip routes (including 2018 `ZDA069`), distinguished history from current intake, and marked DA078's eligible population as conditional on the DA069 route. Updated the source mapping, topic JSON and pair-browser caveats; added an idempotent updater registered in both metadata pipelines and regression tests. No respondent data or Codebook frequencies were used; no new concept counts were added.

## 2026-10-25

- Completed the finalize-only catalogue rebuild after source reviews and restored the final validation order: all review/lock overlays run before the exact triage check and final website shards. Refreshed the crosswalks, catalog and metadata-only candidate-pair index (6,751 concept-source mappings); actual pairwise Ns and association models remain uncomputed. The 92 locks match the triage inventory, and all 370 tests pass.
- Reviewed the 2011 paid pastime-work occupation/industry coding against the household questionnaire, Codebook, and Wave 4 User Guide. Kept free-text job descriptions out of the public index, separated GB/ISCO/industry fields, and marked their coding edition/lookup unresolved and `DO NOT ANALYZE`; fixed the retirement crosswalk builder to refresh existing site payload records when audit metadata changes.
- Audited last-job location (`FL004`, 2011–2018) against wave-specific questionnaire and Codebook sources. Kept 2011 `DO NOT ANALYZE` because the Codebook lacks its category table and no-fixed-address code; surfaced the questionnaire Abroad option omitted by 2013/2018 Codebooks; preserved the concordant 2015 menu.
- Reviewed unpaid family-business location (`FH013`) in 2011–2018. Kept the four wave-specific location menus, documented the 2011 no-fixed-address interviewer code and later-wave carry-forward skips, and excluded address subfields from the public catalogue.
- Reviewed 10 five-wave employed-work intensity fields (days/week and hours/working day). Preserved the 2018 irregular-workday derivation note and 2020 paid-leave exclusion/low-frequency instruction; kept both as separate continuous measures without invented categories or a combined score.
- Reviewed written labor-contract status in all five waves, retaining the 2011 questionnaire/Codebook numeric-code distinction, 2018 payor-reference instruction and 2020 current-employer wording. Kept Yes/No follow-up skips separate from status and documented this as a work-condition candidate rather than direct environmental dose.
- Reviewed current employer organization type in all five waves (`FD002`, 2011–2018; `FC002`, 2020). Preserved the nominal response menus and 2020 “Do not know” code 997, and documented re-interview carry-forward/structural-skip limits so missingness is not misread as no employer.
- Improved metadata catalogue table readability: widened the desktop catalogue layout, gave the interpretation column room for caveats, and added a smaller horizontal-scroll layout for narrow screens.
- Reviewed the 2020 current-employer location item (`FC004`) and corrected its inherited unit, which incorrectly described months worked. The catalog now identifies a nominal location category, retains refusal code 999, and excludes conditional place-name fields from public metadata.
- Reviewed seven agricultural-work location fields across household farming (2011–2020) and paid farm work (2011/2013). Kept concepts and wave categories distinct, documented the 2011 no-fixed-address interviewer code and 2020 refusal code, and excluded place-name subfields from public metadata. No respondent records or Codebook frequencies were used.
- Reviewed non-farm self-employment business location (`FH006`, 2011–2018; `FD002`, 2020) against official questionnaires and Codebooks. Kept categories wave-specific, documented 2011 no-fixed-address and 2020 refusal codes, and excluded address/place-name subfields from public metadata. No participant records or Codebook frequencies were used.
- Reviewed current-workplace location context (`FD004`) against the official 2011/2013/2015/2018 questionnaire and Codebook wording. Kept wave-specific categories, made the 2013/2015 `FD002=6/7` structural skip explicit, documented the 2011 interviewer-entered no-fixed-address code for release QA, and separated 2020 similarly named fields. This is contextual geography only, not commute distance or an environmental dose; no respondent records or Codebook frequencies were used.
- Rechecked the official Wave 2 data portal: its listed `Weights` file checksum matches the guarded 2013 merge script. Confirmed from the official FAQ that researchers register, sign the agreement and apply for each dataset; documented that the local private intake location is still empty and the 2013 `crosssection`/`longitudinal` flags therefore remain absent from the prepared table. The merge path is ready but no 2013 model can run until the correct official file is obtained and validated.
- Reviewed building structure, storey descriptors, entrance-step routes, and construction-year fallback intervals against official questionnaires and Codebooks. Kept material categories nominal, kept building descriptors separate, retained the elevator-related entrance-step skip, and did not convert fallback intervals to exact years. Verified the 2011 `I005_1` Codebook field against the fallback choices printed under parent questionnaire item `I005`. Twenty-three mapping statuses were synchronized across the source crosswalk, final index, and browser JSON; generic pending/under-review rows fell from 23 to 0. See `audit/housing_structure_access_review_2026-10-25.md`.
- Reviewed household electricity availability and in-house bathing-facility categories against official wave-specific questionnaires and Codebooks. Kept household referents explicit, treated bathing categories as nominal, retained 2020's distinct wording, and did not invent a 2015 electricity mapping absent from the current source crosswalk. Updated nine mapped fields in the source crosswalk, final index, and browser JSON; pending/under-review housing rows fell from 32 to 23. No participant values or frequencies were used; all 356 tests pass and all 89 analysis locks match. See `audit/electricity_bathing_source_review_2026-10-25.md`.
- Closed three stale housing-catalog statuses: marked the 2015 `air_cleaner` row as an alias of the already reviewed `air_cleaner_home` field, and reviewed the official 2018 usable-area/floor-area wording, units, and ownership-dependent routes. Kept the two area measures separate and retained authorized-release QA and cross-wave limits. Synchronized the source crosswalk, final index, and browser JSON; added regression checks. No participant values or frequencies were used. Generic pending/under-review rows now total 32; all 353 tests pass and the 89 analysis locks match.
- Reviewed residence running-water access (2011–2018) and toilet flushability (2011–2020) against official questionnaires and Codebooks, including original 2013/2015 PDF pages omitted from the earlier text extraction. Preserved the 2015/2018 seated-toilet skip and kept 2020 tap-water access separate from earlier running-water questions. Propagated nine additional review statuses through the housing crosswalk, final source index, and browser JSON; stale housing “pending” entries fell from 44 to 35. No participant values or frequencies were used; all 350 tests pass and all 89 analysis locks match.

## 2026-10-24

- Fixed propagation of already reviewed housing measurement metadata into the public food/housing source crosswalk and browser JSON. The 2011–2020 room/toilet counts and reviewed dwelling area/construction or move-in timing fields no longer inherit generic “questionnaire review pending” labels; caveats still require authorized-release checks for special values, eligibility, linkage, and cross-wave comparability. Pending housing crosswalk rows fell from 74 to 52. Added regression coverage and regenerated the final metadata index and browser catalogue. No participant data or association models were used; all 347 tests pass and the 89 analysis locks match. See `audit/housing_review_status_sync_2026-10-24.md`.
- Propagated the existing official questionnaire measurement review for five-wave residential floor fields, 2020 above/underground floor routing and entrance steps into the public source crosswalk, final association index and browser JSON. Eight more stale pending labels are cleared (52 to 44); unresolved building-level fields remain pending. No participant values were accessed; all 348 tests pass and all 89 analysis locks still match.
- Reconciled README's current scope with the generated E/P/C shards, concept-source index, and wave-level candidate-pair metadata. Added a regression test so future catalogue updates cannot leave the handoff counts stale. Refreshed scope values are metadata counts only; candidate pairs are not sample sizes or model results. No site asset changed because the homepage KPI was already current.
- Rechecked protected five-wave community-key coverage against the local PSU-map candidate: all observed IDs map, consistent with the prior aggregate audit. Updated the validator to accept only private local map files and to label the result as key coverage, not source-release authentication or variance-design validation. The official source archive identity and sampling stratum remain unverified; no geographic field is substituted as a stratum. Synthetic tests cover key normalization and duplicate rejection. See audit/psu_key_coverage_recheck_2026-10-24.md.
- Refined the cross-wave explorer's migration caveat using the official Wave 4 tracking description, and added direct links to the Wave 2 release note and Wave 4/5 user guides. Corrected the Wave 5 PDF URL to the official CHARLS data-host path. All 341 tests passed after the caveat revision; focused explorer tests passed after source-link changes; the public index returned HTTP 200 with the updated wording and links.
- Added a separate longitudinal metadata explorer for 2011 community-context candidates versus 2013/2015/2018/2020 phenotype concepts. It uses only community-module source fields and cites official CHARLS ID-linkage guidance while clearly stating that no respondent records were joined and that mobility, eligibility, attrition, weights, and variance design remain unresolved. The view contains 113 baseline community concepts per follow-up wave; these are directory combinations, not analytic Ns or results.
- Expanded the 2011 community-context catalogue with nine source-reviewed concepts and 72 field mappings for land use, terrain, agricultural inputs, local food prices, household-energy prices, ranked crop production, household communication/appliance penetration, and retrospective disaster/epidemic severity. Preserved units, reference periods, skip routes, and community-level interpretation limits; excluded unresolved JA012 because the questionnaire and Codebook headings conflict. The full metadata rebuild now contains E/P/C=4,824/2,127/980 field-wave rows, 1,458 unique E/P concepts, and 6,751 source mappings; the 2011 community catalogue has 113 concepts and 270 source mappings. All 339 Python tests pass; Pages Deploy #149–#152 succeeded and the live community JSON contains all nine concepts. Metadata co-availability is not an analytic sample size; formal models remain 0.
- Reviewed five-wave housing elevator and accessibility-facility metadata. Preserved the 2011–2018 elevator floor-routing rule, the 2020 interviewer observation instruction, and the distinct 2018/2020 “Do not need” category. Updated the source-review pipeline, public housing JSON, audit log, and tests. No participant data or Codebook frequencies were used. Commit `6adc381` is live on GitHub Pages; 332 tests pass. Formal association models remain 0.
- Reviewed 2011 and 2013 `BA004` against each wave's official questionnaire and Codebook. Both are self-reported age fallbacks routed only when birth date in `BA002` is unknown or refused; the searchable C catalogue now says they are not complete age covariates and directs users to wave-specific age derivation. No labels, frequencies, or respondent values were copied. Added regression coverage; all 302 tests pass, all 89 analysis locks remain intact, and formal adjustment sets remain estimand-specific. Commit `e6267b4` passed Validate #290 and Pages Deploy #132; the live C catalogue shows the separate wave-specific sources.
- Improved the measurement/design metadata browser after review of the live page: clarified that covariate entries are searchable candidates rather than model selections, renamed the record-type filter, and widened the eight-column table with an explicit horizontal-scroll hint so long field notes remain readable. Bumped the app cache key; no metadata or analysis results changed.
- Reviewed 2013 `FN069_W2` (current participation in New Rural Social Pension Insurance) against the official questionnaire and Codebook: `1=Yes`, `2=No`; Yes routes to `FN071_W2` (first coverage month/year), and No routes to `FN070_W2` (non-participation reasons). Added an idempotent source-review step, audit note, and catalog/index/pair-browser propagation. The common candidate concept with 2011 does not imply cross-wave measurement equivalence; routing and eligible denominators stay wave-specific, and no frequencies or respondent records were used. All 301 Python tests pass; analysis locks remain unchanged.
- Source-reviewed household guest meals in 2011–2020 (`GE005`/`GF005`) against each wave's questionnaire and Codebook. The prior-week count is labeled as household-level guest person-meals; no frequencies or categories were copied. Added explicit warnings against treating it as individual dietary exposure, duplicating household values as independent observations, or assuming cross-wave equivalence without release-level QA. Added repeatable official-text checks, public catalog propagation tests, and a source-review note; all 298 Python tests pass and all 89 analysis locks remain intact. Pages deployment #129 succeeded, and the live five-wave metadata was verified.
- Added a source-reviewed 2013 candidate for predominant residential setting before age 16 (`BB006`, 1=Village, 2=City/Town). Kept it single-wave because 2011 questionnaire labels conflict with the 2011 Codebook; 2011 is excluded pending release-level resolution, and 2013 returnee preload routing is disclosed. Also moved the final E/P concept-source index rebuild after source-review updates so its statuses stay synchronized with reviewed domain crosswalks; all 89 locks remain intact. The directory now contains 1,445 distinct E/P concepts and 6,675 E/P concept-source mappings; pair Ns and formal models remain uncomputed/zero.

- Added two source-reviewed life-course exposure candidates: age at menarche and age at menopause, with eight exact wave-field mappings across 2011–2018. The catalog keeps age responses separate from calendar-year components, retains female-only and menopause routes, and excludes prior-wave `ZDA` history fields pending release-level identity review. The updated scope is 1,444 distinct E/P concepts (E=1,152; P=301, including 9 dual-role concepts) and 6,674 E/P concept-source mappings; pairwise-complete Ns and formal models remain 0/not computed. All 89 analysis locks remain in place; 289 unit tests pass.
- Added a questionnaire- and Codebook-reviewed marital relationship satisfaction phenotype candidate for 2015 and 2018. The catalogue preserves the BE001=1/2 routed population, keeps “No spouse now” outside the 1–5 ordinal scale, and does not claim validated cross-wave comparability or any association result; no respondent records or Codebook frequencies were used.
- Added three separately mapped subjective-wellbeing outcomes: life satisfaction in 2011/2013/2015/2018, health satisfaction in 2015/2018, and relationship-with-children satisfaction in 2015/2018. Preserved the living-offspring route and “No child now” response as separate metadata; health satisfaction remains distinct from self-rated health. No respondent records or Codebook frequencies were used.
- Rebuilt the public metadata catalogue and pair-availability index after the satisfaction review: 1,442 distinct E/P candidate concepts (E=1,150, P=301 including 9 dual-role concepts), with no formal association models or pairwise-complete sample sizes. All 89 analysis locks remain in place; all 283 tests pass.
- Expanded the existing subjective-life-expectancy phenotype concept to questionnaire-reviewed 2011/2013/2015/2018 `DA081` fields. Kept the target-age placeholder unresolved, the five-step response ordinal, 2018 code 997 distinct, and the 2020 `DA029` mapping separate from earlier-wave prostate-disease `DA029`; no cross-wave equivalence or model result is claimed.
- Finalized the update at 1,442 distinct E/P concepts (E=1,150, P=301, including 9 dual-role concepts) and 6,666 concept-source mappings. Actual pairwise-complete Ns and formal models remain uncomputed; all 89 analysis locks remain in place. All 286 tests pass; all 34 static JSON files parse.
- Source-reviewed 62 pending 2013 money-management helper relationship option fields against the official questionnaire and Codebook. Kept them as C source-detail rows for the two-helper loop, documented why blanks cannot be read as “no helper,” and synchronized the series-level catalogue so 64 option slots are not presented as separate association constructs. No frequencies or respondent records were used.
- Corrected alcohol-frequency harmonization across waves: 2011–2018 fields are beverage-specific and routed by selected beverage, while 2020 DA052 is overall frequency. Added official questionnaire line references, field-level notes, site payload updates, and regression coverage; matching 1–8 response labels no longer imply direct equivalence. No participant records or codebook frequencies were used.
- Updated the base behavior crosswalk generator so both its overall concept caveat and wave-specific field notes stay accurate when rebuilt before enrichment; the 2020 overall-frequency distinction is now checked on the concept card as well as field rows.
- Added an audited coverage check between automated E/P candidate field-wave roles and the approved concept-source crosswalk. It records the only current discovery-role exception: 49 internal biomarker rows that remain phenotype-linked but are not approved exogenous exposure links; no respondent data or counts were used.
- Clarified that CHARLS's 2021–2023 regular fifth-round fieldwork materials are not themselves a public data release. The current official data index lists the 2020 follow-up as the latest nationwide release reviewed for this project. Added a dated source audit and direct links from the objective-measurement catalogue; future waves remain excluded until their released datasets and documentation can be verified.

## 2026-10-24 (continued)

- Clarify the official Wave 2 distinction between cross-sectional, longitudinal, and cross-sectional biomarker weights, including the stated biomarker nonresponse adjustment and the absence of a longitudinal biomarker weight; link a source-specific review and keep 2013 design gates closed until authorized source files are verified.
- Require a pair/contrast-level estimability review reference before any result row can be released as `success`; document support, separation, design-information and model-complexity review without inventing unvalidated numeric cutoffs. This release gate is metadata only and does not claim that any CHARLS fit passed review.
- Record that finite output and no engine warning in a sparse synthetic logistic case do not establish adequate event support. Formal CHARLS fits remain blocked by unresolved source/design gates.
- Add a blank, privacy-aware controlled review-record template for consistent pair-level estimability checks.
- Tighten result-state consistency: a `reviewed_pass` requires its protected review reference, and an `inestimable` fit cannot claim that the contrast passed estimability review.
- Update the public methods panel with the official Wave 2 distinction between cross-sectional, longitudinal and biomarker weights; link the source audit and bump the page script cache key.

## 2026-10-24

- Added protected aggregate-only storage validation for 2013/2015 household property-sale allocation fields. Expected columns and numeric 0–100 amounts were confirmed, but option selectors and amount fields do not always co-occur. All 54 amount candidates remain `DO NOT ANALYZE` pending exact release identity, selector encoding, household denominator, and routing validation. Raw responses and QA outputs stay outside the repository; tests use synthetic data. See `audit/household_sale_proceeds_storage_review_2026-10-24.md`.
- Extended the synthetic-only `svy` design probe to binary-outcome and three-level categorical-exposure logistic models with explicit PSU-level dependence and reference coding. The coefficients, stratified PSU-score sandwich SEs and Student-t p values match independent numerical calculations (`n=216` and `n=270`; each design has 6 strata and 18 PSUs). Complete and near separation both emit `GLM_SEPARATION`; the near-separated exposure coefficient is finite while its uncertainty is non-finite, so that contrast must be `inestimable` with blank estimates. All 266 project tests pass, and the pinned isolated `svy` 0.35.0 probe runs successfully. Other sparse-category/convergence cases, finite-sample df for CHARLS and all real CHARLS fits remain unvalidated.
- Added a sparse-event synthetic fixture showing that `svy` can return finite logistic output for two events without a separation warning. Warning absence is therefore not a support or release gate; real-pair event/category support and design adequacy need prespecified review, with no threshold inferred from this fixture.
- Added a separate GitHub Actions job that installs the pinned synthetic-audit dependency set and runs the survey-engine probe on pushes and pull requests. The workflow was also verified in a newly created local Python 3.12 environment, keeping the public metadata tests independent of survey-package installation.
- Added a result-validator regression case for near separation: an `inestimable` result cannot retain a finite iteration coefficient or `NaN` uncertainty fields. The focused validator suite now has 12 tests; all 267 project tests pass locally.
- Added a CI privacy inventory that fails if licensed CHARLS respondent-data formats or local pairwise/QA count outputs enter the tracked Git index. The protected local pair-count file remains ignored and untracked. All 266 local tests pass; GitHub Validate run [#248](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40058708473) succeeded.
- Removed deprecated in-place `DataFrame.drop` calls from the guarded 2013 official-weight merge. The current pandas 3.1 test environment had flagged these calls; merge behavior, row-order checks and conflict safeguards are unchanged. All 263 tests pass, and GitHub Validate run [#236](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40056492623) succeeded.
- Added a reproducible synthetic-only probe of the installed `svy` 0.35.0 survey-analysis engine. Omitting known strata retained point estimates but changed SEs and design degrees of freedom. Independent calculations now match the engine's one-stage with-replacement PSU Taylor SE for a weighted mean and coefficient covariance in this Gaussian identity-link model; a Student-t reference check also reproduces its p-value from the engine-reported df. Other model families, design-df appropriateness and CHARLS analyses remain unvalidated; no CHARLS records or models were used.
- Extended the synthetic probe with a subpopulation represented in one PSU per stratum: `where=` keeps the full design, its Gaussian coefficient and full-design sandwich SE match a hand calculation, while pre-filtering creates singleton strata and is blocked by default. The audit records the implication for future pairwise-complete/domain estimands while leaving CHARLS missingness and eligibility rules prespecified and unresolved.
- Added synthetic structural-missing and pairwise-complete cases to the same probe. With out-of-domain measurement values null, the model runs on `where=`; with one in-domain pairwise missing row and `drop_nulls=True`, `n=47`, all 96 design rows remain, and coefficient/SE match the full-design weighted sandwich calculation. This checks engine behavior only, not the validity of a complete-case estimand or any CHARLS result.
- Updated the Chinese pre-analysis protocol to distinguish exposure–phenotype availability N from covariate-complete model N and to require preserving the full survey design when estimating defined domains. It explicitly says domain variance handling does not establish complete-case validity, module eligibility, or readiness to fit CHARLS models.
- Prepared an unsent bilingual inquiry for CHARLS about wave-specific variance-design fields, Wave 2 official sample flags/weights, and measurement-specific biomarker eligibility. The draft uses public release documentation only and is ready for the project lead to submit through an authorized channel; nothing was sent on the lead's behalf.
- Clarified the public age-domain note: CHARLS interviews an age-eligible main respondent and spouse, and Wave 4 individual weights apply to both; a `crosssection` flag alone does not certify that every record is age 45+. Added a regression test and official-source audit link. This changes only the interpretation note, not sample counts or model eligibility.
- Deployed the age-domain disclosure to GitHub Pages; Validate #240 and Pages Deploy #117 succeeded. A live HTTP check confirmed the note is present.
- Localized all 83 distinct C-catalogue subcategory descriptions in the public table, while preserving each original source-category phrase in the cell hover text and search index. Bumped the app script cache key and added regression checks for full translation coverage, source-text retention and cache-key synchronization; no catalogue records or CHARLS data changed.
- Verified the public Pages homepage references `app.js?v=63`; the live app bundle and C catalogue are HTTP 200, and all 83 live C subcategories have Chinese display labels. Deployment evidence: `audit/public_site_deployment_verification_2026-10-24.md`.
- Tightened the result-table success gate for CHARLS survey models: a successful row now requires a verified weight choice (used or explicitly verified unweighted), the verified PSU to be used, and either a verified variance stratum or a clearly labeled approximate variance method when the stratum is not released. `not_applicable` and other incomplete design statuses can no longer pass as successful CHARLS results. Added synthetic regression tests and documented the release rule; no CHARLS models or respondent data were used.
- Aligned the pre-analysis protocol with the stricter result gate so the survey-weight, PSU and unreleased-stratum requirements are explicit at the analysis-design level as well as in code.
- Strengthened the unreleased-stratum rule further: a successful row must state both that the variance method is approximate and what its limitation is. Added a synthetic regression test for a method label that omits the limitation; no real model results were used.
- Refreshed the result-validator handoff note to match the current design success gate and test coverage, removing its outdated four-test summary.
- Updated the active handoff status with the latest validator safeguards, test/lock checks and the continuing no-model state.
- Require structured `approximate method:` and `limitation:` labels (or Chinese equivalents) when a successful result lacks a released variance stratum, so vague prose cannot satisfy the release gate.
- Updated active project status to describe the structured variance-method labels now required by the validator.
- Added a regression test confirming the Chinese structured method/limitation labels pass; refreshed handoff test totals to 11 focused and 260 overall checks.
- Re-ran the core concept coverage diagnostic against the existing local prepared tables. Outputs and logs remain under the protected, non-synced `%LOCALAPPDATA%\CHARLS_ExWAS_Atlas\qa_outputs`; no counts, percentages, participant values, IDs, or file hashes were copied into GitHub. The 2013 pair-count gate still fails closed because both official `crosssection` and `longitudinal` flags are missing. Other wave outputs remain field-availability diagnostics only, before module eligibility, dedicated weights, QC, or model rules. Details: `audit/core_coverage_gate_refresh_review_2026-10-24.md`.
- Added the 2013 and 2015 `da051_random` release fields to the C-only metadata catalogue as physical-activity randomized-module assignment markers. Official questionnaires confirm that the activity module was administered to a random half of households, but the official Codebooks only label the released marker `Ca052Random`; no code-to-eligibility labels are published because the mapping remains unresolved. The live site warns users not to infer eligibility, denominators, or weight applicability from the marker or its missingness. No participant-level data or private aggregate counts were added. The full metadata finalization, all 256 local tests, JavaScript syntax check, and 89-row analysis-lock audit pass; GitHub Validate #221 and Pages Deploy #114 for commit `24104c7` both succeeded, and the live C shard was checked for both rows.
- Hardened the private Wave 2 weights intake: the merger now verifies the official CHARLS 2015-11-18 Weights.dta SHA1 before reading the file, refuses mismatched versions, and records the official SHA1 alongside the local SHA-256 in aggregate QA. Added synthetic checksum pass/fail coverage; no private file was available or read. Official release metadata: https://charls.pku.edu.cn/en/Data/a2013_CHARLS_Wave2.htm. All 255 local tests and GitHub Validate #217 passed; no Pages asset changed.

- Expanded the CHARLS 2013 yesterday-affect phenotype candidates from the two previously mapped items to all eleven official WB05–WB15 items. Kept each emotion as a separate one-item outcome with the shared 1–5 labels; did not reverse-code, sum, or claim a validated mood scale. Documented the same-day recall limitation versus WB03/WB04 sleep times, plus unresolved released-data routing and denominators. No participant data, frequencies or association results were used. Finalization now rebuilds symptom labels and restores the reviewed balance-test gate before catalog generation; all 254 local tests pass, 89 analysis locks match, and Pages Deploy #112 serves the 11 reviewed items.
- Clarified the 2013 WB03/WB04 clock-time source mapping: `_1/_2` are annotated as the AM-row hour/minute and `_3/_4` as PM-row components, while the published-release storage still requires confirmation before constructing a clock time. The fields remain single-day “yesterday” recall, and same-day associations with the WB05–WB15 affect block have no established temporal direction. Updated public E catalogue metadata; regression checks cover component notes, same-day interpretation and removal of dual-role self-pairs. No respondent records or association results were used.
- Tightened the result-table release gate: a row marked `success` now needs an official source-file SHA-256 token and the producing Git commit in its provenance fields, in addition to the existing survey-design and variance checks. Added pass/fail synthetic regression tests; this validates traceability only and does not fit or publish CHARLS models.
- Extended result validation across the full predeclared family: family IDs use `family_id;K=<integer>`, the CSV must retain all K rows including inestimable tests, and BY/Bonferroni values are recomputed and checked. Synthetic tests cover an inestimable family member, adjusted-value mismatch and missing family rows; no real model results were used.
- Added a family-level Bonferroni/BY P-value adjustment utility for the future ExWAS result pipeline. It preserves predeclared but inestimable hypotheses in K using blank `None` entries, rejects invalid P values, and does not fit models or read CHARLS data. Synthetic reference-family and boundary tests pass; the local suite now has 243 passing tests. No public association results or site assets were generated.
- Fixed value-label coverage reporting to read the final E/P/C site shards rather than the earlier intermediate field list. Moved the report generator to the end of both metadata pipelines, restored the detailed role/category/subcategory CSV schema, and synchronized the queue snapshot: E/P have 0 exact generic-pending rows; C has 171 of 990. This is a reporting-source correction only; no candidate roles, analysis locks, or association results changed. All 237 local tests passed; GitHub Validate run #205 (`40048483905`) succeeded. Browser assets were unchanged, so Pages deployment was not triggered.
- Added regression checks that compare every generated value-label coverage CSV row and the Markdown pending counts against the final E/P/C shards. The full local suite passes 239 tests; GitHub Validate run #207 (`40048680151`) succeeded.
- Refreshed the covariate-search documentation to the final C-shard count (171 field-wave search hits, 133 distinct codes) and reran private prepared-table structural QA. 2011/2015/2018/2020 pass; 2013 remains CHECK because its prepared file lacks the official `crosssection` and `longitudinal` flags, and the isolated incoming-Wave-2-weights folder is empty. The revalidation output and all person-level data remain under the local protected data root; no site assets or Pages deployment changed.

- Reviewed grip-strength and peak-flow protocols in the official 2011–2015 CHARLS questionnaires, baseline user guide and wave Codebooks. Added wave-aware candidate phenotype notes: grip readings remain separate by hand/trial with explicit kg; peak-flow unit remains blank; 30/890/993/999 are retained as protocol/status markers requiring release-specific valid-value review. The 2011 LI-to-QC/QB field identity remains unresolved, and 2013/2015 QC/QB instrument fields are documented without claiming released-data availability. Registered the review in both rebuild modes and added regression tests. No respondent-level data, Codebook frequencies, models or pairwise sample sizes are used; formal analysis locks remain at 89.
  Deployment verified: commit `f4f3345` is GitHub Pages Deploy #107 (run `40045896267`, success). Cache-busted public objective-measurement JSON returns HTTP 200 with 45 concept-wave rows; six grip/peak-flow rows are present, grip unit is kg, peak-flow unit remains blank, and public `app.js` uses cache key v4.
- Added official-source review of semi-tandem, full-tandem and side-by-side balance phenotypes. Recorded the age-graded 30/60-second full-tandem target, 10-second tests, completion/time/compensation as separate fields, 993/999 status handling, routing caveats and unresolved 2011 LI-to-QD/QE/QF field identity. Added a reproducible review step in both metadata build modes, an audit note and regression tests; no balance scores or association results are calculated.
- Deployment verified: commit `4bc7e25` is GitHub Pages Deploy #109 (run `40046572018`, success). The cache-busted public objective-measurement JSON returns HTTP 200 and includes the nine wave-specific balance-test notes, including the 10-second and age-graded full-tandem rules.
- Reviewed standing height, upper-arm length, knee height, body weight and waist circumference against 2011–2015 official sources. Added explicit cm/kg units, retained side and measurement-context fields, documented the 150 kg weight-eligibility route and 993/999 status codes, and left the 2011 LI-to-QI/QJ/QK/QL/QM release-field identity unresolved. No BMI or derived classification was created. Added a reproducible review step, audit note and regression tests.
  Deployment verified: commit `94727b8` is GitHub Pages Deploy #110 (run `40047066433`, success). Cache-busted objective-measurement JSON returns HTTP 200 with all 45 concept-wave rows; height/arm/knee/waist units are cm, weight is kg, and the 2011 candidate-field caveat is visible.
- Reviewed the five-times chair-stand instrument in 2011/2013/2015 official questionnaires and the baseline guide. Kept completion, route-specific duration fields, stand count, and trunk/arm use separate; retained the “fastest pace” preamble versus “usual pace” item wording conflict, the 993/999 statuses, chair setup metadata and unresolved 2011 LI-to-QH release identity. No summary score is inferred. Added a source audit, rebuild step and regression tests.
  Full objective-measurement finalization now covers 15 concepts × 3 waves (45 concept-wave metadata rows). The complete finalization pipeline, 237 Python tests, JavaScript/Python syntax checks, all 89 formal analysis locks and diff checks pass; no respondent-level models or pairwise Ns were created.
  Deployment verified: commit `101c3b1` is GitHub Pages Deploy #111 (run `40047594897`, success). Cache-busted public objective JSON returns HTTP 200 with 45 rows across 15 concepts; the five-times chair-stand wording conflict and route-specific duration caveats are visible.

- Made the full metadata rebuild reproducible for the pension and digital-behavior reviews. Pension Codebook fields with no discrete response menu now retain an explicit source-located/no-category status; the bracket-endpoint review runs after supplementary pension fields are added. The separately reviewed 23-row 2011–2018 internet/digital crosswalk is restored after the social builder, and DA056 review now distinguishes its 41 social-participation fields from 8 linked digital fields. Shared DA056 concepts are classified as related checklist options, not independent exposures.

- Split alcohol-frequency and last-drink quantity concepts, removed the beer-unit selector from the E candidate mapping, and retained it as C measurement metadata. Added 2020 DA029 as a single-wave subjective life-expectancy phenotype with the official five-level response labels and XFAgePossibility interpretation note; it is not treated as survival or harmonized with earlier-wave prostate-illness DA029.

- Rebuilt all public metadata shards: E=4,739, P=2,104 and C=990 wave-field rows; 1,429 unique E/P concepts (1,150 E, 288 P, including nine dual-role concepts) and 6,643 concept-source rows. Wave-level E/P metadata co-availability is 121,318 / 126,727 / 130,608 / 101,757 / 13,906 for 2011/2013/2015/2018/2020; these are not sample sizes. All 89 formal analysis locks remain intact, no association models were fitted, and no respondent records or frequencies were used. The full build, all 220 Python tests, Python compilation, JavaScript syntax and JSON parsing passed.

- Reconciled a 30-row gap in the CI E/P concept-link check: blood-pressure readings and knee-height measurements now join the reviewed objective-measurement map by exact wave and variable code, including objective phenotype categories outside `physical function`. The final E/P source catalog has no rows without a candidate concept link; candidate status remains distinct from analysis eligibility.

- Reviewed CHARLS 2011/2013/2015 timed-walk fields `qg002`/`qg003` against official questionnaires and Codebooks. The 2.5 m usual-pace test has two separate elapsed-time trials in seconds; ages 60+ and route/safety eligibility are retained; 993/999 remain non-completion status codes, not seconds. The 2011 manual's LI item identifiers are not asserted as identical to the Codebook's QG release fields. See `audit/walking_speed_source_review_2011_2015_2026-10-24.md`.

- Fixed review-pipeline ordering so finalization begins from a regenerated wave-level master catalog before source-specific updates. Made DA056 and parent-visit reviews tolerate the compact prior-build catalog state without assigning cross-wave answer categories; kept wave-specific labels in each source record. Fixed household-member amount review to apply the correct wave-specific label-status/source inside the write loop.

- Updated the E/P/C website shards to include the browser search properties while preserving exact wave-level rows and source-reviewed label/status values. Added exact-wave objective concept linkage checks, public shard/catalog checks, and a cache-busting assertion that accepts the current versioned asset. Full finalization completed; 216 unit tests passed, all 34 JSON files parsed, JavaScript syntax passed, deferred asset-loader test passed, and the CI E/P concept-link check found zero unmapped rows. No association models were fitted and no participant-level data or frequencies were used.

- Corrected the derived candidate-series review summary to rebuild from the final wave-field catalog after specialist mappings and source reviews. Previously, custom official statuses such as the reviewed 2020 internet-use route appeared as generic “not yet reviewed” because the summary recognized only a few hard-coded status phrases. The new refresh step preserves a single exact status, reports wave-specific state differences, and keeps “not yet reviewed” visible whenever any source wave is pending. A regression test covers `da040`; 217 tests and all static checks pass.

- Made homepage KPI generation idempotent. Repeated finalization had left duplicate concept-count notes below the four cards; the generator now removes its prior generated note before writing one current copy. Running it twice produces identical HTML, and the homepage regression test asserts exactly one note.

- Clarified the homepage scope cards by separating exposure and phenotype candidate concepts (1,149 and 288), survey-wave coverage, and the zero formal-model count. The note explains that nine concepts have both roles, there are 1,428 unique E/P concepts, and source-field mappings are not participant counts or association results. Counts are generated from the audited concept index; added a consistency test. Deployed as GitHub Pages #102 and verified the public homepage.

- Moved the final E/P/C shard build to the end of both metadata pipelines so late source-reviewed metadata propagation is reflected in the browser catalogue; final role shards match the master field catalogue at E=4,750, P=2,110 and C=986 rows.

- Synchronized the E/P concept-source index with the explicit catalog role audit: seven 2018 HA004 total-value/unit-value format selectors are C-only metadata, not exposure tests. The crosswalk builder now applies exact audited E/P-to-C overrides only when the corresponding C catalogue field and reviewed concept are present; added regression coverage and a reconciliation audit.
  Specialist concept joins now preserve that C-only boundary in the field catalogue as well. Full finalization reports 1,428 E/P concepts (1,149 E, 288 P, including 9 dual-role concepts), 6,624 source mappings, and wave metadata co-availability counts of 121,107 / 126,514 / 130,376 / 101,551 / 13,906 (2011/2013/2015/2018/2020). These counts are not sample sizes or association results. All 210 tests and static checks pass; the 89 analysis locks and zero fitted models remain unchanged.

- Added questionnaire-derived units and field-specific scope notes for the 2011 community weather estimates: annual low/high temperatures (°C) and rainy/snowy day counts (days), explicitly reported by a community informant rather than linked station observations. Added source audit and regression coverage; no responses or Codebook summaries were copied.
  Full finalization synchronized the weather annotations across the candidate catalogue and community site JSON; 209 tests and 34 static JSON checks pass. The refreshed site catalogue contains E=4,750, P=2,110, C=986; 89 formal E/P locks remain and no association models or pairwise sample sizes are computed.
  Deployment verified: commit `0a79030` is GitHub Pages Deploy #100 (run `40028365448`, success); the cache-busted public community JSON returns HTTP 200 and confirms the four weather-field units and caveats.

- Expanded the objective-measurement wave boundary review using official CHARLS sources: the 2018 Wave 4 User’s Guide places non-blood measurements in Waves 1–3 and blood biomarkers in Waves 1 and 3; the 2021–2023 fifth regular survey is kept distinct from the released 2020 Wave 5 package. 2020 care-use recall questions are not coded as direct measurements. Updated the site note and audit; no 2021–2023 rows were inferred without a verified release package.

- Reviewed 2011 community industrial-pollution fields against the official questionnaire and Codebook: JB018 (own community ordinal report), JB019 (nearby settlements, village-only route), and JB027 (village-to-site distance in km, with questionnaire-defined zero for an in-village source) remain separate contextual proxies, not personal exposure doses. Added field-specific caveats, searchable metadata, reproducible finalization steps and regression tests; no respondent values or Codebook summary statistics were used. Full 208-test suite and static checks pass. Updated the community page summary from its stale 100/187 snapshot to the current 104/198 catalogue and added the pollution-field interpretation to the page lead.
  Deployment verified: commit `2bcf2c7` is GitHub Pages Deploy #98 (run `40026396623`, success); the public community JSON returns HTTP 200 with the 104-concept catalogue and the reviewed JB018/JB019/JB027 field caveats.

- Rebuilt the objective-measurement phenotype crosswalk with wave-specific official sources. A reproducible check found every one of the 36 listed candidate field-code tokens in each 2011/2013/2015 Codebook; the site explicitly limits this to token presence, not semantic, routing, unit, or release-file validation. The 2011 manual LI identifiers remain distinct from release QA/QB/QC field names unless independently reconciled. Added regression tests and registered the builder in both metadata pipeline modes. Full finalization pipeline and 203 tests pass; respondent records and Codebook frequencies were not used.
- Preserved the original Codebook display labels for each of the 108 objective-measurement field-wave entries and added those labels to the searchable phenotype table. The 2013 QL002 extraction truncation is marked in the interface. Updated the objective-metadata cache key; all 204 Python tests and static-site checks pass.
- Verified commit `e8377e6` on GitHub Pages Deploy #96 (run `40024182348`) succeeded; the live page renders the label column, and the cache-busted public JSON returns all 45 concept-wave mappings.
- Clarified the objective-measurement page's wave boundary: it includes only waves with the current official questionnaire/Codebook mapping; 2018/2020 are not auto-filled from differently named or absent candidate codes. The note explicitly says code-name differences do not prove a measure is absent and that full wave-specific measurement sources remain to be checked.
- Commit `80a88c8` deployed via GitHub Pages Deploy #97 (run `40024908402`) successfully; live homepage verified to display the updated objective-measurement wave-scope note.
- Reviewed BB005 residential-history year fields in the 2011, 2013, 2015 and 2018 official questionnaires and Codebooks. Added four wave-specific C metadata records, including previously absent 2011 and 2018 rows; documented conditional routing, the 2018 new-interview restriction, address-reference differences, and release-specific special-value validation. No respondent values or Codebook summary statistics were copied; E/P concept counts and association results remain unchanged.
- Reviewed adjacent BB003 county/city/district move-in years across 2011–2018 and added the missing 2011 and 2018 C metadata rows. Preserved its distinction from BB005 village/community years, the 2015 BB001_W3/XRType route, the 2018 new-interview restriction, and wave-specific address references. No participant values or Codebook summary statistics were copied.
- Reviewed 2011/2013 alternate residential-mobility branches BB007–BB010. Added missing 2011 cumulative year/month fields; documented that BB007/BB008 and BB009/BB010 are alternate BB001 routes, not repeated measures, and retained the 2011 Codebook/questionnaire wording caveat. No Codebook frequencies or participant values were copied.
- Clarified the BB004 source-validation hold wording, keeping it separate from the formal E/P analysis-lock inventory. The 89-row E/P lock remains intact.
- Reviewed CHARLS-hosted Harmonized CHARLS Version D documentation as a secondary cross-wave reference. Added a seven-concept field mapping for age, gender, community urbanicity, hukou, self-rated health, BMI, and ADL; clarified its missing-value/construction conventions and survey-design context without copying frequency tables or treating harmonized variables as raw CHARLS measures.
- Clarified the C metadata page for non-specialist users: covariate candidates are search aids, measurement and routing rows are explanatory metadata, and neither implies a selected adjustment set or completed analysis. Updated labels and cache-busted the page assets.
- Reviewed 13 remaining 2011 work-module fields against the official questionnaire. Added questionnaire-only option wording where categories are listed, retained numeric release-code uncertainty, and added units, ranges, routes and interviewer instructions for continuous/count fields including 0/999997 handling notes. No questionnaire option order was treated as verified released-data coding.
- Expanded the 2011 community education profile to include six exact percentage fields and six separate fallback brackets used only when the informant does not know the exact percentage. Verified category bins, current water/electricity price units, road-scale anchors, disaster routing and the village-only sanitation-reconstruction route; codebook frequencies remain excluded.
- Updated the current work and progress notes, regenerated the public catalog, and added regression coverage; all 167 Python tests pass.
- Reconciled 2011–2018 internet activity/device fields with official questionnaires and Codebooks, separating the legacy DA056 social-activity checklist from the dedicated 2020 DA040 internet screen. Reclassified 23 existing wave-field mappings in place, preserved unresolved older checkbox storage, and prevented duplicate E rows.
- Normalized work Codebook identifiers that the 2011 PDF extraction renders with spaces instead of underscores. Numeric/date fields now surface verified field presence without invented answer categories, and occupational/industry classification codes are explicitly marked as lookup codes rather than numeric scales. Codebook frequencies remain excluded.

## 2026-10-23

- Reclassified the 2011 DA062S1/DA062S2 fixed Age/Year Codebook markers as C metadata; the questionnaire records actual cessation time in DA062_1/DA062_2. Added regression coverage and preserved the Codebook labels without frequencies.

- Reviewed smoking cessation age/year selectors against each wave’s official questionnaire and Codebook. Reclassified the 2013, 2015, 2018, and 2020 selectors as C metadata; recorded the direct 2018 DA062_1/DA062_2 age/year label conflict and locked both components from analysis. Added regression checks and updated the DO NOT ANALYZE inventory to 35.

- Clarified six DA017 cancer-site fields with no observed Codebook categories: the official questionnaires confirm each numbered site option, while response labels remain blank and underlying unselected/storage codes remain unknown. The main catalog now carries that source-aware review status; added regression coverage and rebuilt the public metadata assets.
- Pinned the Pages artifact packager to its inspected upstream commit after run #28 showed its v4 release still embeds Node 20 `upload-artifact`; the pinned composite uses Node 24-compatible `upload-artifact@v7.0.1`.
- Added wave-specific Codebook labels for 48 disease-control and prior-interview disease-change fields from 2013, 2015, and 2018. Frequencies are omitted; prior-disease routing and the unresolved release-data denominator remain explicit. Updated the chronic-disease audit and regression coverage.
- Fixed catalog propagation for 18 already-reviewed 2020 DA002 prior-interview disease-change fields; code 99 remains explicitly tied to absence of disease at the prior interview. Added a regression check against the site catalog.
- Added source-reviewed Yes/No/Don't know labels for three 2011 and three 2020 self-awareness items. Kept self-awareness separate from doctor diagnosis and omitted Codebook frequencies; added catalog propagation checks.
- Added calendar-year units for 22 phenotype-side disability-onset fields and retained the conditional disability/verification routes. Kept categorical 2018 prior-wave verification fields separate; added a regression check and documented that year responses are not biological disease onset.
- Added questionnaire-confirmed Yes/No/Don't know options for 11 chronic-disease self-awareness fields across 2013, 2015, and 2018. Omitted Codebook frequencies, preserved wave-specific disease eligibility routes, and kept self-awareness distinct from physician diagnosis.
- Refreshed the handoff README, current directory snapshot, and project estimate with the post-build catalog counts and the 68-test validation result.
- Strengthened private-wave validation to require the 2013 `crosssection` and `longitudinal` sample flags. Aggregate QA confirms 2015/2018/2020 weight coverage matches `crosssection=1`; the existing 2013 prepared table lacks both flags and is now explicitly `CHECK`, with no inference about the 349 rows lacking individual weights.
- Reduced full metadata-catalog build time by pre-indexing wave/field module and source-archive lookups. Same-method profiling fell from 107.8 seconds to 53.6 seconds; output records were verified unchanged. Documented the profiling method and limits in `audit/metadata_builder_performance_2026-10-23.md`.
- Added official Codebook time units for eight 2011–2018 prostate-illness diagnosis-time fields, preserving separate year/age components, male-only routing, and the exclusion of prostate cancer. Codebook extrema remain explicitly non-valid-range evidence; added unit and caveat regression checks.
- Added official, wave-specific physical-activity purpose labels for nine 2015/2018/2020 fields, omitting frequencies and preserving the distinction between activity purpose and activity dose; added regression checks and a source audit.
- Added a guarded `--finalize-only` metadata build path for changes that do not alter upstream mappings. Full rebuild remains the default; the faster mode is documented with its source/crosswalk freshness requirement and was run successfully against the full-build output.
- Added source-specific status for 51 household-income/expenditure fields whose exact wave Codebook entries show numeric summaries without categorical menus; transcribed five wave-specific `ga001` Yes/No menus without frequencies. Routes, units, special values, release coding, and eligibility remain pending; added tests and audit records.
- Propagated 608 pension numeric/count fields whose official Codebook fields are located but have no discrete response categories; preserved six entries with more specific existing review states. The status does not certify units, routes, release coding, or analysis eligibility. Added a dated audit and catalog/UI regression checks.
- Rebuilt the full E/P metadata catalog and propagated 73 source-reviewed continuous behavior measure descriptions (age/year components, smoking/alcohol quantities and sleep durations) that were incorrectly displayed as “not yet reviewed.” The builder preserves blank category labels, conflicts, and `DO NOT ANALYZE` locks; added regression coverage and a dated audit snapshot. No respondent data or association results were used.
- Renamed the navigation entry that opens the C-class measurement/design metadata catalogue so it no longer implies that the page itself is the methods note; the homepage methods link still goes to the methods cards.
- Added a public methods card explaining the five-wave weight/sample-flag rules, 2013 rebuild gate, PSU candidate status, and unresolved variance-stratum/replicate-weight availability. Linked the detailed survey-design audit and added a regression test so the site cannot lose these key inferential limits. No respondent data or association estimates were added.
- Clarified the Chinese labels and review-state explanation in the measurement/design metadata (C) catalog, including that candidate covariates are not automatic adjustment recommendations and continuous measures may have no discrete value labels. GitHub Pages now deploys automatically when published-site assets or the deployment workflow change on `main`; manual dispatch remains available.
- Propagated all 217 field-level healthcare-access review states into the main E/P catalogue, including insurance coding uncertainty, continuous use counts, conditional hospitalization measures, and cost/bracket structure. This improves metadata provenance and interpretation; it does not make the fields analysis-ready.

## 2026-10-22 (continued)

- Deployed the metadata-only CHARLS ExWAS Atlas to GitHub Pages; the site root, app script and candidate-pair JSON return HTTP 200. Added a dated progress audit that distinguishes the completed public prototype from unfinished field-level review, survey-design resolution and association analysis.

- Added official labels for residence electricity, gas supply, running water, flushable-toilet status, and in-house shower/hot-water categories. Preserved code shifts, the absence of a 2015 electricity field in the public inventory, the distinction between running water and 2020 tap water, and the wording difference in 2020 shower categories. Removed duplicate label rows from the generator; inventory now has 99 wave-field rows. E/P labels total 2,908; all 38 tests pass.
- Added heating-source categories for 2011–2020 and separate heating-availability Yes/No labels for 2015, 2018, and 2020. Fuel remains nominal; 2018 `8=Heating provided` and 2020 `8=Do not heating` stay distinct, and neither measure is presented as pollutant concentration or dose. Housing review table now contains 97 wave-field rows; E/P labeled rows total 2,904; all 37 tests pass.
- Added five-wave interviewer-observed household cleanliness and temperature response labels, preserving `6=Not applicable` from 2013 onward but not inventing it for 2011. Added 2020 tap-water access and waterworks-treatment labels, retaining `997=Do not know` and stating clearly these fields are not contaminant measurements. Reviewed-label inventory now has 89 wave-field rows; E/P labeled rows total 2,898; 36 tests pass.
- Final housing pass added residence business-use status for 2011–2018, the 2018 residence-location and house-type categories, and the 2020 floor/ground-condition category. These remain wave-specific candidates; 2018's location field is not equated to the NBS urban/rural identifier. The reviewed housing label table now has 77 wave-field rows (24 distinct source-code names), E/P reviewed-label rows total 2,886, and all 35 tests pass.
- Follow-up pass added official Yes/No labels for household telephone, broadband, and residential air-cleaner fields, preserving the 2020 code shift (telephone i022, broadband i023, air cleaner i024) and the 2018 air-cleaner source suffix. Total reviewed housing-label rows are now 70; E/P reviewed-label rows are 2,879. Added a wave-specific regression check; all 34 tests pass.
- Reconciled official Codebook categories for dwelling structure, building-age bands, floor type, dwelling independence, elevator access, accessibility facilities, and entrance steps across all five waves. Preserved wave-specific codes (including 2013's unlisted structure code 8, the 2018/2020 "Do not need" response, and 2020 continuous step count), omitted Codebook frequencies, and propagated labels into the main field catalogue, concept-source crosswalk, and housing lookup. Added a source reconciliation note and regression tests; all 33 tests pass. No respondent-level records were read.
- Completed the remaining source-identity audit for social-care helper fields. Corrected the 2011 questionnaire path; recorded DB022/DB023 and DB030/DB031 route semantics and Codebook sparsity in the mapping builder and website metadata. The historical source-identity review queue is now clear; respondent-level applicability remains unverified.
- Corrected the subjective-living-standard audit's 2013 source filename and verified 2011 G003 is the respondent's own five-level assessment while G001/G002 are fictional-family vignettes. Kept 2011 absolute self-rating separate from the 2013 reference-group comparisons. One source-identity audit remains.
- Corrected the side-job audit's 2011 source and line references. The baseline questionnaire confirms the FC019=1 route and FJ001–FJ004 count, hours, income, and bracket meanings; the work generator already used this correct source. Two source-identity audits remain.
- Corrected the 2011 source in the job-search/separation-benefit audit and verified the last-job route (FA007/FA008) plus FL021=Yes follow-up to amount and compensation-service years. FK002 remains questionnaire/codebook-supported; 2011 FL021/FL022 stay questionnaire-only candidates because their Codebook entries are absent. Three source-identity audits remain.
- Corrected the 2011 source and scope in the unpaid-debt audit: the baseline questionnaire excludes house loans but does not say it excludes home-improvement loans. Confirmed the 2011 credit-card item has no explicit zero instruction, so the zero rule remains unassigned; 2018's broader exclusions and explicit zero instructions remain wave-specific. Four source-identity audits remain.
- Corrected the rotating-savings audit's 2011 source path and verified the 2011/2013 HC036=No skip to HD001 and conditional HC037 balance against the actual questionnaires. The 2015 private-lending wording and absent HC036_W3 release field remain distinct and unresolved as documented. Five source-identity audits remain.
- Corrected the respondent financial-assets audit to cite the actual 2011 baseline household questionnaire and rechecked its cash, ownership-share, securities, fund, housing-fund, and employer-held contribution routes. The personal-income builder already used the correct source; no microdata were read. Six source-identity audits remain.

- Re-reviewed the 2011 pension subsidy source against the correctly identified baseline household questionnaire and Codebook. Confirmed FN009 eligibility/skip routing, FN011 annual-versus-lump-sum selector, and six distinct amount fields; corrected the source path and reduced the 2011 source-identity review queue to 7 items. Microdata values and special missing codes remain unverified.

- Corrected the source identity in the pension FN079/FN094 audit: its FN072 supplement is a 2013 Wave 2 item, and the previous path incorrectly described a mislabeled 2013 questionnaire extract as a 2011 baseline. Verified the five FN072 components and route against the correctly named 2013 questionnaire and Codebook; removed this resolved file from the remaining source-identity queue (8 remain).

- Rechecked basic-pension FN028 dates against the correctly identified 2013 questionnaire and 2013/2015 Codebooks: both 2013 and 2015 questionnaires say “start,” while both Codebooks title FN028 as “stop.” Expanded the analysis lock to both waves, corrected the audit citation, and removed it from the source-identity queue (9 remain).
- Rebuilt the full metadata catalog after splitting 2011 `fn024` into a wave-specific current-enrollment concept; that intermediate build had 1,409 E/P concepts. The subsequent FN028 conflict correction merged the two locked wave-specific placeholders; current totals are 1,408 (1,130 exposure-side, 287 phenotype-side, 9 dual-role). No respondent records were used.
- Corrected the 2011 pension `fn024` identity: the old discrepancy came from comparing it with 2013 `FN022_W2` using a mislabeled questionnaire. The correct 2011 baseline `FN024` and Codebook `fn024` share the same three categories and ask current enrollment among respondents who have not completed retirement; 2013 `FN022_W2` remains a distinct prior-enrollment follow-up. Corrected the 2011 `fn035` identity note and removed this resolved audit from the source-correction queue (10 remain).
- Audited 2011 prior non-farm job FL008/FL009 routing, weekly-hours range/check, monthly wage meaning, special values, and bracket fallback against the correct baseline questionnaire. Corrected source path and line references; retained the explicit limit that 2011 Codebook entries were not located. Eleven source-identity audits remain.
- Reconfirmed 2011 DE010–DE012 against the official baseline sleep-vignette wording and Codebook labels; recorded exact source positions and removed this already-corrected audit from the pending source-identity queue. The three items remain C-class vignette metadata, not respondent sleep outcomes. The queue is now 12 audits.
- Rechecked 2011 evidence for cross-concept overlap: confirmed the DA051 household random subsample, DA059/DA061 smoking routes, and DA067 past-year drinking categories. Clarified that 2011 chest-pain items DA003/DA004 are not the later general pain-severity item, and corrected source references. The source-identity correction queue is now 13 audits.
- Re-audited 2011 DB021/DB029 assistive-device wording and skip routes against the correctly identified baseline household questionnaire. Kept the five-option DB021 and seven-option DB029 item families separate, with route-specific eligible denominators; corrected the source citation. The source-identity correction queue is now 14 audits.
- Re-audited agricultural work fields FC001–FC011 against the correct 2011 baseline household questionnaire; corrected the audit’s source path, confirmed questionnaire skips and soft checks, and retained the 2018 FC008 questionnaire/Codebook conflict lock. The source-identity correction queue is now 15 audits.
- Added the 16 official 2011 FL020 checkbox option meanings to the field-level catalog as questionnaire text only; selected, unselected, and missing-value coding remains unverified and every option is locked `DO NOT ANALYZE`. Corrected the audit citation to the actual 2011 baseline household questionnaire and reduced the source-identity correction queue by one.
- Rebuilt the metadata catalog and updated value-label coverage to 2,834 E/P rows across 2,808 wave-fields; no respondent data or association models were used.
- Recorded official Wave 5 Sample Information and Sampling Weights hashes and a source-level verification checklist for the age-domain audit. The local prepared tables cannot yet be matched to those source archives, so the 2020 target age domain remains provisional.
- Rechecked 2011 work-history item `FB010` against the correctly identified official baseline household questionnaire and the wave Codebook. The code discrepancy is confirmed and remains locked; both the work-exposure view and the main catalog now show the conflicting menus and `DO NOT ANALYZE` status. The source-correction register no longer treats this audit as unreviewed.
- Preserved wave-specific locked review states during catalog aggregation, made the metadata rebuild update the current homepage stats block safely, and expanded value-label coverage notes to distinguish exact conflict flags from unresolved source discrepancies.

This file records project-level changes that affect reproducibility, methods, data handling, or the local prototype. Individual variable audits remain documented in `audit/`.

## 2026-10-22

- 对照2011社区问卷修正工业污染字段JB018/JB019的类别方向：Codebook英文字面Poor/Fair/Good/Very good容易误读，网站现按问卷中英锚点显示“很严重/有一些/基本没有/完全没有”，并保留JB019村级单独路由。新增回归检查；社区环境审计同步记录这一差异。
- 为交互平台添加手动触发的GitHub Pages Actions部署工作流。部署包严格指向`site-prototype/dist/`并检查JSON有效性及意外微观数据/压缩文件；默认预期地址为`https://calebchu40-gif.github.io/charls-exwas-atlas/`。部署需要在仓库Settings → Pages选择GitHub Actions并运行工作流；公开发布仍待完成。

- Established the private GitHub repository `calebchu40-gif/charls-exwas-atlas` and pushed the local project on `main`.
- Added repository ignore rules for licensed respondent-level data, temporary outputs, locally derived sample/coverage QA tables, credentials, and machine-specific operational notes. These files remain local where needed and are not part of the Git history.
- Added GitHub Actions checks for the standard-library Python tests, website JSON parsing, and JavaScript syntax. The checks do not download CHARLS respondent data or run association models.
- Declared the preparation-script test dependencies (`pandas` and `pyreadstat`) so CI can import and test the wave-table preparation code reproducibly.
- Fixed the CI dependency setup; the run for commit `b77ca0e` passed all checks.
- Recomputed empty concept-link counts from the final website catalog and corrected an obsolete audit heading/count that had presented historical E/P fields as a current queue. The final catalog has 0 empty E IDs, 0 empty P IDs, and 717 empty C metadata/covariate rows; links remain candidates subject to scientific and design review.
- Added a CI guard that fails if a future website catalog contains an E/P row without a candidate concept link.
- Recorded the official wave-specific age/target-population limits: the 2020 guide says younger cohorts are no longer nationally representative after 2018. Added this limitation to the local prototype and marked the 2020 age domain as unresolved pending source-file verification.
- Changed respondent-data audit scripts to write aggregate QA under the private LocalAppData root by default and added a path guard against common cloud-sync folders. Updated handoff commands; local validation again passed for all five prepared tables and the 31-concept/945-pair availability build.
- Added a suppressed local-only Wave 5 age/weight coverage audit to evaluate the unresolved 45+ versus 50+ target-domain question; 50+ remains a candidate pending source-release verification, not a frozen analysis target.
- Confirmed the current project is still in metadata and methods development: no CHARLS association models have been fitted and the website must continue to show zero reviewed results.

## 2026-10-22：血液检测方法学元数据补充
- 将CHARLS 2011 Blood Users' Guide表2中的11项生化检测方法、批内/批间CV和指南报告检测范围逐项加入血检crosswalk与网页；范围按原表措辞展示，不宣称为LOD。
- 2011 CBC五项仅显示指南的本地CDC检测说明及未提供逐分析物方法/CV/范围；2015 Release Note只列字段定义/单位，因此2015这些 assay 字段保持空值并明确不得继承2011值。另保留来源原单位文本。
- 增加4项回归测试；全套44项通过，Python编译、网页JS语法、diff检查通过。审计：`audit/blood_assay_method_metadata_2011_2015_2026-10-22.md`。
- Pages状态：公开项目授权已由用户确认，但GitHub在变更私有仓库可见性前要求账户邮件验证。当前浏览器停在GitHub Confirm access页面；用户需亲自完成验证。完成后再将Pages设为GitHub Actions部署源、运行工作流并验证站点。尚未公开仓库，也未上线网站。

### 2026-10-22：目录覆盖数与锁定清单一致性复核
按当前catalog及crosswalk重算并更新值标签覆盖数为2,908行/2,882个波次字段；核实现行DO NOT ANALYZE锁定33条，2011 FM033仅保留为已解除锁定的历史说明。新增回归测试，确保目录锁定数与分流清单摘要一致；全套45项测试通过。

### 2026-10-22：新增波次级E/P候选配对查询
新增概念级配对浏览器，允许用户选择波次及E/P候选概念，并查看对应CHARLS源变量码、官方标签、模块、单位和值语义/审核提示。配对数来自概念—源字段crosswalk，排除概念自配对；页面明确不代表人群样本数或统计关联。新增可复现生成脚本并接入全目录构建链；各波候选对数与既有覆盖审计一致。49项测试、JS语法、Python编译和diff检查通过。
- Published the CHARLS ExWAS Atlas to GitHub Pages after the owner made the repository public and selected GitHub Actions as the source. First manual deployment (Run #1, 2026-10-22) succeeded; the root page, JavaScript app, and candidate-pair metadata returned HTTP 200. Live URL: https://calebchu40-gif.github.io/charls-exwas-atlas/.

- Transcribed 2018 official Codebook response categories for 68 chronic-disease treatment fields into the audited E/P catalog, omitting frequencies and retaining conditional questionnaire routes and denominator/release-coding checks. Corrected the ancillary crosswalk's default review state so unlabeled items remain pending rather than appearing reviewed.

2026-10-23 chronic-disease treatment update: commit `190837f` was pushed to `main`; Pages deployment run `39874593820` succeeded. Public site root, catalog.json, and app.js returned HTTP 200. Online catalog has 7,544 rows and includes 68 official 2018 chronic-treatment response label sets, with frequencies omitted and questionnaire-route/release-validation cautions retained. Published bundle is 33 files / 34,098,109 bytes; blocked data/archive extension scan found none. This was a metadata-only update; no respondent records were read and no ExWAS model was fitted.

- Added 125 wave-specific chronic-treatment option labels from the 2011, 2013, and 2015 official Codebooks, without aggregate frequencies. Because those sources identify selected-option categories but do not establish unselected storage, the fields stay locked `DO NOT ANALYZE` pending release-data validation. No category was extrapolated across waves.

- Cross-wave follow-up was published in commit `df0930a`; Pages run [`39875503802`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39875503802) succeeded. The live catalog and status translations were checked for 2011/2013/2015 selected-option labels (`DO NOT ANALYZE`) and distinct 2018 `0=No` labels.

- Corrected the 2011 Codebook parser to normalize spaced variable headings (for example, `da010 2 s4`) to the release variable name. This adds 32 previously omitted treatment option labels; the 2011 count is now 53, and the four-wave total is 225 field-wave label sets. No response values or frequencies were inferred.

- Corrected the 2011 Codebook spaced-header match in commit `4e57ae7`; Pages run [`39876436833`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39876436833) succeeded. The live site now contains all 53 mapped 2011 treatment-field option labels. Early-wave fields retain the unselected-storage warning and `DO NOT ANALYZE` lock; four-wave total is 225 field-wave labels.
- Changed static atlas JSON fetches to revalidate against GitHub Pages ETags instead of bypassing the browser cache, reducing repeat downloads while preserving fresh content checks.
- Deferred topic JSON and the large field/pair indexes until a user opens the corresponding view, reducing first-view network transfer and JSON parsing.
- Split the browser catalogue into generated E/P/C role shards and stopped publishing the build/test master JSON in the Pages artifact; each directory now fetches only its own role.
- Updated GitHub Actions to Node 24-compatible releases after the successful Pages run reported forced Node 24 migration warnings: checkout v5, configure-pages v6, upload-pages-artifact v4, deploy-pages v5, setup-python v6, and setup-node v5. The static-site payload boundary and checks remain unchanged; see `audit/github_actions_node24_update_2026-10-23.md`.
- Verified Pages run #29 (`39913706044`) and metadata validation run #87 (`39913706041`) succeeded on `a4e7a39`; the deployment details no longer report the Node 20 deprecation warning.
- Synced precise source statuses for 170 previously generic-pending employment/work numeric fields from the reviewed work crosswalk. The fields remain without fabricated category labels; 677 E/P catalog rows remain generic pending, while the nonempty-label count remains 3,199. Added Chinese website explanation and regression coverage; see `audit/work_numeric_catalog_status_sync_2026-10-23.md`.
- Extended the work-field sync to include five 2020 questionnaire-derived CAPI formulas with unresolved route validation and two questionnaire/Codebook identity conflicts that remain `DO NOT ANALYZE`. Current E/P catalogue counts are 3,207 nonempty-label rows across 3,181 wave-fields and 670 generic-pending rows; the full suite passes 84 tests.
- Published the work-field CAPI and identity-conflict status update as `00a0657`; Pages run #31 and metadata validation run #90 succeeded, and the live E catalogue returned HTTP 200 with the new statuses.
- Surfaced 33 2011 work fields whose official Codebook category labels were not located, with a source citation and a website note that “not located” does not mean “no categories.” Current generic-pending E/P rows: 637; full test suite: 85 passed.


### 2026-10-24 — residential-history metadata verification

- Published source-reviewed BB007–BB010 residential-mobility routes and durations for 2011/2013, including four previously missing 2011 duration fields. The review preserves the distinct BB007/BB009 branches, conditional missingness, 2011 wording mismatch, and duration units.
- Verified commit `41bd6a3` in GitHub Pages Deploy #93 (`40018980973`) and confirmed the cache-busted public C catalogue contains 986 rows and the reviewed records. This is metadata only; formal E/P concepts, mappings, and association models remain unchanged.


### 2026-10-24 — objective measurement protocol metadata

- Added the public 2011 physical-examination manual to official-source materials. Reviewed 2011 pre-blood-pressure behavior QA017/LI875 and chair-height QH006/LI007, leaving the unresolved chair-field identity on hold.
- Clarified 2013 QH006 as chair height in centimeters and separated 2015 QH006 (chair type) from conditional QH006_1 (other-chair height). These remain C measurement metadata and do not enter E/P association pairs.
- Full catalogue rebuild and all 200 Python tests passed; site C catalogue now has 986 rows. See `audit/objective_measurement_protocol_source_review_2011_2015_2026-10-24.md`.

- Published commit `7903732` in GitHub Pages Deploy #94 (`40021600663`); cache-busted live C catalogue returned HTTP 200 and confirmed all reviewed 2011/2013/2015 protocol records.

- Deployment verification for commit `a5a42e4` is recorded in `audit/public_site_deployment_verification_2026-10-24.md`. GitHub Actions validation run `40042411927` and Pages deploy run `40042411919` succeeded. Cache-busted public checks confirmed E/P/C counts 4,739/2,104/990, all 89 analysis locks, reviewed Wave 5 digital/life-expectancy entries, and no public raw-data catalogue or respondent records. The site continues to identify candidate pairs as metadata-only; fitted models and pairwise complete-case Ns are 0.

### 2026-10-24 — blood-pressure and pulse source review

- Reviewed 2011/2013/2015 official physical-examination/Biomarker questionnaires for repeated BP/pulse measurements, protocol context, and non-completion codes. Systolic and diastolic units are recorded as mmHg; the pulse unit is not explicit (“P”) and remains blank.
- Kept the 2011 LI-manual versus QA-Codebook field identity unresolved; 2013/2015 exact QA field identities are questionnaire-documented. Preserved three readings, 993/999 status codes, test context, and release/analysis eligibility cautions. No Codebook frequencies or respondent records were used.
- Added an idempotent source updater to both metadata pipelines, propagated units and source caveats into the concept-source index and public P shard, and refreshed the objective-measurement asset cache key. See `audit/blood_pressure_pulse_source_review_2011_2015_2026-10-24.md`.
- Full finalization passed 225 Python tests, JSON and JS validation, compilation, and exact 89-row analysis-lock validation. Formal models and pairwise complete-case Ns remain 0.
- Commit `0eaf332` was published in Pages deploy run [#106](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40044331718) and validated in run [#195](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40044331712), both successful. Cache-busted live objective-measurement and P-catalogue assets confirmed units, review states, and the unresolved 2011 identifier caveat; details are in `audit/public_site_deployment_verification_2026-10-24.md`.
- Audited the public 2015 blood-biomarker catalogue against CHARLS's official Wave 3 Blood Release Note: all 16 listed analytes and both sampling/processing fields are represented in the source crosswalk and published JSON, while `Blood_weight` stays a design field rather than an analyte. Added regression coverage and a dated audit; retained the limits that 2015 assay methods are not reported in that release note and must not be inherited from 2011.
- Linked the blood-biomarker catalogue to the exact inventory audit and official Wave 3 Blood Release Note, with regression coverage to preserve the provenance links.
- Reduced repeated catalogue-build scans by indexing source archives and existing output rows by wave/field. Before/after direct-build SHA-256 values match for five generated catalogue files; same-machine cProfile time fell from 74.1s to 57.3s (call count 102.4M to 55.7M). The profile includes subprocess and profiler overhead; full finalization order remains intact. Details: `audit/catalog_build_performance_review_2026-10-25.md`.
- Fixed the GitHub validation dependency on the intentionally ignored 4 MB local raw-variable inventory by adding a 38-row Child-module field-presence manifest (wave/code/module only) and a reproducible builder. Child crosswalk tests now validate against this compact source manifest; no participant data are included.
- Revalidated 2011 community linkage against the official Codebook's aggregate structure and searched available private file metadata for a subcommunity crosswalk; none is currently available outside `community.dta`. The Codebook fingerprint supports release-structure correspondence but does not prove archive identity or identify respondents' subcommunities. The protected audit now counts observed `sub_commuID` rows with blank/whitespace values handled as missing; no merge or source values are exported.
- Clarified the 2011 Cystatin C analysis gate from the official Blood Users' Guide: all blood respondents aged 70+ and a random subsample under 70 were assayed; `bloodweight` is described for blood-draw participation and is not documented as correcting this second-phase assay subsampling. Keep Cystatin C as a catalogue candidate, but require a documented second-phase selection probability/weight or a justified target-sample estimand before population association analysis.
- Extended the survey-design gate for split 2011 neighborhoods: the baseline guide says selected sub-neighborhoods could serve as PSUs and their within-village share affects selection probabilities. Available person/PSU metadata has no such sub-neighborhood key, so `communityID` remains a PSU candidate whose variance role must be verified for these selections. Do not construct a synthetic sub-PSU or stratum.
- Found the official Peking University Open Research Data Platform's 2013 `Weights.tab` file record, but its page marks the file restricted and requires login/access approval. Logged its public metadata as a possible retrieval route; it is not interchangeable with the official CHARLS `Weights.dta` SHA-1 target and cannot be used by the guarded merge until its format, fields, and provenance are verified.

- Verified the public Pages release for `495e2aa`: deployment and metadata-validation workflows succeeded, and the live homepage, app, E/P/C catalogues, behavior payload, and cognition payload matched the reviewed local assets. The deployed memory and alcohol metadata were checked for expected wave-specific fields and caveats; no respondent data or association results are present. Audit: `audit/public_release_verification_2026-10-25.md`.

- 更新项目进度估算，核实线上首页/分类显示与现版本一致，并复查CHARLS官方2013权重资料页的文件版本和SHA1；官方权重二进制仍缺失，保持分析阻断。见 `audit/project_progress_estimate_2026-10-23.md` 与 `audit/wave2_weight_estimand_source_review_2026-10-24.md`。
# 2026-10-25

- Hardened GitHub Pages publishing with a reusable fail-closed browser-asset allowlist. The deploy now rejects statistical data, archive, and unknown file types and validates JSON recursively before upload.
- Added focused tests and an audit note for the public payload guard.
## 2026-10-25 同步2011 FM055分类背景与禁分析清单

- 更新总禁分析清单，纳入2011 National Baseline User Guide第5节提供的劳动模块分类背景，同时明确该指南仍未确定FM055三个子字段的逐字段分类对应关系、GB版本或官方查找表，ISCO字段也未解释；三个字段继续锁定。
- 移除FM055审核同步脚本内已过时的固定状态常量，并增加回归断言，防止专题审计与总清单再次不一致。验证：45项目录状态测试及92条禁分析清单核对通过。

## 2026-10-25 更正2018房产名册C类字段审核标签

- 将11个已按官方问卷和Codebook审核的2018 HA025_W4[i]房产位置字段从“自动关键词发现、字段含义未审”改列为已审阅的房产上下文元数据，说明槽位对应分别登记的房产位置，不代表受访者当前住所，也不是个人调整协变量。
- 同步来源目录、候选序列及C类网站目录；添加回归断言和对应中文子类别标签。住房字段及C类标签专项共7项测试通过。未读取个人数据或改变任何模型纳入决定。

## 2026-10-25 区分2020核心人口学字段与测量上下文

- 将2020年龄、性别及公式输入字段的C目录状态改为逐字段来源描述；明确年龄派生和性别输入/预载的角色差异，并将主观预期寿命题目标年龄、访员观察访谈语言保留为测量上下文，避免把它们统称为age/gender协变量。
- 更新8条来源含义已审阅字段的子类别及中文显示标签。波次/角色限定回归测试、C子类别标签测试及完整422项Python测试均通过；公开负载、92项分析锁、JS语法检查通过。不改变任何调整模型决定，不读取个人数据。
## 2026-10-25 Link partner-context C/E overlaps to reviewed sources

- Linked six exact-wave C rows for partner highest education and respondent marital status to their reviewed candidate exposure concepts and official questionnaire/Codebook sources.
- Preserved respondent versus partner distinction, original category codes, and route-specific denominator caveats; an E/C overlap is not a default adjustment recommendation and cannot adjust for itself.
- Added the updater to both build paths, a row-level audit, a public C-directory regression test, and a Chinese subcategory label. The three cohabitation rows remain outside this update because their cross-wave route definitions are not fully resolved. The C directory remains 982 rows; keyword-only subcategory rows decreased to 111 across 61 source codes.
- Validation: clean finalization, all 429 Python tests, public payload validation, exact 92-lock reconciliation, JavaScript syntax, and Python compilation passed. No participant data or frequencies were read; association models and actual pairwise Ns remain 0.


## 2026-10-25 — 家庭经济支持目录扩展（v125已部署；CI待修复）

- 新增非同住父母、岳父母、子女之间的家庭经济支持收/支六类候选概念，覆盖原始目录中对应的2011、2013、2015、2018字段。
- 保留个人索引槽位、钱/实物、定期/非定期、时间间隔及分档上下界；不汇总、不跨波重编码。2011问卷与Codebook字段号/子项描述差异保留为分析前核验警告。
- 全量目录重建后 E/P/C 为6,008/2,107/982 行，候选概念1,554，E/P概念—来源映射8,009条；仍无正式关联模型。
- 新增四项交叉表测试；本机475项完整回归通过，GitHub Validate #497 单测步骤失败，原因未定位；Pages Deploy #246 已成功。
# 2026-10-26 Review 2011 Community Questionnaire Part F mortality-context fields (local update)

- Added two provisional community-context candidate mappings for JF017_1 (total community deaths since 2008) and JF017_2 (community suicide deaths). They are aggregate counts without a population denominator, not individual mortality outcomes or rates.
- Kept JF018 open-text disease names/counts and JF020 informant identity as C-only metadata; excluded direct identifiers. Added source audit and regression coverage without publishing respondent text, records, or Codebook frequencies.
- Part B coverage review then mapped 42 JB029 facility/organization fields and three infrastructure-year fields, and classified four other-specify text fields plus JB040 as C-only; all 127 raw JB fields now have a disposition. Full 159-step finalization completed in 7.6 minutes. Local E/P/C shards=6,175/2,116/1,001; 1,601 E/P concepts; 8,185 E/P source mappings; 2011 metadata co-availability=141,835 (not analytic N). Full suite (501 tests), public-payload validation, 92-lock validation, JS syntax, and diff checks pass. Current public app remains v129; local cache is v132.
# 2026-10-26 Audit all 2011 community Part A fields

- Reconciled all 80 JA-prefixed fields against the official questionnaire and Codebook: 69 candidate mappings and 11 explicit metadata/unresolved dispositions. Added eight contextual candidate concepts covering office establishment, administrative boundary and urban transition, land-rights certification, land development, expropriation, homestead allocation and surname concentration.
- Preserved CAPI scope and routed-year denominators; retained JA012 as C-only because questionnaire wording (paddy field) conflicts with Codebook wording (irrigatable). Excluded open-text surname and homestead-source values; no Codebook frequencies or respondent data were used.
- Full 159-step finalization completed in 6.9 minutes. Local E/P/C=6,278/2,116/1,013; 1,618 E/P concepts; 8,288 E/P source mappings; 2011 metadata co-availability=145,456 (not analytic N). Generic pending labels=0; formal association models=0; exact 92 locks unchanged.
- Full local suite: 513 tests pass. Public payload, exact 92-lock, JS syntax, deferred-loader and diff checks pass. Part A content remains local pending commit/deployment.

# 2026-10-26 Make community source-review tests reproducible in clean CI

- GitHub Validate #520 exposed that seven source-review tests depended on the ignored local `audit/raw_variable_catalog_v1.csv`. That file contains local module row counts and source archive names and remains untracked.
- Added a sanitized 719-field 2011 community inventory with only wave, module, variable code and official field label; updated tests to use it and added a schema/content guard. No respondent records, answer values, frequencies, module row counts or source archive names are included.
- Local suite: 508 tests pass; public payload and exact 92-lock checks pass; JS syntax/deferred-loader checks and `git diff --check` pass. Remote Validate after the fix is pending. The Part E migration site update is live in Pages Deploy #258 (app v132).
# 2026-10-29 Make the active execution plan visible

- Promoted the current task and ordered next steps to the top of the public active-plan page and linked it from the repository landing page.
- Recorded the metadata-only Wave 1 field-name scan: `community.dta` contains `sub_commuID` and `communityID`; 13 other readable modules did not expose a subcommunity field; one module header scan failed for memory allocation and remains unresolved. No respondent values were read.
- The PSU/variance gate remains open, formal association models remain at zero, and no participant data or restricted outputs were added to GitHub.

# 2026-10-29 Complete Wave 1 sub-PSU header search

- Finished a metadata-only header scan of all 15 official All Data modules. The community module alone contains `sub_commuID`; the other 14 modules do not. The module that failed in pyreadstat was inspected through pandas' header-only reader, without reading observations.
- Confirmed from official PSU, Weight, and Blood file headers that the PSU file has community/geographic descriptors but no respondent sub-PSU crosswalk, explicit variance stratum, or replicate weight; the Blood file contains `bloodweight`.
- The protected read-only readiness check passed source and prepared-frame provenance/hash verification, then blocked model fitting because the bound analysis-review record is missing. No real association model was run.

# 2026-10-29 Prepare Wave 1 independent methods review packet

- Added a public-safe reviewer packet with the confirmed PSU/weight/source-header evidence, the 105-coefficient family definition, and explicit unresolved design decisions. It contains no participant-level information or private analysis outputs.
- Official Blood User Guide review confirmed fasting was requested but non-fasting participants were still sampled; the guide notes non-fasting glucose can be higher. The existing pilot runner omits the fasting field for glucose/triglyceride handling, so this is now a pre-analysis specification item and blocks model execution until frozen.
- The `qc1_va003` Stata header has no value-label set, and the local Wave 1 Codebook/Blood User Guide do not specify its numeric coding. The coding must be sourced before any fasting subgroup or adjustment is implemented.
- Source and prepared-frame checks pass, but the independent analysis-readiness record is absent. Real association models remain at zero.

# 2026-10-29

- Rechecked the official Wave 1 document index and protected Blood ZIP member list for the fasting-code gap. The public release lists a general Codebook and Blood Users' Guide; the Blood archive contains only the data file, while `qc1_va003` has no Stata value labels. No official Wave 1 numeric/special-missing mapping was found; adjacent-wave `bl_fasting` coding remains non-transferable.
- Added a gate-by-gate status matrix to the independent methods review packet so source verification, unresolved design/measurement gates, internal pilot approval, and public release approval cannot be conflated.
- Added a Wave 1 survey-variance decision matrix for the documented PSU hierarchy, incomplete split-community respondent mapping, candidate parent-community clustering approximation, and independent reviewer decisions required before real association models.
- Corrected the community-key quick summary: blank `sub_commuID` values are stored as whitespace. After normalization, split-community respondents still cannot be assigned to a final sub-PSU from the released keys. Protected QA details and identifiers remain outside the repository.
- Updated the active work plan and Wave 1 file-inventory audit; no real-data model was run and no result payload was published.

## 2026-10-29 — Review Wave 2/3 weights and blood release notes

- Recorded protected intake and metadata-only header review for official Wave 2 weights, Wave 3 weights, and Wave 3 blood archives; no participant values or row-count-derived sample sizes were published.
- Documented that Wave 2 has distinct cross-sectional and longitudinal weights plus a cross-sectional biomarker weight, but no longitudinal biomarker weight; documented official ID transformations for cross-wave linkage.
- Documented that Wave 3 provides cross-sectional `Blood_weight` with blood-response adjustment; its `bl_fasting` labels apply only to Wave 3 and cannot be used to infer Wave 1 `qc1_va003` coding.
- Added the detailed public-safe source review memo and corrected the active plan's later-wave intake status. No models or tests were run; design and independent-review gates remain closed.

## 2026-10-29 — Add Wave 3–5 sample and weight files to protected intake

- Verified the private server intake manifest marks official 2015 Sample_Infor, 2018 Weights/Sample_Infor, and 2020 Weights/Sample_Infor archives as official-SHA1 verified; copied them only into protected local intake and matched local SHA-256 to the private manifest.
- Ran metadata-only Stata header review and recorded cross-sectional flags, death/interview metadata, and weight fields. No participant values or analysis rows were read, merged or published.
- Read official Wave 4/5 guides and added a review-draft target/weight matrix covering Waves 1–5, including survey-domain handling, module-specific blood weights, Wave 2 ID transformation, panel-weight gaps, and the Wave 4 HCAP age-specific frame.
- Corrected earlier statements that later-wave design inputs were absent and appended superseding status notes to historical review documents. No model/test was run; formal models remain blocked on sample/weight applicability and PSU/variance/method review.

- Confirmed the official Wave 2 PSU archive (document 319) is byte-identical to the already SHA-1-verified PSU archive from baseline in the private manifest, copied it to protected local intake, and checked only the Stata header. The field set provides no county-stage unit or explicit stratum. Documented this result in the wave-specific source/weight review; no participant data or models were accessed.

## 2026-10-29 — Wave 2 preloaded DOB calendar review

- Compared the official Wave 2 questionnaire routes and Codebook with metadata-only labels in protected Wave 1 and Wave 2 prepared Stata schemas. No respondent values, IDs, or row-level records were read.
- Confirmed Wave 2 has preloaded `zba002_*` DOB fields and `ba001_w2_1` confirmation; when the respondent confirms the date, the questionnaire skips `ba002/ba003`. `ba003` therefore applies to the newly reported `ba002` date only and cannot automatically classify the preloaded date as solar/lunar.
- Wave 1 `ba003` is only a candidate calendar source after exact cross-wave linkage, date agreement, and precedence review. Official lunar-conversion code is available, but conversion cannot be applied until the input date/calendar provenance is established.
- Added `audit/wave2_age_preload_calendar_review_2026-10-29.md` and updated the active plan. Age construction remains unfrozen; no analysis or tests were run. Formal CHARLS association model count remains 0.

## 2026-10-29 — Source-bound Wave 1 rebuild and frame-key reconciliation

- Re-ran the protected Wave 1 metadata-only intake preflight. All four authorized official files still match the user-reviewed source manifest and stored local fingerprints; no respondent values were read at preflight.
- Rebuilt Wave 1 from the verified All Data, PSU, Weight, and Blood releases into a new versioned folder under the protected local root. Preserved the prior prepared tables. The new respondent table has source-bound manifest provenance and passed the fail-closed provenance/hash gate.
- Added a private aggregate reconciliation reading only respondent IDs, community keys, `ind_weight_ad2`, and `bloodweight`; no questionnaire, exposure, or outcome values were read. Official interview/blood-target and `ind_weight_ad2` denominator totals agree at aggregate level; all Blood IDs join to the person spine and the Blood Guide's complete-sample count aligns with positive `bloodweight`. A residual set of positive adjusted-weight IDs remains outside the Demographic_Background spine; exact key counts remain in protected QA. The denominator is only partially reconciled at the person-key level and the design frame is not certified.
- Updated the provenance gate to read the prepared manifest alongside an explicitly supplied versioned frame, while enforcing that both remain inside the private root. This makes versioned rebuilds auditable without replacing the default legacy table.
- Updated the Wave 1 pilot runner to honor `CHARLS_EXWAS_DATA_DIR`, so a versioned source-bound Wave 1 frame can be selected for a single run without changing the default multiwave directory. Its source gate still runs before any model; age, design, independent review, and analysis readiness gates remain in force.
- Added `scripts/audit_2011_official_frame_reconciliation.py` and updated the Wave 1 design inventory, active plan, and changelog. Only AST/static parsing and `git diff --check` were used; no test suite or association model was run. Formal model count remains 0.

## 2026-10-29 — Reconcile Wave 1 blood target and source weight at aggregate level

- The official baseline/blood target total now agrees with the Codebook nonmissing `ind_weight_ad2` total; all Blood-file IDs join to the source-bound person spine, and positive `bloodweight` records align with the official Blood Guide complete-sample denominator. A residual set of positive adjusted-weight IDs remains outside the Demographic_Background spine, so person-key reconciliation is still partial.
- `bloodweight` is the source-grounded starting weight for blood-outcome pairs, pending pair-specific exposure response and age-domain checks. It does not resolve county strata, split-community final PSU mapping, or variance review; models remain blocked.

## 2026-10-29 — Route Wave 1 runners to a source-bound frame

- Updated the Wave 1 pilot's data path to honor `CHARLS_EXWAS_DATA_DIR` and documented the new source-bound metadata state. This allows a versioned protected Wave 1 rebuild to be selected without overwriting or globally changing the multiwave prepared-data directory.
- The fail-closed provenance, survey-design, age, frozen-plan, independent-review, and disclosure gates are unchanged. No association model or test suite was run.

# 2026-10-29 — Review the official CHARLS lunar-to-solar implementation

- Inspected the pinned CHARLS-maintained Stata `.ado`, help file, MIT license, and binary Mata lookup-table header. Documented its ordinary/lunar-leap lookup behavior, supported string-date interface, provenance requirements, and why a production Python port cannot be assumed equivalent without validation.
- Confirmed no Stata executable is available on the current local or private server PATH. No participant DOB values were read, no conversion/age derivation or association models were run, and no tests were run.
- Added `audit/charls_official_lunar_conversion_implementation_review_2026-10-29.md` and updated the active plan. Next: establish an authorized Stata execution path or validate an independent implementation against the pinned official lookup using synthetic dates before deriving any participant age.

## 2026-10-29 — Clarify baseline age-screening and target-frame interpretation

- Rechecked the CHARLS official sample-design page and added its age-selection route: household screening selects an eligible member aged over 40; selected persons aged 45+ become main respondents with spouses interviewed, while selected persons aged 40–44 enter the refresher-reserve route.
- Clarified that this screening description alone does not define the blood-analysis weight denominator. The denominator must still be reconciled to the official Blood Guide/Weight release and person-level frame before freezing eligibility. The page describes county sorting by region, urban/rural category and GDP before PPS, but does not provide a released per-county variance-stratum key.
- Updated the Wave 1 estimand/design memos and active plan. No participant values or models were accessed/run.

## 2026-10-29 — Trace residual Wave 1 weight IDs across official modules

- Added a protected aggregate-only audit that verifies the current source-bound frame, temporarily extracts the official All Data RAR only beneath the private root, and reads only module `ID` columns plus `Weight.ID`/`ind_weight_ad2`.
- Found that all residual positive-weight IDs absent from the Demographic_Background spine occur in at least one other official module. This rules out a simple Weight-only-key explanation but does not establish interview completion, age, blood eligibility, or denominator inclusion. Exact small-cell counts and keys remain private.
- A direct protected ID-only comparison also found none of those residual IDs in Blood.dta. Reconciled the official guide's 17,708 interview count with the 2011 Codebook's 17,705 Demographic_Background.ID observations: the public materials reviewed do not explain the difference, so the counts are now explicitly kept distinct in the design memo.
- Read only the official Weight `mainr` value for the residual records: each has an interpretable main-respondent/spouse label. The missing Demographic rows still prevent age/sex verification, so this narrows but does not close the frame/age gate.
- Temporary extraction was automatically removed. Added `scripts/audit_2011_weight_ids_across_modules.py`; only Python bytecode compilation was used for a static syntax check, with no tests or models run.

## 2026-10-29 — Separate official weight construction from variance-design evidence

- Re-read the official Wave 1 Users' Guide weight-construction section and recorded the staged selection probabilities, sub-neighborhood share for split communities, within-household respondent selection, and PSU-dummy nonresponse adjustments (including aggregation of non-estimable village dummies).
- Clarified that these point-weight construction details do not provide the public PSU-dummy aggregation map, explicit variance strata, final sub-PSU respondent crosswalk, or a prescribed variance estimator. Also documented why module-specific response weights do not automatically resolve missingness in the other member of an E/P pair.
- Updated the Wave 1 variance decision memo and active work plan. No participant data, analyses, or tests were used.

## 2026-10-29 — Require official age derivation evidence before Wave 1 model readiness

- Static review found the Wave 1 readiness schema required a review of age-domain eligibility but did not separately require that the age covariate itself be derived from official CHARLS fields/maintained algorithms with validation evidence. The historical water pilot uses a provisional Harmonized CHARLS D age candidate, which is not an official age derivation.
- Added a required `official_age_source_and_derivation` gate to the Wave 1 readiness validator and templates. Approval now requires an official CHARLS source tier, field, method, source anchor and validation evidence. Added the readiness schema to the applicable analysis-plan fingerprints so stale approvals cannot carry forward.
- Updated the family-runner review and active plan. The age gate remains unresolved; no participant values, models, or tests were used.

# 2026-10-29 Pin the cited Python lunar-date source package

- Downloaded the PyPI lunardate 0.1.5 source archive into protected local reference storage and confirmed it against the PyPI-published SHA-256. Static inspection found GPLv3 metadata, a supported 1900–2049 range, and explicit leap-month input. No source archive was added to GitHub.
- CHARLS's official help cites this project but does not name a release; 0.1.5 postdates the help's June 2014 version, and PyPI reports no build provenance. It remains a candidate reference rather than an exact reproduction of the official Stata `.mmat` table. No examples or participant dates were run in this step.

## 2026-10-29 — Correct Wave 2 checksum scope and advance source preflight

- Fixed Wave 2 provenance handling: the CHARLS-published SHA-1 applies to the downloaded ZIP, not its extracted `Weights.dta`. The metadata gate now verifies the ZIP and inspects its unique DTA member header in protected temporary storage. The merge command also verifies that the supplied DTA is byte-identical to that member.
- Rechecked the official Wave 2 weights and Wave 3 blood archives. Both source hashes and required Stata header schemas passed. Outputs remain in the protected local QA directory. No participant values or IDs, flag/weight distributions, merges, or association models were read or run.
- Updated the active plan, outdated intake instructions and handoff status; design/age/weight applicability, variance, independent review and formal analysis gates remain open.
# 2026-10-29 Recheck protected server Wave 2/3 source packages

- Reran the official Wave 2 weights and Wave 3 Blood archive/header audits directly in the private server environment (`pyreadstat 1.3.1`); both official archive hashes and required member headers passed. Aggregate metadata reports remain in owner-only `private/qa_outputs/` on the server.
- Confirmed Wave 1 official inputs remain present and the active design gates are still age derivation and final PSU/variance review. No respondent values or IDs, joins, associations, or tests were processed. Formal model count remains zero.
- Rechecked the public Pages home (HTTP 200) and formal results payload (HTTP 404), consistent with no reviewed results being published. Removed a duplicate paragraph from the server-only progress log and refreshed its current plan entry.

# 2026-10-29 Exhaustively compare lunar-date converter releases

- Added a reusable synthetic-only audit that enumerates valid lunar dates over CHARLS's documented converter domain and compares caller-supplied `python-lunardate` source releases without bundling the GPL implementation.
- Pinned 0.1.4 and 0.1.5 had identical valid-date coverage and zero output differences: 49,949 ordinary and 1,521 leap mappings, matching the dimensions stated in CHARLS's official converter source. This supports source lineage but does not establish cell-by-cell equality to the official `.mmat` table.
- No CHARLS participant dates were read or transformed. Calendar/leap-month and incomplete-date routing remain under review; the age/model/design gates remain closed.

# 2026-10-29 Prepare a protected Wave 1 age-interval candidate

- Added a reusable exhaustive synthetic comparison for the CHARLS-cited lunar-date source releases and documented that the exact official lookup dimensions match while cellwise `.mmat` parity remains unverified.
- Strengthened age-input provenance with a hash of the protected age-input file, then added a source/hash-guarded derivation that stores only lower/upper completed-age bounds and source-route labels under the protected local root. It accounts for missing interview day and unmarked leap-month ambiguity, preserves unresolved dates, and never filters the frame by candidate age.
- Generated and header-checked the private candidate table locally. It is not model-approved; Wave 1 variance and age-method review gates remain open, and no associations or public results were produced.


# 2026-10-29 Recover Wave 1 county-unit candidate from official ID coding

- Added a protected aggregate audit for the official Wave 1 identifier rule: first six household-ID digits identify county-level units, the seventh identifies community, and person IDs extend the household ID. The audit binds to the verified prepared-data manifest and official PSU file hash; it prints no identifiers or row-level data.
- Reproduced the key consistency audit locally and on the private server. This recovers a county-prefix candidate key and corrects the earlier assumption that no county-unit key was available. It does not recover implicit strata/PPS ordering or respondent-to-subcommunity membership, and it does not approve a variance estimator.
- Retrieved the official CHARLS lunar2solar Mata matrix to protected reference storage. It matches the pinned upstream commit; exact matrix parity remains pending because no licensed Stata/Mata runtime is installed locally or on the private server.

# 2026-10-29 Reconcile historical exploratory pilot with formal-model status

- Audited the protected local legacy pilot tables without reading respondent microdata. Their technical structure and declared BY/Bonferroni arithmetic pass, while the original manifest documents provisional Harmonized CHARLS D age and unstratified communityID Taylor approximation; source, target, and survey-design review remain open. Historical exploratory outputs remain private and are not formal approved models or public Atlas results.
- Reviewed the server's installed R `survey` documentation against the recovered county/community key. Without stage-specific FPC/probability information the package uses only first-stage variance; adding a second ID alone would not validate multi-stage variance. Added a review memo and corrected active status language. No real-data association was fit.
# 2026-10-30 Rebuild Wave 1 and reconcile official frame keys

- Re-ran the official Wave 1 metadata-only intake audit, then rebuilt the 2011 person table under the access-controlled local CHARLS root from the verified source manifest. The aggregate-only reconciliation read IDs, community keys, and official weights; it found a mismatch between non-missing individual-weight IDs and the person spine, full Blood ID linkage, and complete respondent-to-released-community-key coverage. Split-subcommunity PSU assignment, strata, and the weight denominator remain unresolved. No small-cell counts, IDs, exposure/outcome values, row-level QA, or association results were added to the repository. Added a count-free discrepancy question to the unsent official methods draft.

# 2026-10-30 Locate unmatched Wave 1 weight IDs without exposing them

- Added an aggregate-only protected audit that reads only `ID` columns from the official All Data RAR modules and the individual-weight file. Some unmatched IDs also occur in other personal questionnaire modules, so their absence from the demographic spine cannot be treated as proof of nonresponse or ineligibility. Module presence is not a denominator decision. Updated the unsent official inquiry accordingly; the QA JSON, identifiers, and module-level small counts remain only in the protected local directory. No respondent exposure/outcome values or models were read/run.

# 2026-10-30 Separate biomarker-weight linkage from individual-weight mismatch

- Corrected the Wave 1 aggregate reconciliation so it evaluates `bloodweight` against the actual Blood-file respondents and the official complete-sample denominator, separately from `ind_weight_ad2`. Re-run confirms the blood file, positive `bloodweight`, and prepared person spine are fully linked and the released blood-record count matches the official guide. The full baseline target denominator remains partly reconciled; the ancillary individual-weight mismatch is retained for follow-up but no longer mislabeled as the blood-model weight failure. Final PSU/strata variance and independent methods review remain unresolved; formal models remain zero.

# 2026-10-30 Refresh independent review packet with confirmed bloodweight linkage

- Updated the reviewer packet to distinguish the blood-specific `bloodweight` used for the primary biomarker estimand from the separate `ind_weight_ad2` mismatch. The released Blood rows and positive biomarker weights link to the prepared person spine, and the released count agrees with the official Blood Guide. The remaining review focuses on full target denominator, exposure-module nonresponse, age-domain, and complex-survey variance. No participant-level data or small-cell counts were added.
# 2026-10-30 Enforce association and variance status consistency

- Hardened the public result-payload validator so successful fits cannot be labeled `Design not fit-ready`, and non-success rows must carry that label. This prevents internally contradictory public records while preserving the separate requirement for independent survey-design review.
- No participant-level data or association results were read or changed. Validation was reviewed statically; no test suite or synthetic fit was run.

# 2026-10-30 Report verified Wave 1 source provenance accurately

- Fixed the metadata-only Wave 1 intake report, which always emitted `source_provenance_verified_by_script: false` even when the user-reviewed manifest, official document IDs/URLs, filenames, and all four local hashes matched. It now derives the field from complete file presence and a clean source-identity review; the separate design-review-pending gate is unchanged.
- No respondent values were read and no association model or test suite was run.

# 2026-10-30 Gate Wave 3 Blood merge on ID-only frame review

- Updated the Wave 3 pipeline review to distinguish the historical missing-file status from the current protected intake. The official 2015 All Data and Blood archives match their posted SHA-1 values, and a protected respondent base table has been built. A frame-linkage discrepancy remains under private review; no association model or public result was produced.
- Hardened the merge runner so it validates prepared-frame membership using ID columns before loading any Blood measurement fields, and applies owner-only file permissions to private merged outputs and QA on POSIX systems. The current run correctly stopped at the ID-only gate and created no merged Blood table.
- No respondent IDs, lab values, small-cell counts, or restricted QA were added to GitHub. No test suite was run.

# 2026-10-30 Build Wave 3 from the official Sample_Infor frame

- Reconciled the Wave 3 person-spine mismatch against the official 2015 Codebook. The public Codebook defines `Sample_Infor` as the sample-information module and `crosssection` as the cross-sectional flag; private ID-only checks showed the Blood module and positive `Blood_weight` target are supported by this frame.
- Updated the wave-table builder to use `Sample_Infor` as the 2015 spine, record the selected spine in the prepared-data manifest, and keep missing demographic fields missing. The Blood merge now requires that manifest declaration. Rebuilt the protected Wave 3 frame and completed the one-to-one Blood merge without row expansion; participant-level files and detailed QA remain owner-only on the server.
- No respondent identifiers, individual values, or exact QA counts were added to GitHub or Pages. Formal association models remain 0; no test suite was run.

# 2026-10-30 Audit Wave 3 age-route completeness in private storage

- Added a provenance-bound aggregate-only Wave 3 age-route audit. It checks the official 2015 archive/Blood hashes and merged-table manifest before reading only `crosssection`, interview timing, and BA002/BA003/BA004_W3 route/date fields. It does not read IDs or Blood/exposure outcomes; exact QA counts are written only under owner-only private storage.
- The restricted audit surfaced unresolved birth-route responses, missing/unrecognized calendar codes on known routes, and unknown month/day entries; no out-of-range observed date components or incomplete interview year/month were flagged. These are not age estimates or sample counts for publication. Age intervals/lunar parity, covariates, survey design, and methods review remain open; formal models remain 0.

# 2026-10-30 Clarify the Wave 3 Blood weight target

- Reviewed the official 2015 Blood Release Note and Codebook. The released `Blood_weight` targets the cross-sectional blood-response sample; it is built from the cross-sectional individual weight with logistic blood-response adjustment and 99th-percentile capping. CHARLS does not provide a ready-made Wave 3 panel blood weight.
- Clarified the initial Wave 3 association frame: Sample_Infor, cross-sectional domain, blood-module participation and the applicable positive Blood_weight, followed by pair-specific complete-data eligibility. This closes the weight-scope documentation question, not the final estimand or variance gate. No panel interpretation, substitution with general Biomarker/individual weights, or association result is authorized.
