"""Map 2013 health-related work absence as a wave-specific functional outcome candidate."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
rows=[{
 "concept_id":"health_related_workdays_missed_2011",
 "concept_label":"因健康问题导致的工作缺勤天数（2011）",
 "domain":"health and work function",
 "wave":"2011",
 "code":"fc013",
 "module":"work_retirement_and_pension",
 "source_label":"Num. of Days Missed due to Health Problems",
 "unit":"days in the past year (questionnaire range 0-366)",
 "value_semantics":"Number of work days missed in the past year due to health problems; the interviewer instruction explicitly records 0 when no work days were missed.",
 "mapping_status":"2011 single-wave phenotype candidate; official questionnaire item and response range reviewed; denominator/routing review required",
 "caveat":"The item follows the agricultural work and workplace-location questions, but the questionnaire wording asks broadly about missed work days. Do not infer the eligible work universe from placement alone. Verify the released-data routing and denominator before analysis. Explicit 0 means no work days missed among respondents asked; structural missingness is not zero. This is work-related functional impact, not a diagnosis or general disability score.",
 "questionnaire_source":"sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt",
 "source_archive":"CHARLS2011_Dataset.zip"
},{
 "concept_id":"health_related_workdays_missed_2013",
 "concept_label":"健康原因导致的工作缺勤天数（2013）",
 "domain":"health and work function",
 "wave":"2013",
 "code":"fc013",
 "module":"Work_Retirement_and_Pension",
 "source_label":"Days No Work due to Health Problems",
 "unit":"days in the past year (0–366)",
 "value_semantics":"Number of work days missed last year due to health problems; questionnaire explicitly instructs 0 when no work days were missed.",
 "mapping_status":"2013 single-wave outcome candidate; questionnaire/codebook field identity and response range reviewed",
 "caveat":"Asked within the agricultural work branch routed from FA001=1; preserve this eligibility universe. Explicit 0 means no missed work days among routed respondents, not absence of health problems. Structural missingness must not be recoded as zero. This is work-related functional impact, not a diagnosis or general disability score.",
 "questionnaire_source":"sources_official/CHARLS_2013_Questionnaire_extracted.txt",
 "source_archive":"CHARLS2013_Dataset.zip"
},{
 "concept_id":"health_related_workdays_missed_2015",
 "concept_label":"因健康问题导致的工作缺勤天数（2015）",
 "domain":"health and work function",
 "wave":"2015",
 "code":"fc013",
 "module":"Work_Retirement_and_Pension",
 "source_label":"Days No Work due to Health Problems",
 "unit":"days in the past year (questionnaire range 0-366)",
 "value_semantics":"Number of work days missed last year due to health problems; the interviewer instruction explicitly records 0 when no work days were missed.",
 "mapping_status":"2015 single-wave phenotype candidate; official questionnaire wording and response range reviewed; denominator/routing review required",
 "caveat":"The item follows the work-location and job-satisfaction questions; verify the released-data routing and eligible work universe before analysis. Keep separate from the 2013 and 2018 items until their route and work-scope equivalence is established. Explicit 0 means no missed work days among respondents asked; structural missingness is not zero. This is work-related functional impact, not a diagnosis or general disability score.",
 "questionnaire_source":"sources_official/CHARLS_2015_Questionnaire_extracted.txt",
 "source_archive":"CHARLS2015r.zip"
},{
 "concept_id":"health_related_household_agricultural_workdays_missed_2018",
 "concept_label":"健康原因导致的自家农业工作缺勤天数（2018）",
 "domain":"health and work function",
 "wave":"2018",
 "code":"fc013",
 "module":"Work_Retirement",
 "source_label":"Days Not Working due to Health Problems",
 "unit":"days in the past year (questionnaire 0–366; Codebook observed max 365)",
 "value_semantics":"Number of days the respondent could not perform household agricultural work in the past year because of health problems; questionnaire explicitly codes 0 when no work days were missed.",
 "mapping_status":"2018 single-wave outcome candidate; questionnaire/codebook field identity and response meaning reviewed; observed maximum differs from questionnaire permitted maximum",
 "caveat":"Located in the Self-Employed Agricultural Work module; retain its eligible work universe. Explicit 0 means no missed household agricultural work days, not absence of health problems. Structural missingness must not be recoded as zero. This is not a diagnosis or general disability score and is kept separate from 2013 FC013 because wording and module scope differ. Check values and routing against the approved release data dictionary.",
 "questionnaire_source":"sources_official/CHARLS_2018_Questionnaire_extracted.txt",
 "source_archive":"CHARLS2018r.zip"
}]
for code, cid, label, meaning, caveat in [
    ("fd030", "health_related_workdays_missed_current_job_2018", "Health-related workdays missed at current job (2018)",
     "Days missed at the current job in the past year due to health problems; questionnaire instructs interviewers to mark 0 when no work days were missed.",
     "Current-job route only. Explicit zero means no missed work days among routed respondents; structural missingness is not zero. This is functional impact, not a diagnosis."),
    ("fd031", "paid_health_related_workdays_missed_current_job_2018", "Fully paid health-related work-absence days (2018)",
     "Number of the FD030 health-related missed work days that were fully paid; asked only when FD030 is nonzero.",
     "Conditional on FD030>0. Preserve the paired relation FD031<=FD030 and 0-366 questionnaire range; do not treat skipped responses as zero."),
]:
    rows.append({
        "concept_id":cid,"concept_label":label,"domain":"health and work function","wave":"2018",
        "code":code,"module":"Work_Retirement","source_label":label,
        "unit":"days in the past year (questionnaire range 0-366)","value_semantics":meaning,
        "mapping_status":"2018 single-wave phenotype candidate; official questionnaire wording, route, and range reviewed",
        "caveat":caveat,"questionnaire_source":"sources_official/CHARLS_2018_Questionnaire_extracted.txt",
        "source_archive":"CHARLS2018r.zip"
    })
out=ROOT/"audit/health_work_absence_crosswalk_v1.csv"
pd.DataFrame(rows).to_csv(out,index=False,encoding="utf-8-sig")
print("health-related work absence mappings=6 across 6 wave-specific concepts; no respondent data read")
