# Employment and work-organization field review, 2026-10-21

## Scope and source rules

This review extends the metadata-only CHARLS E/P atlas. It reads official questionnaires and codebooks, plus the project's official-source variable catalog; it does not read respondent-level records or estimate associations. The files reviewed for the latest mappings were the official 2013/2015/2018 questionnaires and codebooks and the official 2020 English questionnaire/codebook. Source documents are retained under `sources_official/`.

Work, occupation, benefits, and location can be useful social or occupational context candidates in a broad exposome-phenome discovery atlas, but many are not direct chemical, physical, or ambient exposures. They remain exploratory candidates with wave-specific labels, eligible populations, and routes. A mapping does not assert causal direction or analysis readiness.

## Added candidate mappings

The work crosswalk now includes:

- 2020 daily hours across side jobs (`FE002`), separate from `FE001` days per week.
- 2020 own-household agriculture work months, days per week, and hours per workday (`FB005`–`FB007`). The day/week question has an interviewer floor rule of 1 for occasional work; its value scale cannot be treated as a simple zero-inclusive dose.
- 2015/2018 household-agricultural-work satisfaction (`FC012_W3`), retaining the five-level source response and work-specific universe.
- 2020 current employer location relative to residence (`FC004`) as a coarse category only. Conditional place-name fields are not included as exposures, geocoded values, or public outputs.
- 2011–2018 occupation/type of most recent job (`FL001`), last-job location category (`FL004`), whether the former employer remains in existence (`FL007`), and last-job worker arrangement (`FL013`). These are retrospective, last-job measures for their routed populations; they are distinct from current-job fields.
- Coarse workplace-location categories for paid agricultural work, household agricultural work, non-farm self-employment businesses, and unpaid family businesses, each kept separate by work type. 2020 current-employer location remains separately mapped. No place-name strings are included.
- 2011/2013 reasons for paying social insurance through another work unit and the other unit's broad location; 2011/2013 employer and other-unit monthly contribution amounts as separate candidates. Amounts remain conditional on the respondent knowing/reporting the amount.
- 2011/2013 current-work-unit planned retirement processing (`FD026`) and completed processing (`FD028`) as separate concepts; 2013 individual work-injury insurance coverage remains separate from employer-provided coverage.
- 2018 current main-job arrangement (FC020_W4/FC021_W4), multiple-job flags (FC019_W4), and household-farm work type (FC023_W4) are mapped with their route combinations. XF7 is the CAPI-derived main-job arrangement summary and is linked as a source alternative; do not include it alongside its inputs without a prespecified estimand.
- 2011–2020 wage payer source (workplace/employer, dispatch company, individual), 2020 labor-contract period type and conditional year/month components, and the 2015/2018 maximum employer-purchased work-accident insurance payout have been mapped as separate employment-condition/benefit candidates.
- 2020 current-employer start year/month (FC019_1/_2) and conditional corrected year/month (FC018_1/_2) are linked to the same date-component concept but their precedence must be resolved from FC018. The FC018 parent is C route/verification metadata. `xmainjobdays` was reclassified from E to C metadata because its official questionnaire formula repeats a conditional branch; it is excluded from E/P until that definition is resolved.
- 2013/2015 `FA006_W2` prior-work recovery fields now separately map agricultural-work stop/start dates and reason, prior non-agricultural-job stop date/reason, paid-employer continuity and unpaid-family-business continuity; preserve the prior-wave work-status routes and exclude employer/business names from public exposure measures.
- 2011 and 2015 `FC013` health-related days unable to work were added as separate P candidates. The official 2011 item asks broadly about work missed due to health problems; the questionnaire location alone does not establish its denominator. The 2015 item follows work-location and agricultural-work-satisfaction questions. Both preserve a route/denominator verification gate and distinguish explicit zero from structural missingness. They are not merged with 2013 or 2018, whose routes/work scopes differ.

All mappings remain candidate records and are not approved statistical tests. The annual crosswalk build and role override now keep the 2011/2015 `FC013` fields on the phenotype side.

## 2013/2015 employer-start-date correction route

