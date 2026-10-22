"""Add questionnaire-confirmed pension constructs and unit-specific components."""
from pathlib import Path
import re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
raw=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
base_path=AUDIT/"pension_exposure_variable_mapping_v1.csv"
base=pd.read_csv(base_path,dtype=str,encoding="utf-8-sig").fillna("")
lookup={(str(r.wave),str(r.variable).lower()):r for r in raw.itertuples(index=False)}
rows=[]

def add(wave,code,concept,label,construct,*,unit="",values="",value_source="",status="official questionnaire/codebook item; candidate mapping; route and analysis eligibility require review",caveat=""):
    key=(str(wave),str(code).lower())
    rec=lookup.get(key)
    if rec is None: raise SystemExit(f"missing raw metadata: {wave}/{code}")
    scheme_hint = ("government/public-institution/enterprise basic pension loop (2018 Part 1)"
                   if concept.startswith("pension_makeup_contribution_") else
                   "supplementary or plan-specific pension" if "supplement" in concept else "")
    rows.append({"wave":wave,"code":code,"concept_id":concept,"concept_label":label,"domain":"social protection","module":rec.module,
      "source_label":rec.variable_label,"mapping_status":status,"construct":construct,"scheme_hint":scheme_hint,
      "caveat":caveat or "Official question is conditional on the pension plan/route; preserve wave, scheme slot, special missing codes, and conditional denominator.",
      "source_archive":rec.source,"value_labels":values,"value_label_status":"official answer labels transcribed; frequencies omitted" if values else "continuous/structural component; see unit and questionnaire",
      "value_label_source":value_source,"unit":unit})