The 2013 and 2015 questionnaire/Codebook identify `FD011_W2_2_1/_2` as year/month fields asked after a returning respondent rejects the prior-wave record that they were already working for that unit. These fields now join the existing current-employer start-date component concept as correction-route alternatives. They are not an additional event; analysis must use the applicable route and must not count both the preloaded date and corrected date. The 2013/2015 questionnaires explicitly tie the branch to the prior-work record and route into the current-employer module. The routine `FD011_1/_2` route remains separately visible.

## 2018 cross-wave work transitions added in the latest review

The official 2018 questionnaire pages 176–181 route work-history questions using prior-wave and current-wave work status/type. The crosswalk now includes six transition families: not working to working (FA010_W4), working to not working (FA011_W4), household-farm-only to other work (FA012_W4), other work to household-farm-only (FA013_W4), employed work to non-farm self-employment (FA014_W4), and non-farm self-employment to employed work (FA015_W4). Each event keeps its own date components, reason, work type and conditional details; the employer-comparison family FD003_W4 is separately mapped. Correction answers, alternate dates, -1 unable-to-recall codes, severance/retirement-allowance distinctions and relative business-transfer responses remain explicit. These are routed longitudinal transitions, not population-wide employment status measures.

## Rebuild and checks after the first date-field batch

The full metadata build completed successfully with `python scripts/build_ep_atlas_metadata.py`.

- Work crosswalk contains 858 value-label/source mapping rows; the main work-exposure concept mapping has 599 wave-field links.
- Candidate field catalog: 7,868 wave-field rows (E 4,901; P 2,181; dual-role 164; C 622), of which 7,246 are E/P rows.
- Candidate concept union: 1,247 (E 973, P 279, overlap 9; E-only 968, P-only 270).
- E/P concept-source links: 6,185; every E/P source link matches a candidate catalog field. Full concept-source crosswalk: 6,350 rows, including 165 C rows; 6,347 match the directory and 3 directory-external rows are design/eligibility metadata.
- Metadata co-availability pairs, not observed sample sizes: 2011 103,929; 2013 106,042; 2015 109,387; 2018 88,393; 2020 12,448.
- The employment/work-organization subcategory now has 38 E rows across 27 source codes without a linked concept; these form the next review backlog. They are not counted as approved indicators.
- No individual records were analyzed and no association model was fit.

The corresponding source crosswalk is `audit/work_exposure_crosswalk_v1.csv`; generated candidate fields and concept links are `audit/charls_atlas_candidate_fields_v0.csv` and `audit/ep_concept_source_crosswalk_v1.csv`. Rebuild with `python scripts/build_ep_atlas_metadata.py`.


## 2013 self-employed unemployment-insurance coverage

`FI001S3` is an individual coverage checkbox in the self-employed social-insurance module, not the employer benefit item `FG003S3`. The 2013 questionnaire page 176 routes FI001–FI011 only when the respondent has not processed retirement and asks whether pension, health, unemployment, work-injury or maternity insurance is obtained through self-employment. `FI001S3` is now indexed as a single-wave candidate with its self-employment and retirement-status denominator. It must remain separate from employer-provided coverage and coverage through another work unit/job service center. Evidence: `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (p. 176) and `sources_official/CHARLS_2013_Codebook_extracted.txt` (p. 774; response label only, no frequency used).


## 2013/2015 FA006_W2 longitudinal work-history recovery

The 2013 questionnaire pages 139–141 and 2015 pages 125–130 route the prior-interview work-history recovery using prior-wave status/type (ZF1/ZF5–ZF10) and current work route. We added separate two-wave candidate concepts for the stop date and reason for prior-wave agricultural work (`FA006_W2_1_1/_2`, `_1A`), the start date of agricultural work since the prior interview (`FA006_W2_2_1/_2`), the stop date and reason for the prior-wave non-agricultural job (`FA006_W2_3_1/_2`, `_4`), and whether the respondent remained with the prior employer or unpaid family business (`FA006_W2_2A_3`, `W2_2C_3`). The agricultural and non-agricultural events remain distinct, as do paid-employer and unpaid-family-business continuity. Date components remain separate; reason items are single categorical reports, not causal attributions. Prior-wave employer/business names and identity corrections are not published as exposures; they serve only to interpret who enters the follow-up route.

Source evidence: `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (pp. 139–141), `sources_official/CHARLS_2015_Questionnaire_extracted.txt` (pp. 125–130), and corresponding wave Codebooks around the FA006_W2 entries. Codebook frequencies were not used.


## Employer/other-work-unit contribution-amount knowledge

The official 2011 baseline and 2013 questionnaires use `FG011` for knowledge of the respondent's and employer's social-insurance contribution amounts, conditional on the employer insurance route. They use `FI008` for the analogous knowledge question when participation is through another work unit (2011 baseline questionnaire; 2013 questionnaire p. 177, with the associated conditional route). Each is a three-category response about awareness of the respondent's and payer's amounts; neither is the contribution value. We added separate employer-route and other-work-unit-route candidate concepts across 2011/2013. They remain distinct from the numeric contribution fields `FG012/FG013` and `FI009/FI010`; route skips are not zero. The 2011/2013 Codebooks provide response labels (2011 Work/R retirement/pension section; 2013 pp. 767/775); frequencies were not used.


## Repeated planned-work-stop age questions (2011/2013)

Official 2011 baseline and 2013 questionnaires use the same question wording/definition for `FC018`, `FG015` and `FI012`: approximate age at which the respondent plans to stop all income-related activities and unpaid family-business work; 0 means continue while physically able. `FG015` is in the employer social-insurance route and `FI012` in the other-work-unit/self-employment social-insurance route. They now join the existing FC018 candidate concept, but remain visibly separate source fields. Do not count multiple same-wave answers as independent concepts or choose a route-priority rule without authorized data/protocol verification. Keep distinct from `FK003` general expected retirement age and from actual retirement or pension eligibility age. Evidence: 2011 baseline questionnaire and 2013 questionnaire pp. 151, 169, 177; wave codebook response labels only.


## 2011 duplicate other-work-unit contribution reason and 2013 employer noncoverage reason