# Questionnaire-confirmed pension transitions, source work units and plan-specific measures.
# Keep wave-specific routes and response labels; these are candidate E mappings, not harmonized
# analytic variables or respondent-level results.
add("2013","fn064_w2_2_","resident_pension_transfer_source","居民养老保险转入来源",
    "source pension scheme from which current residents' pension participation was transferred",
    values="1=Rural pension; 2=Basic pension insurance of firms; 3=Other",
    value_source="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    caveat="仅在当前参保居民养老计划并回答FN063_w2=Yes后询问；3=Other的开放说明字段不作标准类别。保留原始类别及路由；不要把跳题、空白或未应答推断为未转入。")

work_unit_source_values="1=Current work unit; 2=Last work unit; 3=Work unit that processed retirement; 4=None of the above"
for wave,code in (("2011","fn025"),("2013","fn023_w2"),("2015","fn023_w2")):
    add(wave,code,"pension_benefit_work_unit_relationship","养老金所关联的工作单位关系",
        "work-unit relationship associated with reported government/institution or enterprise pension insurance",
        values=work_unit_source_values,
        value_source=f"sources_official/CHARLS_{wave}_Baseline_Household_Questionnaire_extracted.txt" if wave=="2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="方案限定且按当前/上一份/办理退休单位/无匹配单位分类；仅对相应政府事业单位或企业职工基本养老保险路由适用。预载文本和其他单位详细名称不纳入；2015问卷与Codebook以问卷选项作为类别定义，保留各自源码。")

provider_type_values="1=Government; 2=Institutions; 3=NGO; 4=Firm; 5=Individual; 6=Other"
for wave,code in (("2011","fn027"),("2013","fn025_w2"),("2015","fn025_w2")):
    add(wave,code,"pension_provider_work_unit_type","养老金提供单位类型",
        "type of the work unit providing the reported pension insurance",values=provider_type_values,
        value_source=f"sources_official/CHARLS_{wave}_Baseline_Household_Questionnaire_extracted.txt" if wave=="2011" else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="只在相应方案题中的FN025/FN023选择None of the above后询问；是条件性工作单位类型，不代表所有参保者雇主分布。2011–2015跨波标签按各波问卷保留。")

work_unit_location_values="1=Same as permanent address; 2=Another village/neighborhood in permanent address county/city/district; 3=Other; 4=Abroad"
for wave in ("2013","2015"):
    add(wave,"fn026_w2","pension_employer_work_unit_location_relative_to_permanent_address","养老金提供工作单位相对户籍/常住地址位置",
        "relative location of the work unit providing pension insurance",values=work_unit_location_values,
        value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="仅对FN023_w2=4(None of the above)后的单位详情路径询问。仅映射位置类别码，不映射省市县/村居文本槽位；2015问卷列有Abroad选项，Codebook摘要未显示该选项的观测频数。")

# The same pension-program location family in the later questionnaire uses current residence
# and different answer categories; retain the concept family but make the changed reference explicit.
add("2018","fn085_w2","pension_program_participation_location_relative_to_residence","养老金计划参保地点相对居住地位置",
    "location category of pension-program participation relative to the residential reference used in that wave",
    values="1=Same as current residence; 2=Other township/subdistrict or village/neighborhood within current-residence county/city/district; 3=Other place; 997=Unknown",
    value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
    caveat="2018以当前一般居住地为参照，2013/2015的fn085_w2以永久地址为参照且选项粒度不同；不把类别码强行等值。只纳入位置类别，不纳入详细地理文本；2018问卷该项处于尚未开始领取相应养老金待遇的条件路径。")
for wave in ("2013","2015"):
    add(wave,"fn085_w2","pension_program_participation_location_relative_to_residence","养老金计划参保地点相对居住地位置",
        "location category of pension-program participation relative to the residential reference used in that wave",
        values="1=Same as permanent address; 2=Another village/neighborhood in permanent-address county/city/district; 3=Other; 4=Abroad",
        value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="2013/2015以永久地址为参照，且属于具体养老金项目路径；2018改用当前一般居住地并细化本县范围，跨波类别不视为一一对应。只纳入位置类别，不纳入详细地理文本。")

# Wave 2 supplemental-plan type can extend the already-reviewed Wave 4 concept.
for wave in ("2013","2015"):
    add(wave,"fn032_w2","pension_supplementary_defined_benefit_or_contribution","补充养老金计划给付/缴费确定类型",
        "supplementary pension plan defined-benefit versus defined-contribution structure",
        values="1=Defined-benefit retirement pension; 2=Defined-contribution retirement pension",
        value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="仅对相应雇主补充养老金计划路径适用；2013/2015此变量与2018 fn032_w4的被问资格/路由存在差异，按波次保留，不把未问当作任何一种计划。")

add("2013","fn069_w2","new_rural_social_pension_participation","是否参加新型农村社会养老保险（新农保）",
    "current participation in New Rural Social Pension Insurance",
    values="1=Yes; 2=No",value_source="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    caveat="2013该题直接询问当前是否参加，Yes后跳至FN071；No后进入多选未参保原因。与居民养老计划类型及领取待遇区分；不将条件性原因槽位当作独立暴露。")

add("2013","fn074_w2","new_rural_pension_contribution_payer","新农保参保缴费承担者",
    "person/family member responsible for New Rural Social Pension Insurance contribution",
    values="1=Myself; 2=My children; 3=Other family member or relative; 4=Others",
    value_source="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    caveat="按新农保参保者路径询问；类别是缴费承担者，不等同于缴费金额或缴费方式，也不能据此推断未参保者的家庭支持。")

add("2013","fn077_w2","pension_monthly_benefit_amount","每月养老金领取金额",
    "current monthly benefit amount from the New Rural Social Pension Insurance",
    unit="CNY/month",value_source="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    caveat="仅对已开始领取新农保待遇者询问（FN075=Yes）；不把未领取/未问编码成零。金额有效值、特殊码及分析分母待取得逐波数据后核验。")

for wave in ("2013","2015"):
    add(wave,"fn080_w2","oldest_old_pension_allowance_receipt_status","是否领取高龄老人养老金补贴",
        "receipt status of the old-age pension allowance for the oldest old",values="1=Yes; 2=No",
        value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="计划特异的补贴领取状态；Yes后续问开始领取时间和当前金额。它不等同于一般退休养老金领取，且不得将条件性缺失当作No。")

for wave in ("2013","2015","2018"):
    add(wave,"fn037_w2","pension_defined_contribution_account_balance_check","是否查看过缴费确定型养老金账户余额",
        "ever checked the account balance for the referenced defined-contribution pension plan",values="1=Yes; 2=No",
        value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="仅在FN032对应缴费确定型(DC)方案的条件路径提问；2013 Codebook只列出No观测，问卷仍有Yes回答结构。不得把未问或结构性跳题解释为No。2018题目还绑定具体养老金计划名称。")

# The Harmonized CHARLS D documentation identifies Wave 1 FN024 as the
# enrollment item, but the 2011 codebook categories do not match the response
# options in the baseline questionnaire's FN022_w2 routing. Keep the concept
# searchable while explicitly blocking analytic use until codes are resolved.
add("2011","fn024","pension_past_basic_plan_participation_when_not_currently_enrolled",
    "当前未参保者既往政府/事业单位或企业基本养老金参保",
    "prior participation in government/public institution or enterprise basic pension among respondents routed as not currently enrolled",
    values="1=Yes, government and institutions; 2=Yes, basic pension insurance of firms; 3=No (2011 codebook labels; questionnaire response schema differs)",
    value_source="sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; Harmonized_CHARLS_D.pdf (Wave 1 variable list)",
    status="candidate field; Harmonized CHARLS D confirms Wave 1 FN024 identity; 2011 codebook/questionnaire response-code discrepancy unresolved; DO NOT ANALYZE",
    caveat="The 2011 questionnaire's routed FN022_w2 asks respondents reporting no current enrollment whether they previously participated; it offers 1=government/institutions, 2=enterprise basic insurance, 3=both, 4=neither. The 2011 codebook field fn024 instead labels 1=government/institutions, 2=enterprise basic insurance, 3=No. Preserve this as a candidate directory mapping only; do not recode or model until the official release-specific value schema is reconciled.")

# Wave 2 explicit retirement-plan disposition when eligibility contribution years are insufficient.
plan_values="1=Pay remaining premiums in one payment at retirement; 2=Receive a one-time payment at retirement and not get a pension; 3=Will not receive a pension"
add("2011","fn040","pension_supplementary_defined_benefit_or_contribution","企业补充养老金计划给付/缴费确定类型",
    "employer supplementary enterprise pension defined-benefit versus defined-contribution plan",
    values="1=Defined-benefit retirement pension; 2=Defined-contribution retirement pension",
    value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="仅对FN039=1的企业补充养老金参保者询问；与后续波次同名计划类型候选对应，但应保留波次方案结构和参保资格。")
for code,unit,concept,label,construct in (
    ("fn042_1","age in years","pension_supplementary_expected_benefit_start_timing","预期开始领取补充养老金待遇时间","expected benefit start age for employer supplementary pension"),
    ("fn042_2","years from interview","pension_supplementary_expected_benefit_start_timing","预期开始领取补充养老金待遇时间","expected years until employer supplementary pension benefit start"),
):
    add("2011",code,concept,label,construct,unit=unit,
        value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        caveat="FN039=1企业补充养老金计划路径；年龄与距当前年份数是不同回答单位，原字段分开保留。Codebook中Years组件仅见极少观测，估计资格须由获准数据核验。")
add("2011","fn043_1","pension_supplementary_combined_monthly_contribution_amount","本人及单位每月补充养老金缴费总额",
    "combined monthly contribution by respondent and employer to supplementary enterprise pension",unit="CNY/month",
    value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="仅对FN039=1补充企业养老金路径；Codebook记录的有效观测很少，需检查目标人群和测量缺失，不能推广到全体养老金参保者。")
add("2011","fn043_2","pension_supplementary_personal_monthly_contribution_share","本人补充养老金缴费占比",
    "respondent's percentage share of supplementary enterprise pension contribution",unit="percent of combined contribution",
    value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="FN039=1补充企业养老金路径；这是本人承担比例，不是金额。有效回答仅为少量样本，分析分母和有效范围须数据级复核。")
for code,unit,concept,label,construct,obs_caveat in (
    ("fn044_1","CNY/month","pension_supplementary_db_expected_monthly_benefit_amount","DB计划预期月养老金待遇","expected monthly benefit from defined-benefit supplementary plan","Codebook reports few observations; preserve sparse-response warning."),
    ("fn044_2","percent of retirement wage","pension_supplementary_db_expected_benefit_as_salary_ratio","DB计划预期待遇占退休工资比例","expected DB pension benefit as percentage of retirement wage","The Codebook reports no observations for this component; do not analyze unless the released data confirm responses."),
    ("fn044_3","CNY lump sum","pension_supplementary_db_expected_lump_sum_benefit_amount","DB计划预期一次性养老金待遇","expected lump-sum benefit from defined-benefit supplementary plan","The Codebook reports no observations for this component; do not analyze unless the released data confirm responses."),
):
    add("2011",code,concept,label,construct,unit=unit,
        value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        caveat="FN039=1且FN040=1（DB）企业补充养老金路径。月金额、工资比例、一次性金额分别建项，绝不换算或合并；"+obs_caveat)
add("2011","fn046","pension_defined_contribution_account_balance_check","是否查看过缴费确定型补充养老金账户余额",
    "ever checked the account balance for the defined-contribution supplementary enterprise pension",
    values="1=Yes (questionnaire response); 2=No (Codebook category)",
    value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    status="official questionnaire/codebook item; candidate mapping, but the 2011 Codebook lists only No; confirm released values before modeling",
    caveat="仅适用于FN039=1且FN040=2（DC）计划。Codebook只显示2=No，未显示Yes观测；状态字段保留作为目录候选，但若获准数据中没有变异则不得估计关联。余额与查看年月子字段未见Codebook观测，不作金额或日期分析候选。")
add("2011","fn047","pension_supplementary_earliest_benefit_eligibility_age","最早可离开现单位并领取补充养老金的年龄",
    "earliest age at which respondent could leave the employer and receive supplementary pension benefits",unit="years of age",
    value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="企业补充养老金参保路径下对可领取待遇资格的预期年龄；不是实际退休年龄，也不是法定退休年龄。按问卷适用计划路由分析。")
for code,unit in (("fn048_1","percent reduction from full benefit"),("fn048_2","CNY reduction amount")):
    add("2011",code,"pension_early_exit_reduction_amount_or_ratio","提前离岗养老金扣减金额或比例",
        "expected pension reduction from full benefits if leaving the job at the referenced age",unit=unit,
        value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        caveat="与FN047年龄及企业补充养老金条件路径关联；比例和金额保持不同单位；仅少量有效回答，且金额字段代码本提示区间/有效值需数据级复核。")
add("2011","fn035","pension_plan_if_qualifying_years_insufficient","缴费年限不足时的养老金安排计划",
    "planned pension disposition when qualifying contribution years are insufficient",values=plan_values,
    value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="仅适用于预计缴费年限不足的特定参保路径；选择的是计划而非实际退休时的缴费/领取行为。三类答案与2013/2015题组对齐为同一候选概念，但仍保留逐波定义与路由。")
for wave in ("2013","2015"):
    add(wave,"fn020_w2","pension_plan_if_qualifying_years_insufficient","缴费年限不足时的养老金安排计划",
        "planned pension disposition when qualifying contribution years are insufficient",values=plan_values,
        value_source=f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        caveat="问卷按养老金缴费年限预计不足的特定路径提问；三类计划保留为名义响应，不推断实际领取或实际补缴。")

# 2018 supplemental pension items use an expanded current/expected/contribution scope.
add("2018","fn030_w4","pension_supplementary_current_expected_status","补充养老金当前参保、领取或预期领取/缴费状态",
    "currently participate/receive or expect future receipt/contribution to supplementary pension",
    values="1=Yes; 2=No",value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt",
    caveat="该题把当前参保/领取与未来预期/缴费合并；不得解释为单纯当前领取状态。")
add("2018","fn030_w4_a","pension_supplementary_scheme_current_or_expected","当前、预期或缴费中的补充养老金计划类型",
    "selected supplementary pension scheme type",values="1=Government/public-servant occupational annuity; 2=Public-institution employee occupational annuity; 3=Enterprise annuity; 4=Unknown type",
    value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt",
    caveat="选择型字段；只把实际勾选的计划类型作为阳性选项，未选槽位不推成否。与当前领取计划类型分开。")
add("2018","fn032_w4","pension_supplementary_defined_benefit_or_contribution","补充养老金计划给付/缴费确定类型",
    "supplementary pension plan defined-benefit versus defined-contribution structure",
    values="1=Defined-benefit plan; 2=Defined-contribution plan; 997=Unknown type",
    value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt",
    caveat="仅适用于对应补充计划的条件分支；正在领取待遇者依问卷跳过该项，缺失不能解释为某种计划。")

# FN014_W4 is in Part 1, covering public-servant, public-institution and
# enterprise basic pensions. Part 2 supplementary pensions begins at FN030_W4.
# Keep the question's four plan-loop slots, unit selector and amount components
# together without calling them supplementary-pension measures.
makeup_caveat="2018问卷第1部分中政府机关、公务员、事业单位或企业职工基本养老保险计划的条件性补缴问题；FN030_W4之后才是补充养老保险部分。金额为补缴总额，不是常规月缴费；保留每个计划槽位及原始单位。"
for i in range(1,5):
    add("2018",f"fn014_w4_a_{i}_","pension_makeup_contribution_required","基本养老金计划是否需要补缴",
        "whether a pension plan requires a make-up contribution",values="1=Yes; 2=No",
        value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt",caveat=makeup_caveat)
# This categorical field selects which unit is used by its paired numeric
# response. It is useful for code lookup, but is not itself an exposure value.
for slot in range(1,5):
    add("2018",f"fn014_w4_b_{slot}_","pension_makeup_contribution_total_amount","基本养老金计划补缴总额",
        "unit-selection component for total pension make-up contribution",values="1=Yuan (CNY); 2=10,000 Yuan (10,000 CNY)",
        value_source="sources_official/CHARLS_2018_Codebook_extracted.txt",
        status="official unit selector linked to amount concept; coding metadata, not a standalone exposure",
        caveat=makeup_caveat+" 此字段选择配套金额字段的元/万元单位；本身不表示补缴金额，不单独建模。")
for slot in range(1,5):
    for unit_slot,unit,label in ((1,"CNY","元"),(2,"10,000 CNY","万元")):
        code=f"fn014_w4_b_{unit_slot}_{slot}_"
        add("2018",code,"pension_makeup_contribution_total_amount","基本养老金计划补缴总额",
            "total make-up contribution required for a pension plan",unit=unit,
            status="official questionnaire-confirmed amount component; interval bounds retained under parent; analysis eligibility pending",
            caveat=makeup_caveat+f" 官方源码单位为{label}；不与月缴金额合并。")
# Bracket components of the two unit-specific make-up amount fields.
for parent_slot,unit in ((1,"CNY"),(2,"10,000 CNY")):
    parent=f"fn014_w4_b_{parent_slot}_"
    for bound in ("min","max"):
        code=f"{parent}_{bound}"
        add("2018",code,"pension_makeup_contribution_total_amount","基本养老金计划补缴总额",
            "unfolding-interval bound for make-up contribution amount",unit=unit,
            status="linked questionnaire interval component; not a point estimate",
            caveat=makeup_caveat+" 这是拒答/不记得/0金额后的区间询问上下界，不是精确金额或独立暴露。")
for component in (1,2):
    for slot in range(1,5):
        code=f"fn014_w4_c_{component}_{slot}_"
        part="year" if component==1 else "month"
        add("2018",code,"pension_makeup_contribution_timing","基本养老金计划补缴时间组成字段",
            f"year/month component for timing of pension make-up contribution ({part})",
            unit="calendar year" if component==1 else "month",
            caveat="逐题确认补缴行为的时间组成项；月份0表示不知道时的特殊录入，须按问卷规则解释，不可把年/月字段当作连续指标。")

# Unit-specific expected benefit responses. Parent FN021 fields select the
# response form; do not treat selector codes as benefit values or combine
# monthly currency with a percentage of final pay.
for wave in ("2013", "2015"):
    for code,concept,label,construct,unit in (
        ("fn021_w2_1","pension_expected_monthly_benefit_amount_untyped_plan","预期养老金月待遇金额（计划类型未细分）","expected monthly pension benefit amount","CNY/month"),
        ("fn021_w2_2","pension_expected_final_pay_benefit_ratio_untyped_plan","预期养老金占退休前工资比例（计划类型未细分）","expected pension benefit as a percentage of pre-retirement wage","percent of pre-retirement wage"),
    ):
        add(wave,code,concept,label,construct,unit=unit,
            caveat="Numeric child field selected by parent fn021_w2 (1=Yuan; 2=Percent). Keep units separate; preserve the FN019/FN020 yes-response route and do not infer zero for skipped, unknown, or refused values.")
for r in raw.itertuples(index=False):
    wave,code=str(r.wave),str(r.variable).lower()
    m=re.fullmatch(r"fn021_w2_([12])_(\d+)_",code)
    if wave=="2018" and m:
        measure_slot,plan_slot=m.groups()
        concept=(f"pension_expected_monthly_benefit_amount_slot_{plan_slot}" if measure_slot=="1"
                 else f"pension_expected_final_pay_benefit_ratio_slot_{plan_slot}")
        label=(f"2018养老金方案槽位{plan_slot}预期月待遇金额" if measure_slot=="1"
               else f"2018养老金方案槽位{plan_slot}预期待遇占退休前工资比例")
        unit="CNY/month" if measure_slot=="1" else "percent of final pay"
        add(wave,r.variable,concept,label,"plan-slot-specific expected pension benefit component",unit=unit,
            caveat=f"Numeric child field for response form {measure_slot} in 2018 plan slot {plan_slot}; its parent selector is fn021_w2_{plan_slot}_. Monthly amount and final-pay ratio are distinct units. Retain plan-slot route; skip/unknown/refusal is not zero.")
for wave,code_pattern in (("2013",r"fn021_w2_bracketbracket_(min|max)"),
                          ("2015",r"fn021_w2_bracket_(min|max)")):
    for r in raw.itertuples(index=False):
        code=str(r.variable).lower()
        m=re.fullmatch(code_pattern,code)
        if wave==str(r.wave) and m:
            add(wave,r.variable,"pension_expected_monthly_benefit_amount_untyped_plan","预期养老金月待遇金额（计划类型未细分）",
                "unfolding interval bound for expected monthly benefit amount",unit="CNY/month",
                status="questionnaire/codebook bracket component linked to monthly-currency benefit; not a point estimate",
                caveat="Interval follow-up bound for the amount-form response only; do not treat as exact monthly benefit or as an independent exposure. Preserve unknown/refusal route.")
for r in raw.itertuples(index=False):
    wave,code=str(r.wave),str(r.variable).lower()
    m=re.fullmatch(r"fn021_w2_(\d+)__(min|max)",code)
    if wave=="2018" and m:
        slot,bound=m.groups()
        add(wave,r.variable,f"pension_expected_monthly_benefit_amount_slot_{slot}",f"2018养老金方案槽位{slot}预期月待遇金额",
            f"unfolding interval {bound} bound for expected monthly pension benefit",unit="CNY/month",
            status="questionnaire/codebook bracket component linked to monthly-currency benefit; not a point estimate",
            caveat="Interval follow-up applies to the monthly-currency child response; it is not an exact amount or independent exposure. Preserve plan-slot route and unknown/refusal handling.")
for code,concept,label,construct,unit in (
    ("fn035_w4_b_1","pension_employer_monthly_contribution_amount","单位每月养老金缴费金额","employer monthly pension contribution amount","CNY/month"),
    ("fn035_w4_b_2","pension_employer_contribution_salary_ratio","单位养老金缴费占工资比例","employer pension contribution as salary ratio","percent of wage"),
    ("fn035_w4_c_1","pension_personal_monthly_contribution_amount","本人每月养老金缴费金额","respondent monthly pension contribution amount","CNY/month"),
    ("fn035_w4_c_2","pension_personal_contribution_salary_ratio","本人养老金缴费占工资比例","respondent pension contribution as salary ratio","percent of wage"),
):
    add("2018",code,concept,label,construct,unit=unit,
        caveat="补充养老金计划条件分母；金额与工资比例为不同测量单位，按本人/单位分别保留。")
for parent,concept,label,construct,unit in (
    ("fn035_w4_b","pension_employer_monthly_contribution_amount","单位每月养老金缴费金额","employer pension contribution interval component","CNY/month"),
    ("fn035_w4_c","pension_personal_monthly_contribution_amount","本人每月养老金缴费金额","personal pension contribution interval component","CNY/month"),
):
    for bound in ("min","max"):
        add("2018",f"{parent}_{bound}",concept,label,construct,unit=unit,
            status="linked questionnaire interval component; not a point estimate",
            caveat="对应金额字段的拒答/记忆困难/零值区间追问；只作为金额区间组成项，不用于工资比例或独立暴露。")

# 2018 supplementary plan expected amount fields have distinct monthly-amount and final-pay-ratio units.
for code,unit in (("fn039_w4_1","CNY/month"),("fn039_w4_2","percent of final pay")):
    add("2018",code,"pension_expected_benefit_amount_unspecified_form","补充养老金预期待遇金额或退休前工资比例",
        "expected supplementary pension benefit in monthly amount or final-pay-ratio response",unit=unit,
        caveat="受补充养老金计划类型和预期领取路由限定；金额与比例分开保留。")
# Reassign parent label from the vague autogenerated concept to the clarified supplementary-plan concept.
parentmask=(base.wave.eq("2018") & base.code.str.lower().eq("fn039_w4"))
base.loc[parentmask,"concept_id"]="pension_expected_benefit_amount_unspecified_form"
base.loc[parentmask,"concept_label"]="补充养老金预期待遇金额或退休前工资比例"
base.loc[parentmask,"construct"]="expected supplementary pension benefit in monthly amount or final-pay-ratio response"
base.loc[parentmask,"caveat"]="受补充养老金计划类型和预期领取路由限定；金额与比例分开保留；问题定义见2018官方问卷。"

# 2018 expected benefit timing selector and its unit-specific numeric components.
for code,concept,label,construct,unit in (
    ("fn065_w2_1","pension_expected_receipt_age_2018_plan_loop","2018具名养老金计划预期领取年龄","expected age of receipt from the named selected pension plan","years of age"),
    ("fn065_w2_2","pension_expected_receipt_wait_years_2018_plan_loop","2018具名养老金计划预期领取等待年数","years from interview until expected receipt from the named selected pension plan","years from interview"),
):
    add("2018",code,concept,label,construct,unit=unit,
        value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
        caveat="按FN058_W4_a每个选择的养老金计划路径询问；FN058_W4_b=Yes（当前已领取）跳过后续时间题。此处年龄与距访谈年数分开，不能把两者共用同一连续变量；拒答/未知/跳题不编码成0。")

# Wave-specific pension timing fields with distinct age and wait-year units.
timing_source = {
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
}
for code,concept,label,construct,unit in (
    ("fn078_w2_1","pension_expected_claim_age_rural_resident","新农保/居民养老预期领取年龄","expected age of claim from the rural/resident pension route","years of age"),
    ("fn078_w2_2","pension_expected_claim_wait_years_rural_resident","新农保/居民养老预期领取等待年数","years from interview until expected claim from the rural/resident pension route","years from interview"),
):
    add("2013",code,concept,label,construct,unit=unit,value_source=timing_source["2013"],
        caveat="FN078在FN075=No后询问新农保/居民养老待遇预期；_1为年龄、_2为距访谈年数。语义与FN065具名计划模块部分重叠，保留来源路径但不得作为独立重复假设计数；不得把未问当作0。")
for wave in ("2013","2015","2018"):
    for suffix,concept,label,construct,unit in (
        ("1","pension_expected_receipt_age_land_requisition","征地养老金预期领取年龄","expected age of receipt of land-requisition pension","years of age"),
        ("2","pension_expected_receipt_wait_years_land_requisition","征地养老金预期领取等待年数","years from interview until expected receipt of land-requisition pension","years from interview"),
    ):
        add(wave,f"fn079_w2_8_{suffix}",concept,label,construct,unit=unit,value_source=timing_source[wave],
            caveat="FN079_W2_8按征地养老金路径询问响应格式，_1为年龄、_2为距访谈年数；仅在对应征地养老金计划路由下适用。年龄与年数不可合并，跳题不是否定或0。")

# 2013 NRSP first coverage date. A source discrepancy locks this candidate from analysis.
for suffix,unit in (("1","calendar year"),("2","month")):
    add("2013",f"fn071_w2_{suffix}","pension_nrsp_first_coverage_date_components","新农保首次覆盖时间组成字段",
        "year/month components for first New Rural Social Pension coverage",unit=unit,value_source=timing_source["2013"],
        status="DO NOT ANALYZE; official questionnaire/codebook range discrepancy requires release-level confirmation",
        caveat="问卷FN071给出的首次覆盖年份为2008–2013，但代码本fn071_w2_1汇总最小值显示1987；在官方发布版数据字典/变量来源得到解释前锁定不可分析。月份0表示不记得；保留原始字段，不推断年份或日期。")

# Required contribution duration is distinct from elapsed years paid and expected wait years.
add("2013","fn073_w2","pension_nrsp_required_contribution_years","新农保领取待遇所需缴费年限",
    "reported number of contribution years required to receive NRSP benefits",unit="years",value_source=timing_source["2013"],
    caveat="新农保参保路径中询问领取待遇所需缴费年数；FN072缴费方式中由子女代缴/年满60岁免缴路径跳过此题。与实际已缴年数及预期等待年数分开；发布数据的0–100范围需核验，不将结构性缺失编码为0。")

# 2011 commercial-pension annual-payment route: annual premium and required duration.
commercial_2011_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
add("2011","fn050","pension_contribution_payer_commercial_program_or_current","商业养老保险缴费承担者",
    "person or entity reported as paying the commercial pension insurance premium",
    values="1=Myself; 2=My employer; 3=My family or relative; 4=Other people",
    value_source=commercial_2011_source,
    caveat="仅商业养老保险参保路径；该题记录缴费承担来源，不等同于保险合同持有人、待遇领取者或缴费金额。类别标签按2011代码本，分析频数不纳入网站标签。")
add("2011","fn052","pension_contribution_method","商业养老保险缴费方式",
    "whether respondent contributes annually or as a lump sum to commercial pension insurance",
    values="1=Annual payment; 2=Lump-sum payment",value_source=commercial_2011_source,
    caveat="FN052=1后询问年度保费fn053及所需缴费年限fn054；FN052=2跳过两项并转入一次性总保费fn055。保留为有实际缴费方式含义的E候选，同时不把其类别编码误作金额。")
add("2011","fn053","commercial_pension_annual_premium_amount","商业养老保险年度缴费金额",
    "annual premium amount respondent reports paying toward commercial pension insurance",
    unit="Yuan/year",value_source=commercial_2011_source,
    caveat="仅商业养老保险FN052=1（按年缴费）路径适用；FN052=2一次性缴费者跳过FN053/FN054并转FN055。不得将其与一次性总保费fn055合并为同一尺度。")
add("2011","fn054","commercial_pension_required_contribution_years","商业养老保险所需缴费年限",
    "number of years respondent needs to pay commercial pension premiums",
    unit="years",value_source=commercial_2011_source,
    caveat="仅商业养老保险FN052=1（按年缴费）路径适用；一次性缴费者跳过。与已缴年数、当前参保时长、预期领取等待年数分开；有效范围及特殊值须在许可个体数据中核验。")
add("2011","fn041","pension_current_plan_duration_years","当前/既往养老金计划累计参保年限",
    "total years included in the named supplementary pension plan, including years with other employers if the same plan continued",
    unit="years",value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="仅FN039=1（企业补充养老金）路由。问卷明确跨雇主但同一计划的年数计入；不等于当前雇主任职年限或距领取年数。应核验退出/中断计划者的适用性及有效特殊码。")
add("2011","fn061_1","pension_annual_contribution_amount","选定养老金计划年度个人缴费金额",
    "respondent-reported annual personal contribution to the selected rural/resident pension program",
    unit="Yuan/year",value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    caveat="仅2011 FN039=3/4/5所选农村/城乡居民/城镇居民养老金计划路径；政府与集体补贴分别在fn061_2/_3，不要相加或混作个人缴费。金额适用计划路由，不等同于商业养老金fn053。")

# Land-requisition history and the expected-benefit response-format parent.
for wave in ("2013", "2015"):
    source=timing_source[wave]
    add(wave,"fn079_w2_1","land_requisition_exposure_status","土地是否曾被征收",
        "whether respondent's land has ever been requisitioned",values="1=Yes; 2=No",
        value_source=source,
        caveat="2013/2015征地养老金模块的前置筛选问题；仅用于刻画土地征收经历，不等同于参加征地养老保险。FN079_W2_2仅对Yes继续询问征收年份。")
    add(wave,"fn079_w2_2","land_requisition_year","土地被征收年份",
        "calendar year in which respondent's land was requisitioned",unit="calendar year",
        value_source=source,
        caveat="仅在FN079_W2_1=Yes后询问；年份是回顾性土地征收时点，不作为确切日期或当前居住地。原始编码范围和特殊码须在许可个体数据中核验。")
    add(wave,"fn079_w2_9","pension_expected_benefit_amount_form_selector_land_requisition","征地养老金预期待遇金额形式选择器",
        "response format for expected land-requisition pension benefit amount",
        values="1=Yuan per month; 2=Yuan lump sum",value_source=source,
        status="measurement metadata; C only",
        caveat="FN079_W2_9父项仅选择月金额或一次性金额形式，数值在fn079_w2_9_1/_2中；不作为待遇金额E或二元领取状态。预期金额只适用于问卷规定的未领取待遇路径。")

# Actual land-requisition pension receipt date and current monthly benefit.
for wave in ("2013", "2015", "2018"):
    source=timing_source[wave]
    for suffix,unit in (("1","calendar year"),("2","month")):
        add(wave,f"fn079_w2_10_{suffix}","pension_land_requisition_benefit_start_date_components","征地养老金实际开始领取年月组成字段",
            "year/month components for when respondent began receiving land-requisition pension benefits",
            unit=unit,value_source=source,
            caveat="仅FN079_W2_3=2（当前正在领取征地养老金）路径询问。月份0表示不记得；2018问卷对未知金额/月份的特殊码需按该波代码本核对。保留年/月组件，不把未问者记为未领取或零。")
    add(wave,"fn079_w2_11","pension_monthly_benefit_amount","征地养老金当前月领取金额",
        "current monthly amount received from land-requisition pension benefits",
        unit="CNY/month",value_source=source,
        caveat="仅FN079_W2_3=2（当前正在领取）路径询问。2013/2015题干明确每月金额；2018也明确按月，-1表示未知并追问区间，0元也触发区间追问。须保留原值/区间信息并按波次代码本处理特殊值，不能把未知或结构缺失转成0。")

# Commercial-pension contribution-start date components in Waves 2 and 3.
# FN043=2 (already receiving benefits) skips this block; do not read blanks as No.
for wave, endyear, src in (("2013", "2013", "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"),
                           ("2015", "2015", "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt")):
    for suffix,unit in (("1","calendar year"),("2","month")):
        add(wave,f"fn046_w2_{suffix}","commercial_pension_contribution_start_date_components","商业养老金开始缴费时间组成字段",
            "year/month component for when respondent started paying toward commercial pension insurance",
            unit=unit,value_source=src,
            caveat=f"仅商业养老金问卷中FN043_W2=1（有该保险但尚未领取待遇）路径询问；FN043=2已领取待遇者跳过。2013/2015分别保留原始年范围至{endyear}；月份0按访员说明表示不记得，不能当作1月。不同于补充养老金实际待遇开始领取年月FN041或其他计划参保起始时间；年月需在分析时合成并处理边界/特殊码。")

# Earliest plan-specific age at which the respondent could leave the employer and
# receive benefits is an entitlement-rule measure, distinct from actual retirement/claim age.
for wave, source in (("2013", "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"),
                     ("2015", "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"),
                     ("2018", "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt")):
    add(wave,"fn038_w2","pension_earliest_employer_exit_age_for_benefits","养老金计划最早可离职并领取待遇年龄",
        "earliest age reported at which respondent could leave the named employer and receive the pension benefit",
        unit="years of age",value_source=source,
        caveat="这是具名/特定养老金计划的自报领取资格年龄，不是实际离职年龄、法定退休年龄或实际开始领取年龄；保留波次与计划路由，原始数值45–120及可能特殊码须在许可数据字典中核实。")

# Whether a pension plan requires personal/employer contributions is a meaningful plan-level
# candidate, but the 2013/2018 questionnaire-to-codebook response definitions conflict.
add("2013","fn012_w2_1_","pension_plan_contribution_requirement_personal_or_work_unit","养老金计划是否要求个人或单位缴费",
    "whether the government/institution pension plan requires a personal or work-unit contribution",
    values="1=Yes; 2=No",
    value_source="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    status="DO NOT ANALYZE; questionnaire asks whether respondent pays, while codebook label refers to respondent or work unit",
    caveat="2013问卷FN012_W2仅写个人是否需要缴费，代码本fn012_w2_1_标签却写个人或工作单位是否缴费。保留候选概念与原始码用于检索，禁止分析，直到发布版题意/变量映射得到确认。")
add("2013","fn012_w2_2_","pension_plan_contribution_requirement_personal_or_work_unit","养老金计划是否要求个人或单位缴费",
    "whether the firm pension plan requires a personal or work-unit contribution",
    values="1=Yes; 2=No",
    value_source="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    status="DO NOT ANALYZE; questionnaire asks whether respondent pays, while codebook label refers to respondent or work unit",
    caveat="2013问卷FN012_W2仅写个人是否需要缴费，代码本fn012_w2_2_标签却写个人或工作单位是否缴费。保留候选概念与原始码用于检索，禁止分析，直到发布版题意/变量映射得到确认。")
add("2015","fn012_w2_1_","pension_plan_contribution_requirement_personal_or_work_unit","养老金计划是否要求个人或单位缴费",
    "whether the government/institution pension plan requires a personal or work-unit contribution",
    values="1=Yes; 2=No",
    value_source="sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    caveat="只在对应政府/机关事业单位养老金计划路径询问；计划槽位、特殊缺失和实际缴费者仍须分开。该题询问是否需要个人或单位缴费，不等于个人当前缴费金额。")
add("2015","fn012_w2_2_","pension_plan_contribution_requirement_personal_or_work_unit","养老金计划是否要求个人或单位缴费",
    "whether the firm pension plan requires a personal or work-unit contribution",
    values="1=Yes; 2=No",
    value_source="sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    caveat="只在对应企业养老金计划路径询问；与政府/事业单位计划及个人实际缴费金额分开解释。")
# Keep 2018's four original loop slots and flag the codebook's missing No category.
mask=(base.wave.eq("2018") & base.code.str.lower().str.match(r"fn012_w2_[1-4]_"))
base.loc[mask,"concept_id"]="pension_plan_contribution_requirement_personal_or_work_unit"
base.loc[mask,"concept_label"]="养老金计划是否要求个人或单位缴费"
base.loc[mask,"construct"]="whether respondent or employer is required to contribute to the named pension plan"
base.loc[mask,"mapping_status"]="DO NOT ANALYZE; questionnaire includes No but codebook lists only Yes"
base.loc[mask,"value_labels"]="1=Yes (codebook lists only Yes; questionnaire also specifies 2=No)"
base.loc[mask,"value_label_status"]="questionnaire/codebook conflict"
base.loc[mask,"value_label_source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
base.loc[mask,"caveat"]="2018问卷FN012_W2提供1=Yes、2=No，并规定Yes才进入缴费金额题；代码本四个槽位目前仅列1=Yes。保留原计划槽位及路由，不能把未列出的2、缺失或未问推断为No；发布版类别频数/存储码需核实后才可分析。"

# Link 2011 unfolding-bracket interval bounds to the existing amount concepts.
# These are only asked after refusal/no recall; retain lower/upper-bound semantics and route.
for code in ("fn005_a", "fn005_b", "fn008_a", "fn008_b", "fn014_a", "fn014_b", "fn019_a", "fn019_b", "fn023_a", "fn023_b"):
    bound = "lower bound" if code.endswith("_a") else "upper bound"
    add("2011", code, "pension_monthly_benefit_amount", "养老金月待遇金额",
        f"unfolding-bracket {bound} for a plan-specific current monthly pension amount",
        unit="CNY/month interval bound; not a point estimate",
        value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        caveat="仅在对应养老金来源的当前月待遇题拒答或不记得时按问卷追问；与计划/来源路由绑定。该字段是金额区间端点，不可当作精确月金额、跨计划独立暴露或普通缺失填补值。")
for code in ("fn037_a", "fn037_b"):
    bound = "lower bound" if code.endswith("_a") else "upper bound"
    add("2011", code, "pension_expected_monthly_benefit_amount_untyped_plan", "未指定计划的预期月养老金待遇",
        f"unfolding-bracket {bound} for expected monthly pension benefit amount",
        unit="CNY/month interval bound; not a point estimate",
        value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        caveat="FN037只在FN034=Yes或FN035选择退休时一次性补缴路径后，用于补充FN036预期待遇题；FN036另有C类金额/工资比例单位选择器。保留区间端点，不把它当精确月金额或合并百分比口径。")

# Preserve questionnaire-confirmed combined-contribution brackets in 2013/2015.
# Codebook declares the bounds as strings, so link them but prohibit numeric conversion
# until the authorized release dictionary confirms the stored representation.
for wave, codes in (("2013", ("fn035_w2_bracketbracket_min", "fn035_w2_bracketbracket_max")),
                    ("2015", ("fn035_w2_bracket_min", "fn035_w2_bracket_max"))):
    for code in codes:
        bound = "lower" if "min" in code.lower() else "upper"
        add(wave, code, "pension_combined_contribution_amount_or_share", "养老金月度缴费总额/工资比例题组",
            f"questionnaire bracket {bound} for the combined monthly contribution amount",
            unit="CNY/month bracket endpoint; Codebook stores endpoint as string",
            value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
            status="candidate source link; official questionnaire confirms bracket for the amount item; Codebook marks bound as string; numerical use pending release dictionary",
            caveat="FN035_W2先询问个人与单位合计月缴费，再询问个人缴费工资比例；此区间只对应合计金额项。官方Codebook将min/max端点标为字符串，保留原类型；获批发布字典确认存储前不得强制转数值、估算金额或与比例字段合并。")

# 2011 employer-linked basic pension start date matches the 2013/2015 FN011 work-unit route.
for code, unit in (("fn029_1", "calendar year"), ("fn029_2", "calendar month")):
    add("2011", code, "pension_employer_plan_participation_start_date", "经工作单位参加企业基本养老保险的起始年月",
        "start-date component for participation in basic enterprise pension through the selected current/last/retirement-processing work unit",
        unit=unit,
        value_source="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        caveat="仅在FN024=2（参加企业基本养老保险），并在FN025选定提供这份养老保险的当前、上一份或办理退休单位后询问；FN029_2=0可表示不记得月份。该路由与2013/2015 FN011 work-unit date题意一致，年份范围依波次保留，不自动拼接或填补日期。")

# Required years of contribution for the named other-pension program, distinct from years already enrolled.
for wave in ("2013", "2015", "2018"):
    add(wave, "fn091_w2", "pension_required_contribution_years", "养老金计划所需缴费年限",
        "number of years the respondent needs to contribute to the selected other pension program",
        unit="years",
        value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        status="official questionnaire/codebook item; candidate mapping; payment-route and range validation required",
        caveat="只适用于FN087_w2=Yes、该其他养老计划需要缴费的受访者；与当前已参保年限、参保起始时间和预期领取时间分别建项。问卷对超过法定上限设软校验提示，不等同于数据清洗规则；Codebook极值不得单独据以推断有效/无效。保留波次原值和路由，特殊缺失/值域需对应发行版数据字典确认。")

# Add the 2018 other-pension participation/receipt status to the existing 2013/2015 concept.
add("2018", "fn083_w2", "pension_current_participation_or_receipt_unspecified_scheme", "是否正在参加或领取其他养老保险",
    "whether respondent currently participates in or receives benefits from an unspecified other pension program",
    values="1=Yes, currently participating/not yet receiving; 2=Yes, currently receiving; 3=No",
    value_source="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
    caveat="2018问卷FN083_W2询问前述计划之外的其他养老金；当前参保/领取状态受前序已列养老计划的条件路由影响。FN084_W4仅对该计划进一步核实是否正在领取，不能把fn083_w2=1和fn084_w4混成同一个状态。2018 Codebook列Yes Participate/Yes Receive/No但未为No列数值码，目录依问卷记为3；跨波保留原分类与资格路径。")

# Other-pension participation start date: retain as a separate construct from employer/basic plans.
for wave, max_year in (("2013", "2013"), ("2015", "2015")):
    for code, unit in (("fn086_w2_1", "calendar year"), ("fn086_w2_2", "calendar month")):
        add(wave, code, "other_pension_program_participation_start_date", "其他养老保险计划参保起始年月",
            "start-date component for participation in the other pension program named by the respondent",
            unit=unit,
            value_source=f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
            status="candidate source link; questionnaire route reviewed; Codebook observed range/special-value reconciliation pending",
            caveat=f"仅适用于FN083_w2=1（正在参加但尚未领取其他养老保险待遇）；FN083_w2=2（正在领取）跳过起始日期，FN083_w2=3（未参加）跳至后续题。FN084计划名称可能对应不同方案，单独保留此其他计划概念，不并入企业基本/补充养老金。问卷列年份为1990至{max_year}，而Codebook观测摘要最小年份早于1990（2013:1985；2015:1984），月份摘要还出现非月份特殊值；保留原始字段和取值，待对应发行版字典核实前不得据问卷范围截断、将特殊值当日期或用于分析。FN086_2的0按问卷可表示不记得月份。")

extra=pd.DataFrame(rows).drop_duplicates(["wave","code","concept_id"])
# Parent amount-format selectors are curated in the catalog-role and protocol
# tables only; they must not enter the E/P pension concept crosswalk.
extra=extra.loc[~(extra.code.str.lower().eq("fn079_w2_9") & extra.mapping_status.eq("measurement metadata; C only"))].copy()
base_concepts_before=set(base.concept_id)
base=pd.concat([base,extra],ignore_index=True).drop_duplicates(["wave","code","concept_id"],keep="last")
# Ensure unit is available to the shared Atlas mapping builder.
if "unit" not in base.columns: base["unit"]=""
base.to_csv(base_path,index=False,encoding="utf-8-sig")
# Curated value labels for response-coded additions; no counts or frequencies are included.
label_rows=extra[extra.value_labels.fillna("").ne("")][["wave","code","concept_id","source_label","value_labels","value_label_status","value_label_source"]]
label_path=AUDIT/"pension_codebook_value_labels_v1.csv"
if label_path.exists():
    labels=pd.read_csv(label_path,dtype=str,encoding="utf-8-sig").fillna("")
    labels=pd.concat([labels,label_rows],ignore_index=True).drop_duplicates(["wave","code","concept_id"],keep="last")
    conflict_mask=(labels.wave.eq("2018") & labels.code.str.lower().str.match(r"fn012_w2_[1-4]_"))
    labels.loc[conflict_mask,"value_labels"]="1=Yes (codebook lists only Yes; questionnaire also specifies 2=No)"
    labels.loc[conflict_mask,"value_label_status"]="questionnaire/codebook conflict"
    labels.loc[conflict_mask,"value_label_source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
    labels.to_csv(label_path,index=False,encoding="utf-8-sig")
summary=(base.groupby(["construct","concept_id","concept_label"],dropna=False)
 .agg(waves=("wave",lambda x:",".join(sorted(set(x)))),source_fields=("code","size"),source_codes=("code",lambda x:";".join(sorted(set(x)))))
 .reset_index())
summary.to_csv(AUDIT/"pension_exposure_concept_summary_v1.csv",index=False,encoding="utf-8-sig")
print(f"pension plan/supplementary audit appended {len(extra)} mappings; net new concepts={len(set(base.concept_id)-base_concepts_before)}; total mappings={len(base)}; total concepts={base.concept_id.nunique()}")