The 2011 baseline questionnaire contains `FG006` and `FI004` in two routes asking why the respondent contributes social insurance through another work unit. The five response meanings match, so `FI004` is linked to the existing other-work-unit reason concept as a route-specific duplicate, without creating another indicator; preserve the section/coverage route. The 2013 questionnaire p. 166 asks a multi-select `FG004` reason for not being covered through the employer. `FG004_S2` specifically means work-based insurance is available locally but the employer does not provide it. It is indexed as a single-option candidate with the noncoverage parent route and multi-select caveat; do not assume it applies to every listed insurance type or recode missing/unselected storage without data-dictionary validation. Sources: `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`, `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (p. 166), and wave Codebooks for item identity/response labels; no frequencies used.


## 2026-10-21 current-job, family-business, and prior-work dates

Questionnaire and Codebook review added seven separate candidate concepts, with 30 wave-field links: 2013 current-job start (FD012_W2_5), 2013 current-work activity start (FD013_W2_5), 2013/2015 current non-farm self-employment start (FH008), 2013/2015/2018 unpaid family-business participation start (FH018), most-recent-job start and stop dates (FL002/FL003, 2013–2018), and last-worked date reported in the non-employment/job-search module (FK001, 2013/2015). Year and month components remain separate. Routes and respondent universes stay attached to each source family; FK001 is not merged with FL003.

The 2018 FH008 codebook label suggests a business founding date, while the 2018 questionnaire wording and prior-wave FH008 use a respondent work-start meaning. It is excluded from the personal self-employment start concept pending reconciliation against the official release metadata. The 2011 versions of these fields have generic codebook labels and are not inferred into the harmonized concepts without reviewing the source identity.

Evidence: `sources_official/CHARLS_2013_Questionnaire_extracted.txt` (FD012_W2_5/FD013_W2_5 printed p.157; FH008/FH018 and FK001/FL002/FL003 in the corresponding work-history, self-employment, family-business and retrospective-job sections), `sources_official/CHARLS_2015_Questionnaire_extracted.txt` (FH008/FH018 and FK001/FL002/FL003 sections), `sources_official/CHARLS_2018_Questionnaire_extracted.txt` (FH018 and FL002/FL003 sections), plus corresponding wave Codebooks. No frequencies or individual responses were used.


## 2026-10-21 employment continuity, last-job reason, and correction branch

The official 2011 baseline and 2013 questionnaires both ask FC002 for the number of farm employers worked for in the past month, after FC001=Yes (paid farm work for at least 10 days in the past year). The existing concept now covers both waves; the 2020 FC002 employer-organization item remains separate.

Three further source families were added without conflating their universes: 2013 FD012_W2_3 records whether the respondent still did the specific task reported at the prior interview (not whether they stayed with the same employer); 2018 FL020_W4 is a single categorical reason for stopping the last job/work activity, distinct from the 2011–2015 FL020 multi-select checklist; 2020 FA018/FA019 records the retrospective stop date/reason after denying the prior-wave working record and confirming nonwork. The 2020 correction branch remains `DO NOT ANALYZE` until the prior-status/date logic and approved-release coding are reconciled. FA018 month `-1` is unable to report; preserve the year/month components and route. Questionnaire category labels are stored without codebook frequency counts.

Source evidence: 2011 baseline questionnaire FC001–FC002; 2013 questionnaire pp.149 and 155; 2018 questionnaire pp.202–204 and corresponding Codebook; 2020 English questionnaire p.59 and Codebook. The 2020 date/reason questions are not combined with routine FA016 work exit or the 2013/2015 FK001/FL003 reports.

## Rebuild after the second employment batch (superseded on 2026-10-22)

- Work crosswalk: 858 value-label/source rows, including 599 main work concept wave-field links; the retirement-history append is produced by `scripts/build_retirement_history_exposure_crosswalk.py` after `scripts/build_work_exposure_crosswalk.py`. Run the master entry point to preserve that order.
- Candidate catalog remains 7,868 wave-field rows (E 4,901; P 2,181; E/P 164; C 622). Candidate concept union: 1,247 (E 977, P 279, overlap 9; E-only 968, P-only 270).
- E/P concept-source links: 6,185, all matched to the candidate catalog. Full crosswalk: 6,350 rows (C 165; 6,347 matched, 3 directory-external design/eligibility items).
- Metadata co-availability pairs, never observed sample sizes: 2011 103,929; 2013 106,042; 2015 109,387; 2018 88,393; 2020 12,448.
- Employment/work-organization backlog: 38 E rows across 27 codes. No individual-level data or association models were used.


## 2026-10-22 employment backlog role audit and latest rebuild

The remaining 38 employment fields were reviewed against the official questionnaire route. Thirty-six fields were prior-wave status recovery/validation inputs, CAPI work-status summaries, or interviewer comparisons of employer/business names. They are now C-role metadata in `audit/catalog_role_override_review_v1.csv`; company-name strings are not exposed as public indicators. The remaining 2011 FD009 and 2020 FC008 have questionnaire/Codebook identity conflicts and are isolated as separate candidate concepts with `DO NOT ANALYZE` status. They are not merged with formal-employee indicators from other waves. The employment/work-organization E subcategory now has zero unlinked fields.

The master build completed successfully after applying the role overrides. Current catalog: 7,868 rows (E 4,865; P 2,181; dual-role 164; C 658; E/P 7,210). Candidate concept union: 1,249 (E 979, P 279, overlap 9; E-only 970, P-only 270). E/P concept-source links: 6,187, all matched. Full source crosswalk: 6,352 rows (6,349 matched and 3 directory-external design/eligibility items). Work crosswalk has 860 value-label/source rows, including 601 main work-concept links; retirement-history mappings are appended by the master build after the base work mapper.

Metadata co-availability, not sample size or eligible N: 2011 104,132; 2013 106,042; 2015 109,387; 2018 88,393; 2020 12,523. No individual records were read and no association models were fit.
