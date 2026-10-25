"""Create conservative pension-exposure concept candidates from official metadata."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

SCHEMES = [
    ("government_institution", r"government|institution|staffing|public institution"),
    ("enterprise_employee", r"firm|enterprise|company|employer"),
    ("supplementary", r"supplement"),
    ("commercial", r"commercial"),
    ("life_insurance", r"life insurance"),
    ("new_rural_social", r"new rural|nrsp"),
    ("rural", r"rural pension"),
    ("urban_residents", r"urban residents"),
    ("residents", r"residents' pension|resident pension"),
    ("land_requisition", r"land requisition"),
    ("oldest_old_subsidy", r"oldest old"),
]
SCHEME_ZH = {
    "government_institution": "政府/机关事业单位", "enterprise_employee": "企业职工",
    "supplementary": "补充养老金", "commercial": "商业养老金保险",
    "life_insurance": "人寿保险", "new_rural_social": "新型农村社会养老保险",
    "rural": "农村养老金", "urban_residents": "城镇居民养老金",
    "residents": "居民养老金", "land_requisition": "征地养老保险",
    "oldest_old_subsidy": "高龄老人养老金补贴", "unspecified_scheme": "未区分计划",
}

def scheme_of(label: str) -> str:
    for slug, pattern in SCHEMES:
        if re.search(pattern, label, re.I):
            return slug
    return "unspecified_scheme"

rows = []
for rec in raw.itertuples(index=False):
    wave, code, label, module = str(rec.wave), str(rec.variable).lower(), str(rec.variable_label), str(rec.module)
    if wave not in {"2011", "2013", "2015", "2018"} or not code.startswith("fn"):
        continue
    # These exact 2011/2013 items are added below from the correct wave-specific
    # questionnaire and Codebook evidence, rather than inferred by label alone.
    if (wave == "2011" and code in {"fn015", "fn016", "fn036_1", "fn036_2", "fn065", "fn066"}) or (wave == "2013" and code == "fn063_w2_2_"):
        continue
    # FN056_W2 is reused for life-insurance questions after the pension
    # subsections. Its suffix fields are not pension contribution/receipt
    # variables; keep the reviewed insurance family in its dedicated crosswalk.
    # Preserve the distinct pension-benefit amount brackets with this code.
    if (code.startswith("fn056_w2_")
            and not code.startswith("fn056_w2_bracket")
            and code != "fn056_w2_max"):
        continue
    if code == "fn073_w4":
        continue
    if wave == "2018" and code in {"fn072_w3_1", "fn072_w3_1_min", "fn072_w3_1_max"}:
        continue
    # In the 2018 commercial-pension section FN051_W4 is an age-vs-years
    # response-format selector, not a binary future-receipt status. Its
    # questionnaire wording overrides the ambiguous codebook label; its C
    # classification is maintained in the role-override crosswalk.
    if wave == "2018" and code in {"fn051_w4", "fn076_w4_a", "fn093_w2"}:
        continue
    # 2018 FN038_W2 shares its short label with a generic receipt-age concept,
    # but the questionnaire asks earliest age to leave the named employer and
    # receive that plan's benefits. Its precise reviewed concept is added by
    # build_pension_supplementary_crosswalk.py.
    if wave == "2018" and code == "fn038_w2":
        continue
    # Expected pension timing selectors and their unit-specific numeric children
    # are mapped from the questionnaire-reviewed supplementary crosswalk.
    if ((wave == "2013" and code in {"fn078_w2", "fn078_w2_1", "fn078_w2_2"})
            or (wave in {"2013", "2015", "2018"}
                and re.fullmatch(r"fn079_w2_8(?:_[12])?", code))
            or (wave in {"2013", "2015"}
                and code in {"fn079_w2_1", "fn079_w2_2", "fn079_w2_9"})):
        continue
    if wave in {"2013", "2015"} and code.startswith("fn065_w2_"):
        continue
    # FN021_W2 is a response-format selector (monthly Yuan versus final-pay
    # percentage); the numeric responses are separate child fields. Preserve
    # unit-specific concepts in the questionnaire-reviewed supplemental map.
    if wave in {"2013", "2015"} and code.startswith("fn021_w2"):
        continue
    # Land-requisition benefits have a plan-specific start date and current
    # monthly amount; do not mix their generic questionnaire labels into the
    # pooled pension start-date/amount constructs.
    if wave in {"2013", "2015", "2018"} and re.fullmatch(r"fn079_w2_(?:10_[12]|11)", code):
        continue
    if wave == "2018" and code.startswith("fn021_w2_"):
        continue
    # FN036_W2 parent is a response-format selector; the monetary/percentage
    # values are held in three distinct child fields and the parent is C metadata.
    if (code == "fn036_w2"
            or (wave in {"2013", "2015"} and code in {"fn066_w2_1_", "fn066_w2_2_", "fn066_w2_3_"})
            or (wave == "2015" and code in {"fn075_w3_1_1_", "fn075_w3_1_2_", "fn075_w3_1_3_", "fn075_w3_2_1_", "fn075_w3_2_2_", "fn075_w3_2_3_"})
            or (wave == "2015" and code in {"fn072_w3_1_1_", "fn072_w3_1_2_", "fn072_w3_1_3_", "fn072_w3_2_1_", "fn072_w3_2_2_", "fn072_w3_2_3_"})):
        continue
    if not re.search(r"pension|contribut|benefit|subsidy", module + " " + label, re.I):
        continue
    kind = None
    scheme = ""
    mapping_status = "candidate from official variable metadata; questionnaire wording/value codes and route review pending"
    caveat = "Pension variables are plan-, wave-, and route-specific. Do not treat preloads, bracket endpoints, family-level amounts, or different receipt/contribution questions as interchangeable measures."
    extra = {}
    # Questionnaire-reviewed commercial-pension fields. The short/blank codebook
    # labels in these waves are not sufficient to infer construct or unit, so
    # map by exact field code and preserve the routed plan-specific meaning.
    if re.fullmatch(r"fn075_w3_([12])_([12])_([123])_", code) and wave == "2015":
        match = re.fullmatch(r"fn075_w3_([12])_([12])_([123])_", code)
        amount_kind, unit_code, scheme_code = match.groups()
        scheme_id, scheme_zh = {"1": ("new_rural", "新农保"), "2": ("residents", "居民"), "3": ("urban_residents", "城镇居民")}[scheme_code]
        kind_name = "total" if amount_kind == "1" else "personal"
        concept = f"pension_2015_{scheme_id}_{kind_name}_supplementary_repayment_amount"
        display = f"2015年{scheme_zh}养老保险{'总' if kind_name == 'total' else '个人'}补缴金额"
        kind = f"{kind_name} supplementary repayment amount for {scheme_id} pension"
        unit = "Yuan" if unit_code == "1" else "10,000 Yuan"
        mapping_status = "2015 questionnaire/codebook identifies plan-specific repayment amount, payer scope, and currency unit; candidate only"
        caveat += " Asked within the conditional 2015 FN067–FN075 pension-plan receipt and repayment section. Keep total plan repayment distinct from the personal portion. For alternative unit-coded fields, normalize 10,000 Yuan responses to Yuan before any pooled calculation; do not add total and personal amounts together. Skipped or unit-alternative fields are not zero."
        extra = {"unit": unit, "value_label_status": "official codebook plan, amount scope, and currency unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn066_w2_[12]_[123]_", code) and wave in {"2013", "2015"}:
        tokens = code.split("_")
        form_code, scheme_code = tokens[2], tokens[3]
        form = "monthly" if form_code == "1" else "lump_sum"
        scheme = {"1": ("rural" if wave == "2013" else "new_rural", "农村" if wave == "2013" else "新农保"),
                  "2": ("residents", "居民"), "3": ("urban_residents", "城镇居民")}[scheme_code]
        scheme_id, scheme_zh = scheme
        concept = f"pension_{scheme_id}_expected_{form}_benefit"
        display = f"{scheme_zh}养老保险预期{'月待遇' if form == 'monthly' else '一次性待遇金额'}"
        kind = f"expected {form} benefit for {scheme_id} pension"
        mapping_status = "2013/2015 codebook identifies plan-specific amount field and unit; questionnaire route reviewed; candidate only"
        caveat += " Conditional on the selected social-pension plan and its contribution/transfer route; preserve plan and payment form. Monthly and lump-sum amounts are separate; do not annualize or impute the nonselected form as zero. The codebook labels the 2013 scheme as Rural Pension and the 2015 counterpart as New Rural Pension, so these remain distinct concepts pending an explicit harmonization decision."
        extra = {"unit": "Yuan/month" if form == "monthly" else "Yuan (lump sum)",
                 "value_label_status": "official codebook field label/unit and plan-specific route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn035_w2_2" and wave in {"2013", "2015"}:
        kind, concept, display = ("employee share of combined monthly supplementary-pension contribution",
                                  "pension_firm_supplementary_employee_share_of_combined_monthly_contribution",
                                  "企业补充养老金个人承担月缴费比例")
        mapping_status = "2013/2015 questionnaire and codebook verified; percent denominator is combined employee-plus-employer monthly contribution; candidate only"
        caveat += " Asked in the firm supplementary-pension follow-up, among respondents not already receiving the plan benefit. This is the respondent's percentage share of the combined contribution, not percentage of salary and not an amount. Preserve the plan route and denominator."
        extra = {"unit": "percent of combined monthly contribution",
                 "value_label_status": "official questionnaire range 0–100 and codebook label reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code in {"fn036_w2_1", "fn036_w2_2", "fn036_w2_3"} and wave in {"2013", "2015"}:
        specs = {
            "fn036_w2_1": ("monthly", "pension_firm_supplementary_expected_monthly_benefit", "企业补充养老金预期月待遇金额", "Yuan/month"),
            "fn036_w2_2": ("percentage", "pension_firm_supplementary_expected_monthly_benefit_percentage", "企业补充养老金预期月待遇比例", "percent/month as coded; denominator unspecified"),
            "fn036_w2_3": ("lump_sum", "pension_firm_supplementary_expected_lump_sum_benefit", "企业补充养老金预期一次性待遇金额", "Yuan (lump sum)"),
        }
        form, concept, display, unit = specs[code]
        kind = f"firm supplementary pension expected {form} benefit"
        mapping_status = "2013/2015 questionnaire and codebook verified; DB-plan route and response form reviewed; candidate only"
        caveat += " Conditional on participation in the firm supplementary pension, not currently receiving benefits, and the defined-benefit plan route (FN032_W2=1). Monthly Yuan, percentage, and lump-sum response forms are separate; the percentage denominator is not specified and must not be inferred."
        extra = {"unit": unit, "value_label_status": "official questionnaire/codebook field unit and route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn027_w2_[12]", code):
        component = "year" if code.endswith("_1") else "month"
        kind, concept, display = ("basic pension participation start-date component",
                                  "pension_basic_plan_participation_start_date",
                                  "通过所选工作单位参加企业职工基本养老保险的开始年月")
        mapping_status = "official questionnaire and codebook reviewed; selected work-unit route verified; candidate only"
        caveat += " Asked in the prior basic-pension participation/work-unit follow-up; retain year and month separately. Questionnaire says month 0 means not remembered; do not treat it as January. This is participation start timing, not current contribution amount or benefit receipt date."
        extra = {"unit": "calendar year" if component == "year" else "calendar month; 0=not remembered",
                 "value_label_status": "official questionnaire date range and month-0 convention reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn028_w2_[12]", code) and wave in {"2013", "2015"}:
        component = "year" if code.endswith("_1") else "month"
        kind, concept, display = ("conflicted basic pension participation date component",
                                  "pension_basic_plan_fn028_timing_questionnaire_codebook_conflicted",
                                  "\u4f01\u4e1a\u804c\u5de5\u57fa\u672c\u517b\u8001\u4fdd\u9669FN028\u5e74\u6708\uff08\u95ee\u5377/\u4ee3\u7801\u672c\u9898\u610f\u51b2\u7a81\uff09")
        mapping_status = f"DO NOT ANALYZE: {wave} questionnaire says start participating; {wave} codebook says stop participating"
        caveat += f" {wave} questionnaire wording says start participating, while its Codebook title says stop participating. Keep this wave-code as a locked audit candidate; do not assign start/stop meaning, derive duration, harmonize with FN027 or another wave, or analyze until CHARLS resolves the discrepancy. The questionnaire's month 0 means not remembered, but does not resolve the event-identity conflict."
        extra = {"unit": "calendar year" if component == "year" else "calendar month; 0=not remembered per questionnaire; event identity unresolved",
                 "value_label_status": "questionnaire/codebook wording conflict; unresolved",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif wave == "2013" and code in {"fn072_w2_1", "fn072_w2_2", "fn072_w2_3", "fn072_w2_4", "fn072_w2_5"}:
        fn072_specs = {
            "fn072_w2_1": ("annual", "pension_new_rural_annual_contribution_amount", "新农保年度缴费金额", "Yuan/year", "FN072 contribution form=annual payment"),
            "fn072_w2_2": ("lump_sum", "pension_new_rural_lump_sum_contribution_amount", "新农保一次性缴费金额", "Yuan (lump sum)", "FN072 contribution form=lump-sum payment"),
            "fn072_w2_3": ("lump_sum_annual_equivalent", "pension_new_rural_lump_sum_annual_equivalent", "新农保一次性缴费对应年缴金额", "Yuan/year", "FN072 contribution form=lump-sum payment; reported annual equivalent"),
            "fn072_w2_4": ("retroactive_lump_sum", "pension_new_rural_retroactive_lump_sum_contribution", "新农保不足15年路径一次性补缴金额", "Yuan (lump sum)", "FN072 contribution form=less than 15 years before benefit age"),
            "fn072_w2_5": ("post_retroactive_annual", "pension_new_rural_post_retroactive_annual_contribution", "新农保不足15年路径后续年度缴费金额", "Yuan/year", "FN072 contribution form=less than 15 years before benefit age"),
        }
        subkind, concept, display, unit, route = fn072_specs[code]
        kind = f"new-rural pension {subkind} contribution amount"
        mapping_status = "2013 questionnaire and codebook verified; exact contribution-form route and unit reviewed; candidate only"
        caveat += f" {route}. The four FN072 alternatives are mutually routed measurement forms and must not be summed or treated as comparable without a prespecified harmonization; category 4 (no personal payment because over 60 and covered through children) skips these amounts. Do not infer zero for skipped fields."
        extra = {"unit": unit, "value_label_status": "official questionnaire route and unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"}
    elif code in {"fn079_w2_6_1", "fn079_w2_6_2"} and wave in {"2013", "2015", "2018"}:
        period = "monthly" if code.endswith("_1") else "annual"
        period_zh = "月" if period == "monthly" else "年度"
        kind, concept, display = (f"land-expropriation pension {period} contribution amount",
                                  f"pension_land_expropriation_{period}_contribution_amount",
                                  f"征地养老保险{period_zh}缴费金额")
        mapping_status = ("2013/2015 questionnaire route and amount period reviewed; candidate only" if wave in {"2013", "2015"}
                          else "2018 codebook amount field and period unit reviewed; exact questionnaire route not independently confirmed; candidate only")
        caveat += " Conditional on reported participation/receipt in the land-expropriation pension and the self-payment route (FN079_W2_3=1/2 and FN079_W2_4=1); preserve monthly versus annual units and do not infer zero for skipped fields."
        extra = {"unit": "Yuan/month" if period == "monthly" else "Yuan/year",
                 "value_label_status": "official questionnaire/codebook wording, route, and period unit reviewed; frequencies omitted",
                 "value_label_source": (f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt" if wave in {"2013", "2015"}
                                        else "sources_official/CHARLS_2018_Codebook_extracted.txt")}
    elif code in {"fn079_w2_7_1", "fn079_w2_7_2", "fn079_w2_7_3", "fn079_w2_7_4"} and wave in {"2013", "2015", "2018"}:
        payer = "government" if code.endswith(("_1", "_2")) else "collective"
        period = "monthly" if code.endswith(("_1", "_3")) else "annual"
        payer_zh = "政府" if payer == "government" else "集体"
        period_zh = "月" if period == "monthly" else "年度"
        kind, concept, display = (f"land-expropriation pension {period} subsidy from {payer}",
                                  f"pension_land_expropriation_{payer}_{period}_subsidy_amount",
                                  f"征地养老保险{payer_zh}{period_zh}补贴金额")
        mapping_status = "2013/2015 questionnaire route, subsidy payer, and period reviewed; candidate only"
        caveat += " Government and collective subsidies are distinct reporters; monthly and annual values must remain separate. Conditional on the land-expropriation pension route; do not infer zero from skipped fields."
        extra = {"unit": "Yuan/month" if period == "monthly" else "Yuan/year",
                 "value_label_status": "official questionnaire/codebook wording, payer, and period unit reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code in {"fn079_w2_9_1", "fn079_w2_9_2"} and wave in {"2013", "2015", "2018"}:
        form = "monthly" if code.endswith("_1") else "lump_sum"
        kind, concept, display = (("expected monthly land-expropriation pension benefit", "pension_land_expropriation_expected_monthly_benefit", "预期征地养老保险月待遇")
                                  if form == "monthly" else
                                  ("expected lump-sum land-expropriation pension benefit", "pension_land_expropriation_expected_lump_sum_benefit", "预期征地养老保险一次性待遇金额"))
        mapping_status = ("2013/2015 questionnaire route and payment-form field reviewed; candidate only" if wave in {"2013", "2015"}
                          else "2018 codebook payment-form field reviewed; exact questionnaire route not independently confirmed; candidate only")
        caveat += " Expected benefit amount, not current receipt. Payment form is explicit in the child field; retain monthly and lump-sum amounts separately and do not annualize or infer zero for the nonselected form."
        extra = {"unit": "Yuan/month" if form == "monthly" else "Yuan (lump sum)",
                 "value_label_status": "official questionnaire/codebook wording, route, and unit reviewed; frequencies omitted",
                 "value_label_source": (f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt" if wave in {"2013", "2015"}
                                        else "sources_official/CHARLS_2018_Codebook_extracted.txt")}
    elif code == "fn094_w2_1" and wave in {"2013", "2015", "2018"}:
        kind, concept, display = "expected monthly pension benefit, specified pension-plan route", "pension_expected_monthly_benefit_other_plan", "其他养老金计划预期月待遇"
        mapping_status = "official codebook identifies monthly amount; questionnaire field code reviewed; candidate only"
        caveat += " Conditional on the plan/status route preceding FN094; represents expected monthly amount, not current receipt. The questionnaire prints the same child code for both payment forms in 2013/2015; use this field as monthly only per the wave-specific codebook, and retain that source discrepancy in the audit record."
        extra = {"unit": "Yuan/month", "value_label_status": "codebook field label and unit reviewed; questionnaire code duplication noted; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn094_w2_2" and wave == "2018":
        kind, concept, display = "expected lump-sum pension benefit, specified pension-plan route", "pension_expected_lump_sum_benefit_other_plan", "其他养老金计划预期一次性待遇金额"
        mapping_status = "2018 codebook identifies lump-sum field and unit; candidate only"
        caveat += " Conditional on the plan/status route preceding FN094; expected one-time total, not monthly or annual benefit. Preserve the distinct lump-sum response."
        extra = {"unit": "Yuan (lump sum)", "value_label_status": "official codebook field label and unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn094_w2_2" and wave in {"2013", "2015"}:
        kind, concept, display = "conflicted expected pension lump-sum benefit field", "pension_fn094_lump_sum_code_conflict", "其他养老金计划预期一次性待遇（问卷代码冲突）"
        mapping_status = "DO NOT ANALYZE: codebook labels _2 as lump sum, but questionnaire duplicates _1 for both payment forms"
        caveat += " Retained as an audit/search item only. Do not analyze or harmonize until the questionnaire/codebook field-code discrepancy is resolved."
        extra = {"unit": "Yuan (lump sum per codebook; unresolved)", "value_label_status": "questionnaire/codebook child-code conflict; unresolved",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif wave == "2011" and code in {"fn011_1", "fn011_2", "fn011_3", "fn011_4", "fn011_5", "fn011_6"}:
        fn011_specs = {
            "fn011_1": ("pension_annual_contribution_amount", "自报年度养老金缴费金额", "Yuan/year", "annual contribution"),
            "fn011_2": ("pension_subsidy_annual_amount", "自报年度养老金补贴金额", "Yuan/year", "annual subsidy from the collective"),
            "fn011_3": ("pension_subsidy_annual_amount", "自报年度养老金补贴金额", "Yuan/year", "annual subsidy from the government"),
            "fn011_4": ("pension_lump_sum_contribution_amount", "自报一次性养老金缴费金额", "Yuan (lump sum)", "lump-sum contribution"),
            "fn011_5": ("pension_subsidy_lump_sum_amount", "自报一次性养老金补贴金额", "Yuan (lump sum)", "lump-sum subsidy from the collective"),
            "fn011_6": ("pension_subsidy_lump_sum_amount", "自报一次性养老金补贴金额", "Yuan (lump sum)", "lump-sum subsidy from the government"),
        }
        concept, display, unit, kind = fn011_specs[code]
        payer = "collective" if code in {"fn011_2", "fn011_5"} else "government" if code in {"fn011_3", "fn011_6"} else "respondent contribution"
        mapping_status = "2011 baseline questionnaire and Codebook item, route, amount period, and unit reviewed; candidate only"
        caveat += " Asked only in the 2011 selected rural/residents/urban-residents pension route (FN002=3/4/5) after FN009=Yes. Preserve the FN011 Codebook form selector (1=annual, 2=lump sum) and pair it with the corresponding amount component; the questionnaire displays annual and lump-sum blanks together with 'or'. Keep subsidy payer explicit in the source field. Do not interpret skipped or nonselected-form values as zero; participant-level special missing codes and selector/component consistency require authorized-data QA."
        extra = {"unit": unit,
                 "value_label_status": "official 2011 questionnaire/Codebook field identity, route and amount period reviewed; special missing codes not reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code in {"fn061_2", "fn061_3"}:
        payer = "collective" if code.endswith("_2") else "government"
        payer_zh = "集体" if payer == "collective" else "政府"
        kind, concept, display = (f"annual pension subsidy from {payer}",
                                  f"pension_annual_subsidy_{payer}_amount_named_program",
                                  f"选定养老金计划的{payer_zh}年度补贴金额")
        mapping_status = "2011 baseline questionnaire and codebook reviewed; annual subsidy payer and Yuan/year unit verified; candidate only"
        caveat += " Asked within the selected rural/residents/urban-residents pension follow-up (FN039 routes 3–5); retain payer and plan-specific denominator. Do not merge with monthly subsidies or infer zero from a skipped route."
        extra = {"unit": "Yuan/year", "value_label_status": "official questionnaire wording, route, and codebook unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code in {"fn062_1", "fn068_1"}:
        route = "selected rural/residents/urban-residents pension (FN039=3–5)" if code == "fn062_1" else "selected other pension program (FN039=6)"
        kind, concept, display = "expected age at pension receipt", "pension_expected_receipt_age", "预期开始领取养老金年龄"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; age response verified; candidate only"
        caveat += f" Conditional route: {route}; applicable only when the paired parent response-format selector indicates age. Keep separate from years-until-receipt responses."
        extra = {"unit": "years of age", "value_label_status": "official questionnaire range and response-format route reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code in {"fn062_2", "fn068_2"}:
        route = "selected rural/residents/urban-residents pension (FN039=3–5)" if code == "fn062_2" else "selected other pension program (FN039=6)"
        kind, concept, display = "expected years until pension receipt", "pension_expected_receipt_wait_years", "预期距离领取养老金年数"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; waiting-years response verified; candidate only"
        caveat += f" Conditional route: {route}; asked as years after the interview when the paired parent selector indicates years. Do not interpret as age or actual contribution duration."
        extra = {"unit": "years until expected receipt", "value_label_status": "official questionnaire wording and response-format route reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code in {"fn063_1", "fn069_1"}:
        route = "selected pension program(s) FN039=3–5" if code == "fn063_1" else "selected other pension program FN039=6"
        kind, concept, display = "expected monthly pension benefit", "pension_expected_monthly_benefit", "预期养老金月待遇"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; expected monthly amount and program route verified; candidate only"
        caveat += f" Expected (not currently received) amount; conditional route: {route}. Use only when the paired format field selects Yuan/month; keep distinct from lump-sum values and current-benefit amounts."
        extra = {"unit": "Yuan/month", "value_label_status": "official questionnaire wording, response format, and codebook unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code in {"fn063_2", "fn069_2"}:
        route = "selected pension program(s) FN039=3–5" if code == "fn063_2" else "selected other pension program FN039=6"
        kind, concept, display = "expected lump-sum pension benefit", "pension_expected_lump_sum_benefit", "预期养老金一次性待遇金额"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; expected lump-sum amount and program route verified; candidate only"
        caveat += f" Expected one-time total (not monthly); conditional route: {route}. Use only when the paired format field selects lump sum; do not annualize or merge with monthly benefits."
        extra = {"unit": "Yuan (lump sum)", "value_label_status": "official questionnaire wording, response format, and codebook unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code == "fn055":
        kind, concept, display = "commercial pension total premium amount", "pension_total_premium_amount_commercial", "商业养老金累计应缴保费总额"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; commercial-pension route and Yuan unit verified; candidate only"
        caveat += " 2011 commercial-pension module; the questionnaire routes this total premium after the annual-versus-lump-sum contribution item. Preserve that route and do not equate it with expected benefit amounts."
        extra = {"unit": "Yuan (total premium)", "value_label_status": "official 2011 questionnaire wording, route, and codebook unit reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code == "fn056":
        kind, concept, display = "commercial pension benefit payment form", "pension_benefit_payment_form_commercial", "商业养老金待遇领取方式"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; commercial-pension payment-form categories verified; candidate only"
        caveat += " 2011 categories distinguish lump-sum, annual, and monthly benefit forms; annual/monthly amount questions route from this answer. Preserve the raw category and do not interpret skipped amount responses as zero."
        extra = {"value_labels": "1=Lump sum; 2=Yearly; 3=Monthly", "value_label_status": "official answer categories transcribed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code == "fn057":
        kind, concept, display = "commercial pension expected annual benefit", "pension_expected_annual_benefit_commercial", "预期商业养老金年度待遇"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; Yuan/year and annual-benefit route verified; candidate only"
        caveat += " 2011 commercial-pension item, asked only when the benefit form is yearly; keep separate from monthly and lump-sum benefit amounts."
        extra = {"unit": "Yuan/year", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code == "fn058":
        kind, concept, display = "commercial pension expected monthly benefit", "pension_expected_monthly_benefit_commercial", "预期商业养老金月待遇"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; Yuan/month and monthly-benefit route verified; candidate only"
        caveat += " 2011 commercial-pension item, asked only when the benefit form is monthly; keep separate from annual and lump-sum benefit amounts."
        extra = {"unit": "Yuan/month", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code == "fn059":
        kind, concept, display = "commercial pension expected total benefit", "pension_expected_total_benefit_commercial", "预期商业养老金待遇总额"
        mapping_status = "2011 baseline questionnaire and codebook reviewed; commercial-pension expected total amount verified; candidate only"
        caveat += " 2011 commercial-pension expected total benefit; retain as a total amount and do not annualize or merge with monthly/yearly benefits."
        extra = {"unit": "Yuan (total benefit)", "value_label_status": "official questionnaire wording and codebook field reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif code == "fn037_w2_1":
        kind, concept, display = ("commercial pension account balance (latest reported check)",
                                  "pension_commercial_account_balance",
                                  "商业养老金账户余额（最近一次查看）")
        mapping_status = "official questionnaire and codebook reviewed; asked after defined-contribution plan route; amount only; candidate, not analysis-ready"
        caveat += " Asked only on the defined-contribution pension route after FN032_W*=2/997 and a Yes response to account-balance checking; the linked year/month fields identify when the balance was checked and are not separate exposures. Preserve missing/unknown codes and the wave-specific route."
        extra = {"unit": "Yuan", "value_label_status": "questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn043_w4":
        kind, concept, display = ("commercial pension current participation/receipt status",
                                  "pension_current_participation_or_receipt_commercial",
                                  "当前商业养老金参保/领取状态")
        mapping_status = "2018 questionnaire and codebook reviewed; three-category response; candidate only"
        caveat += " 2018-only item combines purchased/participating and currently receiving categories; 3=neither. Keep the original three-category response; do not collapse to binary without a prespecified estimand."
        extra = {"value_labels": "1=Yes, purchased/participating; 2=Yes, currently receiving benefits; 3=Neither participating nor receiving",
                 "value_label_status": "official answer categories transcribed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn047_w2":
        kind, concept, display = "commercial pension contribution payment method", "pension_contribution_method_commercial", "商业养老金缴费方式（按年/一次性）"
        mapping_status = "official questionnaire reviewed; commercial-pension route and categories verified; candidate only"
        caveat += " Asked within the commercial-pension section; response distinguishes annual from lump-sum payment. Do not infer annual amount for lump-sum respondents."
        extra = {"value_labels": "1=Annual payment; 2=Lump-sum payment", "value_label_status": "official answer categories transcribed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn048_w2":
        kind, concept, display = "commercial pension annual premium amount", "pension_annual_contribution_amount_commercial", "商业养老金年度缴费金额"
        mapping_status = "official questionnaire reviewed; Yuan/year and commercial-pension route verified; candidate only"
        caveat += " Annual amount in Yuan/year, asked on the annual-payment route; preserve amount brackets as interval components and do not compare directly with lump-sum totals."
        extra = {"unit": "Yuan/year", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn049_w2":
        kind, concept, display = "commercial pension required payment duration", "pension_required_contribution_years_commercial", "商业养老金要求缴费年限"
        mapping_status = "official questionnaire reviewed; years unit and commercial-pension route verified; candidate only"
        extra = {"unit": "years", "value_label_status": "official questionnaire unit reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn050_w2":
        kind, concept, display = "commercial pension total premium amount", "pension_total_premium_amount_commercial", "商业养老金累计应缴保费总额"
        mapping_status = "official questionnaire reviewed; Yuan and commercial-pension route verified; candidate only"
        extra = {"unit": "Yuan (total premium)", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn051_w2":
        kind, concept, display = "commercial pension benefit payment form", "pension_benefit_payment_form_commercial", "商业养老金待遇领取方式"
        mapping_status = "official questionnaire reviewed; routed payment-form categories verified; candidate only"
        caveat += " Response categories are lump-sum, annual, and monthly; annual/monthly amount questions are routed by this response. Preserve the category and do not treat downstream skipped amount fields as zero."
        extra = {"value_labels": "1=Lump-sum; 2=Annual; 3=Monthly", "value_label_status": "official answer categories transcribed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn052_w4":
        kind, concept, display = "commercial pension expected annual benefit", "pension_expected_annual_benefit_commercial", "预期商业养老金年度待遇"
        mapping_status = "2018 questionnaire reviewed; Yuan/year; asked only for annual benefit route; candidate only"
        caveat += " 2018-only; asked when FN051_W2=2 (annual payment form). Do not interpret skipped values as zero or merge with monthly/lump-sum amounts."
        extra = {"unit": "Yuan/year", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn053_w2":
        kind, concept, display = "commercial pension expected monthly benefit", "pension_expected_monthly_benefit_commercial", "预期商业养老金月待遇"
        mapping_status = "official questionnaire reviewed; Yuan/month and commercial-pension route verified; candidate only"
        caveat += " Asked on the monthly benefit route (2018 FN051_W2=3); period/unit is Yuan/month. Do not merge with annual or lump-sum benefit amounts."
        extra = {"unit": "Yuan/month", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn054_w2":
        kind, concept, display = "commercial pension expected total benefit", "pension_expected_total_benefit_commercial", "预期商业养老金待遇总额"
        mapping_status = "official questionnaire reviewed; lump-sum benefit route verified; candidate only"
        caveat += " Total amount is a distinct payment form; preserve the official routed universe and do not annualize or compare directly with monthly/annual benefits."
        extra = {"unit": "Yuan (total benefit)", "value_label_status": "official questionnaire unit and route reviewed; frequencies omitted",
                 "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif code == "fn092_w4":
        kind, concept, display = "commercial pension lump-sum premium amount", "pension_lump_sum_contribution_amount_commercial", "商业养老金一次性缴费金额"
        mapping_status = "2018 questionnaire reviewed; Yuan and explicit one-time-payment wording verified; candidate only"
        caveat += " 2018-only item explicitly asks for a one-time total premium; keep distinct from recurring annual premium and generic total-premium fields."
        extra = {"unit": "Yuan (one-time premium)", "value_label_status": "official questionnaire unit and wording reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif re.search(r"types? of pension", label, re.I):
        kind, concept, display = "pension scheme type (categorical/multi-select)", "pension_plan_type_received", "养老金计划类型（自报）"
    elif re.search(r"never received.*participat|never.*pension", label, re.I):
        kind, concept, display = "never received/participated pension history", "pension_never_received_or_participated", "是否从未领取或参加养老金（自报）"
    elif re.search(r"participat.*more than 10 years", label, re.I):
        kind, concept, display = "pension participation duration threshold", "pension_participation_over_10_years", "养老金参保是否超过10年（自报）"
    elif re.search(r"years? of .*participat|years? of .*contribut", label, re.I):
        kind, concept, display = "pension participation/contribution duration", "pension_participation_duration_years", "养老金参保/缴费年限（自报）"
    elif re.search(r"ever contributed to your pension|ever contributed", label, re.I):
        kind, concept, display = "pension contribution history", "pension_ever_contributed", "是否曾缴纳养老金（自报）"
    elif code.startswith("fn013_w2_") and re.fullmatch(r"fn013_w2_[12]_[12]_", code):
        if re.match(r"fn013_w2_1_", code):
            kind, concept, display = ("respondent monthly pension contribution amount",
                                      "pension_personal_monthly_contribution_amount",
                                      "本人每月养老金缴费金额")
        else:
            kind, concept, display = ("respondent pension contribution as salary ratio",
                                      "pension_personal_contribution_salary_ratio",
                                      "本人养老金缴费占工资比例")
    elif code.startswith("fn014_w2_") and re.fullmatch(r"fn014_w2_[12]_[12]_", code):
        if re.match(r"fn014_w2_1_", code):
            kind, concept, display = ("employer monthly pension contribution amount",
                                      "pension_employer_monthly_contribution_amount",
                                      "单位每月养老金缴费金额")
        else:
            kind, concept, display = ("employer pension contribution as salary ratio",
                                      "pension_employer_contribution_salary_ratio",
                                      "单位养老金缴费占工资比例")
    elif code.startswith(("fn013_w2_", "fn014_w2_")) and re.search(r"percentage/yuan|yuan/month or ratio|yuan/yue or ratio", label, re.I):
        payer = "personal" if code.startswith("fn013") else "employer"
        kind, concept, display = (f"{payer} pension contribution mixed amount-or-ratio response",
                                  f"pension_{payer}_contribution_amount_or_salary_ratio",
                                  f"{'本人' if payer == 'personal' else '单位'}养老金缴费金额或工资比例（混合单位）")
    elif code.startswith("fn013_w2_") and re.search(r"yuan.*per month|yuan/month|yuan/yue", label, re.I):
        kind, concept, display = ("respondent monthly pension contribution amount",
                                  "pension_personal_monthly_contribution_amount",
                                  "本人每月养老金缴费金额")
    elif code.startswith("fn013_w2_") and re.search(r"ratio of salary|percentage", label, re.I):
        kind, concept, display = ("respondent pension contribution as salary ratio",
                                  "pension_personal_contribution_salary_ratio",
                                  "本人养老金缴费占工资比例")
    elif code.startswith("fn014_w2_") and re.search(r"yuan.*per month|yuan/month|yuan/yue|how much.*contribut", label, re.I):
        kind, concept, display = ("employer monthly pension contribution amount",
                                  "pension_employer_monthly_contribution_amount",
                                  "单位每月养老金缴费金额")
    elif code.startswith("fn014_w2_") and re.search(r"ratio of salary|percentage", label, re.I):
        kind, concept, display = ("employer pension contribution as salary ratio",
                                  "pension_employer_contribution_salary_ratio",
                                  "单位养老金缴费占工资比例")
    elif re.search(r"pay the premium by yourself|yourself or through company|work unit contribute", label, re.I):
        kind, concept, display = "pension contribution payer/channel", "pension_contribution_payer_channel", "养老金缴费承担方/渠道（自报）"
    elif re.search(r"how do you contribute", label, re.I):
        kind, concept, display = "pension contribution method", "pension_contribution_method", "养老金缴费方式（自报）"
    elif re.search(r"currently|never received|ever participat", label, re.I):
        scheme = scheme_of(label)
        combined = bool(re.search(r"participat", label, re.I))
        if scheme == "unspecified_scheme" and re.search(r"least one kind|any pension", label, re.I):
            concept = "pension_current_receipt_any"
            display = "当前是否领取任一类养老金（自报）"
        else:
            mode = "participation_or_receipt" if combined else "receipt"
            concept = f"pension_current_{mode}_{scheme}"
            display = f"当前养老金参保/领取状态：{SCHEME_ZH[scheme]}"
        kind = "current pension participation/receipt status"
    elif code == "fn006_w2":
        kind, concept, display = ("combined current government/institution or firm pension participation status",
                                  "pension_current_government_firm_participation_status",
                                  "当前政府/机关事业单位或企业基本养老金参保状态")
    elif code == "fn002_w3":
        kind, concept, display = ("combined current pension receipt/participation status",
                                  "pension_current_any_receipt_or_participation",
                                  "当前是否领取或参加养老金（合并状态）")
    elif re.search(r"benefits?.*(?:per month|monthly).*(?:when you retired)|(?:per month|monthly).*when you retired", label, re.I):
        kind, concept, display = ("reported monthly pension benefit at retirement",
                                  "pension_retirement_monthly_benefit_amount",
                                  "退休时自报月养老金待遇金额")
    elif ((wave == "2011" and code in {
              "fn003_1", "fn003_2", "fn006_1", "fn006_2",
              "fn012_1", "fn012_2", "fn017_1", "fn017_2",
              "fn021_1", "fn021_2"})
          or re.search(r"year of receive .*pension|when did you start to receive .*pension", label, re.I)):
        kind, concept, display = ("reported pension benefit receipt start date component",
                                  "pension_benefit_start_date_components",
                                  "开始领取养老金待遇时间组成字段")
        if wave == "2011":
            mapping_status = "2011 baseline questionnaire and Codebook field, plan, date component, and skip route reviewed; candidate only"
            pension_routes = {
                "fn003_": "FN002=1 enterprise supplementary pension; asked only for current recipients",
                "fn006_": "FN002=2 commercial pension; asked only for current recipients",
                "fn012_": "FN002=3/4/5 rural, residents, or urban-residents pension; follows FN009 ever-contributed route and selected plan",
                "fn017_": "FN002=6 oldest-old pension subsidy; asked only for current recipients",
                "fn021_": "FN002=7 other pension; follows named other-program route",
            }
            route = next((v for prefix, v in pension_routes.items() if code.startswith(prefix)), "")
            caveat += f" 2011 baseline route: {route}. Year and month remain separate components across unlike pension programs; do not calculate one pooled date or treat month 0 as January."
            extra = {"unit": "calendar year" if code.endswith("_1") else "calendar month; 0=month not remembered",
                     "value_label_status": "2011 baseline questionnaire and Codebook field/route reviewed; frequencies omitted",
                     "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"}
    elif re.search(r"when did you start participating pension through this employer|when did you start to participate in the pension through this work unit", label, re.I):
        kind, concept, display = ("reported employer-plan participation start date component",
                                  "pension_employer_plan_participation_start_date",
                                  "通过当前/相关单位参加养老金计划的起始时间组成字段")
    elif re.search(r"monthly pension|monthly benefit|amount per month", label, re.I):
        kind, concept, display = "reported monthly pension benefit amount", "pension_monthly_benefit_amount", "自报月养老金待遇金额"
    elif re.search(r"how much is the combined contribution", label, re.I):
        kind, concept, display = "combined pension contribution amount-or-share response", "pension_combined_contribution_amount_or_share", "养老金合计缴费金额或个人缴费比例"
    elif re.search(r"how much you are entitled to", label, re.I):
        kind, concept, display = "reported pension entitlement amount-or-share response", "pension_entitlement_amount_or_share", "养老金应享待遇金额或比例"
    elif re.search(r"pension reduction.*percentage|reduction if leave early", label, re.I):
        kind, concept, display = "pension reduction amount-or-percentage response", "pension_early_exit_reduction_amount_or_ratio", "提前离岗养老金扣减金额或比例"
    elif re.search(r"how much premium do you need to pay in total", label, re.I):
        kind, concept, display = "reported total pension premium amount", "pension_total_premium_amount", "养老金计划累计应缴保费"
    elif re.search(r"expect.*receive.*per year after retirement", label, re.I):
        kind, concept, display = "expected annual post-retirement pension benefit", "pension_expected_annual_benefit", "预期退休后年度养老金待遇"
    elif re.search(r"expect.*receive.*per month after retirement", label, re.I):
        kind, concept, display = "expected monthly post-retirement pension benefit", "pension_expected_monthly_benefit", "预期退休后月养老金待遇"
    elif re.search(r"expect.*receive in total", label, re.I):
        kind, concept, display = "expected total pension benefit amount", "pension_expected_total_benefit", "预期养老金待遇总额"
    elif re.search(r"how much cash settlements did you receive", label, re.I):
        kind, concept, display = "reported pension cash settlement amount", "pension_cash_settlement_amount", "养老金一次性结算金额"
    elif re.search(r"how much do you receive now", label, re.I):
        kind, concept, display = "reported current pension benefit amount (period/unit to verify)", "pension_current_benefit_amount_unspecified_period", "当前养老金待遇金额（期间/单位待核）"
    elif re.search(r"how much do you expect (?:the )?benefits to be|expect benefits", label, re.I):
        kind, concept, display = "expected pension benefit amount (payment form to verify)", "pension_expected_benefit_amount_unspecified_form", "预期养老金待遇金额（领取形式待核）"
    elif re.search(r"how much was the compensation", label, re.I):
        kind, concept, display = "reported life-insurance compensation amount", "life_insurance_compensation_amount", "自报人寿保险理赔金额"
    elif re.search(r"annual contribution", label, re.I):
        kind, concept, display = "reported annual pension contribution amount", "pension_annual_contribution_amount", "自报年度养老金缴费金额"
    elif re.search(r"lump sum contribution", label, re.I):
        kind, concept, display = "reported lump-sum pension contribution amount", "pension_lump_sum_contribution_amount", "自报一次性养老金缴费金额"
    elif re.search(r"contribut.*pension", label, re.I):
        kind, concept, display = "pension contribution status", "pension_contribution_status", "养老金缴费状态（自报）"
    elif re.search(r"yuan/month or ratio of salary", label, re.I):
        kind, concept, display = "pension contribution mixed amount-or-ratio response", "pension_contribution_amount_or_salary_ratio", "养老金缴费金额或工资比例（需按计划辨别）"
    elif re.search(r"ratio of salary|percentage.*contribut", label, re.I):
        kind, concept, display = "reported pension contribution ratio", "pension_contribution_salary_ratio", "自报养老金缴费比例"
    elif code in {"fn106_w4_1", "fn107_w4_1"}:
        is_medical = code.startswith("fn107")
        concept = "medical_insurance_subsidy_ratio" if is_medical else "pension_insurance_subsidy_ratio"
        display = "医疗保险补贴比例" if is_medical else "养老保险补贴比例"
        kind = "reported monthly insurance subsidy share (percent)"
        mapping_status = "2018 questionnaire item and routing verified; percentage scale reviewed; candidate only"
        caveat = "2018-only reported subsidy share. Keep medical and pension insurance separate; asked within the FN104–FN107 subsidy loop after the respondent reports receiving 4050 subsidies. Not harmonized with annual or lump-sum subsidy amounts in earlier waves."
        extra = {"unit": "percent (0–100)", "value_label_status": "official questionnaire scale reviewed; frequencies omitted", "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code in {"fn106_w4_2", "fn107_w4_2"}:
        is_medical = code.startswith("fn107")
        concept = "medical_insurance_subsidy_monthly_amount" if is_medical else "pension_insurance_subsidy_monthly_amount"
        display = "医疗保险月补贴金额" if is_medical else "养老保险月补贴金额"
        kind = "reported monthly insurance subsidy amount"
        mapping_status = "2018 questionnaire item and routing verified; Yuan/month unit reviewed; candidate only"
        caveat = "2018-only reported monthly amount. Keep medical and pension insurance separate; asked within the FN104–FN107 subsidy loop after the respondent reports receiving 4050 subsidies. Do not combine with percentage responses or earlier annual/lump-sum subsidy amounts."
        extra = {"unit": "Yuan/month", "value_label_status": "official questionnaire unit reviewed; frequencies omitted", "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif re.search(r"subsidy", label, re.I) and re.search(r"ratio", label, re.I):
        kind, concept, display = "reported pension subsidy ratio", "pension_subsidy_ratio", "自报养老金补贴比例"
    elif re.search(r"subsidy", label, re.I) and re.search(r"annual", label, re.I):
        kind, concept, display = "reported annual pension subsidy amount", "pension_subsidy_annual_amount", "自报年度养老金补贴金额"
        extra = {"unit": "Yuan/year", "value_label_status": "annual period verified from official variable label; frequencies omitted", "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif re.search(r"subsidy", label, re.I) and re.search(r"lump sum", label, re.I):
        kind, concept, display = "reported lump-sum pension subsidy amount", "pension_subsidy_lump_sum_amount", "自报一次性养老金补贴金额"
        extra = {"unit": "Yuan (lump sum)", "value_label_status": "lump-sum period verified from official variable label; frequencies omitted", "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"}
    elif re.search(r"subsidy", label, re.I) and re.search(r"yuan|amount", label, re.I):
        kind, concept, display = "reported pension subsidy amount (period to verify)", "pension_subsidy_amount_period_unspecified", "自报养老金补贴金额（期间待核）"
    elif code == "fn002_w4" or code == "fn099_w4":
        kind, concept, display = "current pension receipt/participation overall item", "pension_current_any_receipt_or_participation", "当前是否领取/参加养老金（合并题）"
    elif re.fullmatch(r"fn002_w4_a_s\d+", code):
        kind, concept, display = "pension plan type selection component", "pension_current_plan_type_selection", "当前养老金计划类型选择项"
    elif code.startswith("fn002_w4_b_"):
        suffix = re.search(r"_b_(\d+)", code)
        kind = "current receipt by government/institution/firm plan item"
        if suffix and suffix.group(1) in {"1", "2", "3"}:
            scheme = {"1": "government_institution", "2": "government_institution", "3": "enterprise_employee"}[suffix.group(1)]
            concept = f"pension_current_receipt_{scheme}"
            display = f"当前领取养老金：{SCHEME_ZH[scheme]}"
        else:
            concept, display = "pension_current_any_receipt_or_participation", "当前是否领取/参加养老金（合并题）"
    elif re.search(r"if ever had the pension", label, re.I):
        kind, concept, display = "historical pension plan participation/receipt roster slot", "pension_ever_had_plan_type", "曾参加/领取养老金计划类型（历史槽位）"
    elif re.search(r"expect.*(?:start.*receiv|receive.*benefit)|expect.*receive this pension", label, re.I):
        kind, concept, display = "expected future pension receipt timing", "pension_expected_benefit_start_timing", "预期开始领取养老金时间"
    elif re.search(r"receive pension in the future|expect.*receive pension", label, re.I):
        kind, concept, display = "expected future pension receipt status", "pension_expected_future_receipt", "预期未来是否领取养老金"
    elif re.search(r"age of receive pension|old enough to receive pension", label, re.I):
        kind, concept, display = "expected pension receipt age threshold", "pension_expected_receipt_age", "预期开始领取养老金年龄"
    elif re.search(r"what you can rely on financially for old-age support|whom do you think you can rely on financially", label, re.I):
        kind, concept, display = "reported financial old-age support source", "old_age_financial_support_source", "自报老年经济支持来源"
    elif re.search(r"4050 subsidy", label, re.I) and code == "fn104_w4":
        kind, concept, display = "4050 subsidy receipt status", "pension_4050_subsidy_receipt", "4050补贴领取状态"
    elif code in {"fn105_w4_1", "fn105_w4_2"}:
        kind, concept, display = ("4050 subsidy receipt start date component",
                                  "pension_4050_subsidy_start_date",
                                  "4050补贴开始领取时间")
        mapping_status = "2018 questionnaire item and FN104=Yes route verified; year/month component metadata reviewed; candidate only"
        caveat = "Only asked after FN104_W4=1 (reports receiving the subsidy). Preserve year and month separately; month 0 means month not remembered and must not be treated as January or a complete date. This 2018-only reported start date is not a measure of subsidy amount, duration, or a consistently harmonized cross-wave policy exposure."
        extra = {
            "unit": "calendar year" if code.endswith("_1") else "calendar month; 0=month not remembered",
            "value_label_status": "continuous date-component range and month-0 convention verified from official questionnaire; frequencies omitted",
            "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
        }
    elif re.search(r"need to pay the premium|need to contribute|pay insurance premium", label, re.I):
        kind, concept, display = "pension premium/contribution requirement status", "pension_contribution_requirement", "养老金是否需要缴费/缴纳保费"
    elif re.search(r"how is the contributes collected|pay it monthly|pay it annually|pay it every six months", label, re.I):
        kind, concept, display = "pension contribution collection frequency/method", "pension_contribution_frequency", "养老金缴费频率/收取方式"
    elif re.search(r"expected benefits yuan/percentage|yuan/month or percentage of final pay|percentage of final pay", label, re.I):
        kind, concept, display = "expected retirement benefit amount or final-pay ratio", "pension_expected_retirement_benefit_amount_or_ratio", "预期退休待遇金额或末期工资比例"
    elif re.search(r"participated in (?:the )?old rural pension|participate in land expropriation pension", label, re.I):
        kind, concept, display = "historical participation in named pension plan", "pension_historical_named_plan_participation", "曾参加特定养老金计划（自报）"
    elif re.search(r"who get you this pension", label, re.I):
        scheme = scheme_of(label)
        concept = f"pension_benefit_source_{scheme}"
        display = f"养老金待遇来源：{SCHEME_ZH[scheme]}"
        kind = "reported pension benefit source/provider"
    elif (re.search(r"who pay for|who paid for", label, re.I)
          and not re.fullmatch(r"fn072_w3_5_[123]_s\d+", code)):
        scheme = scheme_of(label)
        period = "last_year" if re.search(r"last year", label, re.I) else "program_or_current"
        concept = f"pension_contribution_payer_{scheme}_{period}"
        display = f"养老金缴费承担来源：{SCHEME_ZH[scheme]}（{'上年' if period == 'last_year' else '当前/该计划'}）"
        kind = "reported pension contribution payer/source"
    elif code == "fn062_w4":
        concept, display, kind = ("pension_resident_plan_contribution_required_2018",
                                  "居民类养老金是否需要缴费（2018）",
                                  "resident-plan contribution requirement status")
        mapping_status = "2018 questionnaire FN062_W4 and codebook Yes/No categories verified; candidate only"
        caveat += " Asked for the preloaded resident pension plan the respondent expects to receive or currently contributes to. No routes past the amount fields; skipped subsidy/contribution amounts are not zero. Contributions explicitly include both individual payments and government subsidies."
        extra = {"value_label_status": "official questionnaire route and codebook response categories reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code in {"fn062_w4_a_1", "fn062_w4_a_2", "fn062_w4_b_1", "fn062_w4_b_2"}:
        kind_is_subsidy = code.startswith("fn062_w4_a_")
        who = "government_subsidy" if kind_is_subsidy else "individual_contribution"
        period = "monthly" if code.endswith("_1") else "annual"
        amount_label = "政府补贴" if kind_is_subsidy else "个人缴费"
        concept = f"pension_resident_plan_{who}_{period}_amount_2018"
        display = f"居民类养老金{amount_label}{'月' if period == 'monthly' else '年'}金额（2018）"
        kind = f"{who.replace('_',' ')} amount ({period})"
        mapping_status = "2018 questionnaire FN062_W4_a/b unit-specific amount and codebook numeric field verified; candidate only"
        caveat += " Only after FN062_W4=Yes for the selected resident pension plan. Keep monthly and annual fields separate; do not convert without a defined method. Questionnaire specifies -1 for unknown and prompts for follow-up brackets at -1 or 0; validate sentinels and extreme values against authorized data before analysis."
        extra = {"unit": "Yuan/month" if period == "monthly" else "Yuan/year",
                 "value_label_status": "questionnaire unit and -1 unknown convention verified; respondent-file sentinel distribution not validated",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn063_w4":
        concept, display, kind = ("pension_resident_plan_account_balance_checked_2018",
                                  "是否查看过居民类养老金账户余额（2018）",
                                  "resident-plan account-balance checking status")
        mapping_status = "2018 questionnaire FN063_W4 route and codebook response categories verified; candidate only"
        caveat += " Asked of current contributors or other participants in the selected resident pension plan. Yes routes to account balance and last-check date; missing follow-ups are not No/zero."
        extra = {"value_label_status": "official questionnaire route and codebook response categories reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn063_w4_1":
        concept, display, kind = ("pension_resident_plan_account_balance_amount_2018",
                                  "居民类养老金账户余额金额（2018）",
                                  "resident-plan account balance")
        mapping_status = "2018 questionnaire FN063_W4 amount in Yuan and codebook numeric field verified; candidate only"
        caveat += " Asked only after FN063_W4=Yes. Questionnaire identifies Yuan and captures the balance for the selected resident plan; interpret together with last-check date fields, which are metadata. Validate special missing codes in authorized data before analysis."
        extra = {"unit": "Yuan",
                 "value_label_status": "questionnaire amount unit verified; respondent-file missing/value semantics not validated",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn069_w4" and wave == "2018":
        concept, display, kind = ("pension_resident_plan_local_eligibility_2018",
                                  "居民类养老金当地实施与个人参保资格（2018）",
                                  "resident-plan local implementation/eligibility status")
        mapping_status = "2018 questionnaire FN069_W4 scope, skip route, and codebook categories verified; candidate only"
        caveat += " Measures whether the hukou-registered community implemented the listed resident pension programs and the respondent could participate if willing. Yes skips to the age requirement item; No asks the reason for ineligibility; don't-know skips the reason. Keep unknown distinct from No and do not treat this as actual participation or benefit receipt."
        extra = {"value_label_status": "official questionnaire categories and skip routes verified; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn084_w4" and wave == "2018":
        concept, display, kind = ("pension_other_program_current_receipt_status_2018",
                                  "所选其他养老金计划当前是否领取待遇（2018）",
                                  "selected other-pension-program current receipt status")
        mapping_status = "2018 questionnaire FN083_W2/FN084_W4 route and codebook binary values verified; candidate only"
        caveat += " Asked only when the respondent reports another pension program at FN083_W2; when multiple other plans are present, the interviewer selects the most important plan. This follow-up verifies current receipt for that selected program; do not treat it as coverage of every other pension plan."
        extra = {"value_label_status": "official questionnaire Yes/No categories and upstream route reviewed; codebook frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn079_w2_3" and wave in {"2013", "2015", "2018"}:
        concept, display, kind = ("pension_land_requisition_plan_participation_receipt_status",
                                  "征地养老保险参保/领取状态",
                                  "land-requisition pension participation and receipt status")
        mapping_status = "2013/2015/2018 questionnaires and codebooks confirm the same three response states; candidate only"
        caveat += " Asked only after reporting that land was requisitioned (FN079_W2_1=Yes). Categories distinguish participating but not yet receiving, currently receiving, and not participating. Preserve the three-category status; the denominator is respondents reporting land requisition."
        extra = {"value_labels": "1=Participating now, not receiving yet; 2=Receiving now; 3=Not participating",
                 "value_label_status": "official response categories verified in 2013, 2015 and 2018 questionnaire/codebooks; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt; sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn057_w4_5":
        concept, display, kind = ("pension_reason_not_receiving_resident_plan_benefit",
                                  "未领取居民类养老金待遇原因（2018）",
                                  "reported reason for not receiving resident-plan benefits")
        mapping_status = "2018 questionnaire and codebook options verified; routed after age-eligibility question; candidate only"
        caveat += " Asked only of respondents who had reached the statutory age threshold but reported no current receipt; denominator is this routed subgroup, not all non-recipients or all eligible respondents. Keep separate from reasons for nonparticipation or nonpayment."
        extra = {"value_label_status": "official 2018 questionnaire and codebook response categories verified; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn057_w3_6":
        concept, display, kind = ("pension_reason_not_paying_resident_plan_premium",
                                  "未缴纳居民类养老金保费原因（2018）",
                                  "reported reason for not paying resident-plan premium")
        mapping_status = "2018 questionnaire and codebook options verified; current nonpayment route verified; candidate only"
        caveat += " Asked only after the respondent reported not currently paying; denominator is the routed nonpayers. It is not interchangeable with FN057_W4_5 (reason for not receiving benefits) or plan-specific 2015 reasons."
        extra = {"value_label_status": "official 2018 questionnaire and codebook response categories verified; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn069_w4_a":
        concept, display, kind = ("pension_reason_ineligible_resident_plan",
                                  "居民类养老金不具备资格原因（2018）",
                                  "reported reason for resident-plan ineligibility")
        mapping_status = "2018 questionnaire and codebook options verified; asked only after ineligibility response; candidate only"
        caveat += " Asked only after FN069_W4 reports ineligible (and excludes the don't-know branch); denominator is respondents reporting ineligibility. Keep distinct from nonparticipation and nonreceipt reasons."
        extra = {"value_label_status": "official 2018 questionnaire and codebook response categories verified; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn075_w3_4_1_":
        concept, display, kind = ("pension_post_supplementary_annual_payment_status_new_rural",
                                  "新农保补缴后是否继续按年缴费",
                                  "post-supplementary annual pension payment status")
        mapping_status = "2015 questionnaire page 181 and codebook response labels verified; candidate only"
        caveat += " Asked after FN075_W3 supplementary repayment. A Yes/No item about continuing annual payments is not an amount; follow-up duration and total paid are separate fields."
        extra = {"value_label_status": "official 2015 questionnaire/codebook response categories verified; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 181); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif code == "fn075_w3_4_1_1_":
        concept, display, kind = ("pension_post_supplementary_annual_payment_duration_new_rural",
                                  "新农保补缴后继续按年缴费年数",
                                  "post-supplementary annual pension payment duration")
        mapping_status = "2015 questionnaire page 181 defines duration in years; codebook value range conflicts with expected duration and is locked from analysis pending reconciliation"
        caveat += " Questionnaire asks the number of years of continued annual payment, but the codebook summary range includes 2012 and a negative sentinel (-999), incompatible with an ordinary duration. Candidate metadata only; DO NOT ANALYZE until source field/value labels and sentinel handling are reconciled."
        extra = {"unit": "years (questionnaire wording; codebook conflict unresolved)",
                 "value_label_status": "questionnaire wording reviewed; codebook range conflict unresolved; DO NOT ANALYZE",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 181); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif code == "fn075_w3_4_2_1_":
        concept, display, kind = ("pension_post_supplementary_annual_payment_total_amount_new_rural",
                                  "新农保补缴后继续按年缴费累计金额",
                                  "post-supplementary annual pension payment total amount")
        mapping_status = "2015 questionnaire page 181 and codebook variable label/unit reviewed; candidate only"
        caveat += " Asked only after reporting continued annual payments following supplementary repayment. Questionnaire specifies total Yuan amount; codebook summaries contain negative sentinel values, which must be identified from authorized raw-data labels before analysis."
        extra = {"unit": "Yuan (reported total)",
                 "value_label_status": "questionnaire unit and codebook field label verified; special missing codes not yet checked in respondent file",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 181); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn075_w3_([123])_", code):
        scheme = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[re.fullmatch(r"fn075_w3_([123])_", code).group(1)]
        concept = f"pension_supplementary_repayment_status_{scheme}"
        display = f"是否补缴居民类养老金：{SCHEME_ZH[scheme]}"
        kind = "supplementary pension repayment status"
        mapping_status = "2015 questionnaire FN075_W3 routed by selected plan and codebook scheme-specific status label verified; candidate only"
        caveat += " Yes/No status for whether a supplementary payment was required/made for this plan. Keep separate by scheme and retain the FN057_W3 selected-plan route; unasked fields are not No."
        extra = {"value_label_status": "official 2015 questionnaire and codebook categories reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 180); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn075_w3_5_([123])_", code):
        scheme = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[re.fullmatch(r"fn075_w3_5_([123])_", code).group(1)]
        concept = f"pension_contribution_payer_{scheme}_supplementary"
        display = f"养老金补缴费用承担者：{SCHEME_ZH[scheme]}"
        kind = "reported supplementary pension contribution payer"
        mapping_status = "2015 questionnaire page 181 identifies a multiple-response payer question; plan-specific codebook field verified; candidate only"
        caveat += " Multiple-response payer field for supplementary contributions, separate by pension plan. Child-slot choices and other-family/other-person responses must retain their released storage semantics; unselected options are not assumed to be explicit No."
        extra = {"value_label_status": "official 2015 questionnaire/codebook labels reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 181); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif code == "fn072_w3" and wave == "2018":
        concept, display, kind = ("pension_supplementary_repayment_required_selected_plan_2018",
                                  "加入所选居民类养老金时是否需要补缴（2018）",
                                  "selected resident-plan supplementary repayment status")
        mapping_status = "2018 questionnaire FN072_W3 and codebook Yes/No/unknown/refusal categories verified; candidate only"
        caveat += " Asked for the preloaded selected plan. Questionnaire defines make-up contributions as lump-sum or repeated payments for a short contribution history at age 60, prior nonparticipation, or seeking higher future pension. No/unknown/refusal routes skip the amount/date follow-ups; do not impute zero."
        extra = {"value_label_status": "official questionnaire definition, route and codebook categories reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code == "fn072_w3":
        concept, display, kind = ("pension_supplementary_repayment_required_selected_plan",
                                  "所选居民类养老金是否需要补缴",
                                  "supplementary repayment status for selected pension plan")
        mapping_status = "2015 questionnaire page 178 FN072_W3 question and Yes/No route verified; candidate only"
        caveat += " Asked after FN060_W2 contribution history is Yes, for the preloaded selected pension plan. A No response skips the amount/payer follow-ups; skipped fields are not zero."
        extra = {"value_label_status": "official questionnaire response categories and skip verified; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 178); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif code in {"fn072_w3_1_1", "fn072_w3_1_2"} and wave == "2018":
        scale = "Yuan" if code.endswith("_1") else "10,000 Yuan"
        concept = "pension_supplementary_repayment_total_selected_plan_2018"
        display = "加入所选居民类养老金时补缴总额（2018）"
        kind = "supplementary repayment total amount"
        mapping_status = "2018 questionnaire FN072_W3_1 amount and scale-specific codebook field verified; candidate only"
        caveat += " Asked only after FN072_W3=Yes for the selected resident pension plan. The questionnaire defines make-up payment broadly; preserve Yuan and 10,000-Yuan fields separately and convert only via the unit selector. Questionnaire specifies -1 unknown and follow-up brackets for -1/0; codebook summary has -1 and extreme ranges, so validate sentinel handling against authorized raw data before analysis."
        extra = {"unit": scale,
                 "value_label_status": "questionnaire unit and -1 unknown convention verified; respondent-file value validity not assessed",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif code in {"fn072_w4_b_1", "fn072_w4_b_2"} and wave == "2018":
        component = "year" if code.endswith("_1") else "month"
        concept = "pension_supplementary_repayment_date_components_selected_plan_2018"
        display = "加入所选居民类养老金补缴时间组成字段（2018）"
        kind = f"supplementary payment date {component} component"
        mapping_status = "2018 questionnaire FN072_W4_b asks make-up contribution date; official component and month-0 convention verified; candidate only"
        caveat += " Date of the make-up payment, asked only following the selected-plan repayment route. Preserve year/month as components; month 0 means not remembered, not January. This is a date component rather than a standardized contribution-duration measure."
        extra = {"unit": "calendar year" if component == "year" else "calendar month; 0=month not remembered",
                 "value_label_status": "official questionnaire date range and month-0 convention verified; codebook frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn072_w3_([123])_", code):
        scheme = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[re.fullmatch(r"fn072_w3_([123])_", code).group(1)]
        concept = f"pension_supplementary_repayment_status_{scheme}"
        display = f"是否补缴居民类养老金：{SCHEME_ZH[scheme]}"
        kind = "scheme-specific supplementary repayment status"
        mapping_status = "2015 codebook scheme-specific response field mapped to questionnaire FN072_W3 selected-plan route; candidate only"
        caveat += " Plan-specific status attached to the FN057_W3 selected-plan loop; a blank for a nonselected scheme is not No. Keep distinct from subsequent total and personal amounts."
        extra = {"value_label_status": "official questionnaire/codebook response categories reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 178); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn072_w3_1_([12])_([123])_", code):
        m = re.fullmatch(r"fn072_w3_1_([12])_([123])_", code); scale, scheme = m.groups()
        scheme_slug = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[scheme]
        kind, concept = "total supplementary repayment amount", f"pension_supplementary_repayment_total_{scheme_slug}"
        display = f"养老金补缴总额：{SCHEME_ZH[scheme_slug]}"
        mapping_status = "2015 questionnaire amount and Yuan/10,000 Yuan unit verified; plan-specific codebook value field mapped; candidate only"
        caveat += " Convert the 10,000-Yuan field to Yuan using its unit selector before pooling. Do not sum total and personal amount. Asked only on the selected-plan repayment route."
        extra = {"unit": "Yuan" if scale == "1" else "10,000 Yuan",
                 "value_label_status": "questionnaire unit and plan-specific codebook field reviewed; respondent-value special missings not validated",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 178); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn072_w3_2_([12])_([123])_", code):
        m = re.fullmatch(r"fn072_w3_2_([12])_([123])_", code); scale, scheme = m.groups()
        scheme_slug = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[scheme]
        kind, concept = "personal supplementary repayment amount", f"pension_supplementary_repayment_personal_{scheme_slug}"
        display = f"养老金补缴个人部分：{SCHEME_ZH[scheme_slug]}"
        mapping_status = "2015 questionnaire personal-payment question and Yuan/10,000 Yuan unit verified; codebook plan field mapped; candidate only"
        caveat += " Convert the 10,000-Yuan field to Yuan using its unit selector before pooling. Keep personal amount separate from total repayment; do not sum them. Asked only on the selected-plan repayment route."
        extra = {"unit": "Yuan" if scale == "1" else "10,000 Yuan",
                 "value_label_status": "questionnaire unit and plan-specific codebook field reviewed; respondent-value special missings not validated",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 178); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn072_w3_4_([123])_", code):
        scheme = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[re.fullmatch(r"fn072_w3_4_([123])_", code).group(1)]
        kind, concept = "continued annual pension payment status", f"pension_supplementary_route_continued_annual_payment_{scheme}"
        display = f"补缴后是否继续按年缴费：{SCHEME_ZH[scheme]}"
        mapping_status = "2015 questionnaire page 178 conditional continuation question and codebook plan-specific field reviewed; candidate only"
        caveat += " Asked only after supplementary payment, by selected plan. Yes routes to annual amount, subsidy, completed-year and remaining-year fields; skipped follow-ups are not zero."
        extra = {"value_label_status": "official questionnaire route and codebook labels reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 178); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn072_w3_4_([1-4])_([123])_", code):
        m = re.fullmatch(r"fn072_w3_4_([1-4])_([123])_", code); item, scheme = m.groups()
        scheme_slug = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[scheme]
        mapping_info = {
            "1": ("annual contribution amount", f"pension_supplementary_route_annual_contribution_{scheme_slug}", "元/年"),
            "2": ("annual government subsidy amount", f"pension_supplementary_route_annual_subsidy_{scheme_slug}", "Yuan/year"),
            "3": ("completed annual contribution duration", f"pension_supplementary_route_years_already_paid_{scheme_slug}", "years"),
            "4": ("remaining annual contribution duration", f"pension_supplementary_route_years_remaining_{scheme_slug}", "years"),
        }[item]
        kind, concept, unit = mapping_info
        display = f"补缴后按年缴费{kind}：{SCHEME_ZH[scheme_slug]}"
        mapping_status = "2015 questionnaire page 178 field sequence and codebook plan-specific label verified; candidate only"
        caveat += " Asked only after continued annual payment is reported for this plan. Amount/duration is plan-specific; do not treat skipped responses as zero or combine years with currency amounts."
        extra = {"unit": unit,
                 "value_label_status": "questionnaire item sequence and codebook plan-specific label reviewed; respondent special-missing codes not validated",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 178); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn072_w3_5_([123])_s\d+", code):
        scheme = re.fullmatch(r"fn072_w3_5_([123])_s\d+", code).group(1)
        scheme_slug = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[scheme]
        kind, concept = "prior-year pension contribution payer", f"pension_contribution_payer_{scheme_slug}_last_year"
        display = f"上年养老金缴费承担者：{SCHEME_ZH[scheme_slug]}"
        mapping_status = "2015 questionnaire page 178 multiple-response payer item and codebook selected-option slots reviewed; candidate only"
        caveat += " Source fields are selected-option slots for a multi-response item. Treat selected options as endorsements; blank/unselected child slots are not explicit negative responses. Plan-specific and prior-year denominator."
        extra = {"value_label_status": "official questionnaire response choices and codebook selected-option storage reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed pages 178–179); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn057_w3_5_([123])_", code):
        scheme = re.fullmatch(r"fn057_w3_5_([123])_", code).group(1)
        scheme_slug = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[scheme]
        concept, kind = f"pension_reason_not_receiving_benefit_{scheme_slug}_2015", "reported reason for not receiving pension benefit"
        display = f"未领取居民类养老金原因（2015）：{SCHEME_ZH[scheme_slug]}"
        mapping_status = "2015 questionnaire page 177 route/options and scheme-specific codebook response categories reviewed; candidate only"
        caveat += " Conditional reason item for the selected plan, asked after the eligibility/age and current-benefit route; analyze only within the routed nonrecipients. Do not treat skipped responses as no reason."
        extra = {"value_label_status": "official 2015 questionnaire and plan-specific codebook categories reviewed; frequencies omitted",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 177); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.fullmatch(r"fn057_w3_6_([123])_", code):
        scheme = re.fullmatch(r"fn057_w3_6_([123])_", code).group(1)
        scheme_slug = {"1": "new_rural_social", "2": "residents", "3": "urban_residents"}[scheme]
        concept, kind = f"pension_reason_not_paying_premium_{scheme_slug}_2015", "reported reason for not paying pension premium"
        display = f"未缴纳居民类养老金保费原因（2015）：{SCHEME_ZH[scheme_slug]}"
        mapping_status = "2015 questionnaire page 177 asks reason for nonpayment; codebook response options align but English field title says not receiving; DO NOT ANALYZE pending source reconciliation"
        caveat += " Questionnaire wording and response categories describe reasons for not paying, but the codebook English field title says 'Reason for Not Receive'. Keep separate from FN057_W3_5 nonreceipt reasons and do not analyze until this source-label conflict is reconciled. Conditional on the plan-specific nonpayment route."
        extra = {"value_label_status": "questionnaire wording/options reviewed; codebook English field-title discrepancy unresolved; DO NOT ANALYZE",
                 "value_label_source": "sources_official/CHARLS_2015_Questionnaire.pdf (printed page 177); sources_official/CHARLS_2015_Codebook_extracted.txt"}
    elif re.search(r"reason.*(?:do not|don't|not).*participat", label, re.I):
        scheme = scheme_of(label)
        concept = f"pension_nonparticipation_reason_{scheme}"
        display = f"未参加养老金原因：{SCHEME_ZH[scheme]}"
        kind = "reported reason for nonparticipation"
    elif re.search(r"reason you stop to participate|reason for stopping participation", label, re.I):
        concept, display, kind = "pension_participation_cessation_reason", "停止养老金参保原因（自报）", "reported reason for stopping pension participation"
    elif re.search(r"years?.*(?:included|been included).*(?:other province)", label, re.I):
        concept, display, kind = "pension_credited_years_other_province", "异地养老金计划累计参保年限", "reported pension credited duration in other province"
    elif re.search(r"years?.*(?:included|been included).*(?:local province)", label, re.I):
        concept, display, kind = "pension_credited_years_local_province", "本地养老金计划累计参保年限", "reported pension credited duration in local province"
    elif re.search(r"years?.*(?:included|been included).*(?:when.*retir|retir.*when)", label, re.I):
        concept, display, kind = "pension_years_in_plan_at_retirement", "退休时该养老金计划累计年限", "reported pension plan duration at retirement"
    elif re.search(r"years?.*(?:included|been included).*(?:program|plan)", label, re.I):
        concept, display, kind = "pension_current_plan_duration_years", "养老金计划累计参保年限", "reported pension plan duration"
    elif re.search(r"how many years do you need to pay", label, re.I):
        concept, display, kind = "pension_required_contribution_years", "养老金计划要求缴费年限", "reported required pension contribution duration"
    elif re.search(r"enough years to receive pension|enough year to receive pension", label, re.I):
        concept, display, kind = "pension_qualifying_years_sufficiency", "自报养老金缴费年限是否足够领取待遇", "self-reported eligibility-duration assessment"
    elif re.search(r"(year|month).*(?:stop this pension|stop receiving pension)|(?:stop this pension|stop receiving pension).*(year|month)", label, re.I):
        concept, display, kind = "pension_benefit_cessation_date_components", "停止领取养老金时间组成字段", "reported pension cessation year/month component"
    elif re.search(r"(year|month).*(?:start.*receiv|receive pension|receive the benefits)|(?:start.*receiv|receive pension|receive the benefits).*(year|month)", label, re.I):
        concept, display, kind = "pension_benefit_start_date_components", "开始领取养老金时间组成字段", "reported pension receipt start year/month component"
    elif re.search(r"did you start to receive benefits", label, re.I):
        concept, display, kind = "pension_benefits_started_status", "是否已开始领取养老金待遇", "reported pension benefit commencement status"
    if wave == "2018" and code == "fn076_w4":
        kind, concept, display = "future life-insurance benefit receipt status", "pension_expected_future_receipt", "预期未来是否领取人寿保险待遇"
        mapping_status = "2018 official questionnaire binary status and skip route verified; candidate only"
        caveat += " Specifically asks whether the respondent can receive future pension benefits from the life-insurance policy. No/unknown skips the expected timing follow-up; do not confuse with current receipt."
        extra = {"value_labels": "1=Yes; 2=No", "value_label_status": "official questionnaire/codebook response labels reviewed; frequencies omitted", "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"}
    if not kind:
        continue
    rows.append({
        "wave": wave, "code": rec.variable, "concept_id": concept,
        "concept_label": display, "domain": "social protection", "module": module,
        "source_label": label, "mapping_status": mapping_status,
        "construct": kind, "scheme_hint": scheme,
        "caveat": caveat,
        "source_archive": rec.source,
        **extra,
    })

# Explicit historical-enrollment follow-up. This only appears after the
# current-participation item routes respondents who are not currently enrolled.
# Wave 2 matches the questionnaire and codebook; Wave 3's question wording is
# narrower than the codebook label, so keep it searchable but block analysis.
historical_specs = [
    ("2013", "fn022_w2", "pension_past_basic_plan_participation_when_not_currently_enrolled",
     "当前未参保者既往基本养老金参保类型", "1=Government/institutions; 2=Enterprise basic pension; 3=Both; 4=No",
     "questionnaire and codebook agree; only asked on FN006_W2=4 route",
     "2013问卷在当前未参加政府/事业单位或企业基本养老保险者中询问既往参保；代码本与问卷一致。保留政府/事业单位、企业、两者、从未四类原始回答。"),
    ("2015", "fn022_w3", "pension_past_government_institution_plan_participation_when_not_currently_enrolled",
     "当前未参保者既往政府/事业单位养老金参保（范围待核）", "1=Yes; 2=No",
     "questionnaire/codebook scope discrepancy; DO NOT ANALYZE",
     "仅在FN006_W2=4当前未参保路径提问。2015问卷题干仅写政府/事业单位养老金，代码本变量标签却写政府/事业单位或企业基本养老金；范围不一致，保留检索候选但在官方释义澄清前不得分析。"),
]
for wave, code, concept, display, values, status, caveat in historical_specs:
    rec = raw[(raw.wave.astype(str) == wave) & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official catalog row for {wave}/{code}; found {len(rec)}")
    rec = rec.iloc[0]
    rows.append({
        "wave": wave, "code": rec.variable, "concept_id": concept,
        "concept_label": display, "domain": "social protection", "module": rec.module,
        "source_label": rec.variable_label, "mapping_status": status,
        "construct": "prior basic-pension enrollment among respondents not currently enrolled",
        "scheme_hint": "historical enrollment; routed follow-up",
        "caveat": caveat, "source_archive": rec.source,
        "value_labels": values,
        "value_label_status": "official answer categories transcribed; frequencies omitted",
        "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt; sources_official/CHARLS_{wave}_Questionnaire_extracted.txt",
    })

# Exact 2018 questionnaire components for expected pension-claim timing.
# Keep age and elapsed years as distinct units and honor their routed plan.
timing_specs = [
    ("fn046_w4_1", "pension_commercial_contribution_start_year_2018", "商业养老金开始缴费年份", "calendar year commercial pension contributions began", "calendar year", "Records when contributions began; retain the separate year component and do not infer an exact date without month."),
    ("fn046_w4_2", "pension_commercial_contribution_start_month_2018", "商业养老金开始缴费月份", "calendar month commercial pension contributions began", "calendar month; 0=month not remembered", "Records when contributions began; month 0 means not remembered, not January."),
    ("fn051_w4_1", "pension_commercial_expected_claim_age_2018", "商业养老金预期领取年龄", "age at expected commercial-pension claim", "years of age", "Asked in the 2018 commercial-pension section; preserve as age, not elapsed years."),
    ("fn051_w4_2", "pension_commercial_expected_claim_wait_years_2018", "商业养老金预期领取等待年数", "years until expected commercial-pension claim", "years from interview", "Asked in the 2018 commercial-pension section; preserve as years from interview, not age."),
    ("fn076_w4_a_1", "pension_life_insurance_expected_claim_age_2018", "人寿保险预期领取年龄", "age at expected life-insurance claim", "years of age", "Only asked after FN076_W4=Yes; preserve as age, not elapsed years."),
    ("fn076_w4_a_2", "pension_life_insurance_expected_claim_wait_years_2018", "人寿保险预期领取等待年数", "years until expected life-insurance claim", "years from interview", "Only asked after FN076_W4=Yes; preserve as years from interview, not age."),
    ("fn093_w2_1", "pension_other_plan_expected_claim_age_2018", "其他养老金预期领取年龄", "age at expected other-pension claim", "years of age", "Asked after FN087_W2=No (the selected plan does not require contributions); preserve age as a distinct unit."),
    ("fn093_w2_2", "pension_other_plan_expected_claim_wait_years_2018", "其他养老金预期领取等待年数", "years until expected other-pension claim", "years from interview", "Asked after FN087_W2=No (the selected plan does not require contributions); preserve years from interview as a distinct unit."),
]
for code, concept, display, construct, unit, caveat in timing_specs:
    rec = raw[(raw.wave.astype(str) == "2018") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official catalog row for 2018/{code}; found {len(rec)}")
    rec = rec.iloc[0]
    rows.append({
        "wave": "2018", "code": rec.variable, "concept_id": concept,
        "concept_label": display, "domain": "social protection", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "2018 official questionnaire and codebook component/route verified; candidate only",
        "construct": construct, "scheme_hint": "commercial" if "commercial" in concept else "life_insurance",
        "caveat": caveat + " Unknown/refused/skip values must not be converted to zero; codebook frequencies are not analysis sample sizes.",
        "source_archive": rec.source, "unit": unit,
        "value_label_status": "continuous component; questionnaire range reviewed; codebook frequencies omitted",
        "value_label_source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
        "source_item": "FN046_W4" if code.startswith("fn046") else "FN051_W4" if code.startswith("fn051") else "FN076_W4/FN076_W4_a" if code.startswith("fn076") else "FN087_W2=No; FN093_W2",
        "value_semantics": "expected claim timing; age and elapsed years are distinct measures",
        "official_source": "2018 questionnaire pp. 236-237 (commercial) and pp. 233-234 (life insurance); 2018 codebook field labels",
    })

for wave in ("2013", "2015"):
    for plan_code, plan_slug, plan_label in (("1", "rural_resident", "农村/新农保"), ("2", "residents", "城乡居民"), ("3", "urban_residents", "城镇居民")):
        for component_code, dimension, unit, component_label in (
            ("1", "age", "years of age", "预期领取年龄"),
            ("2", "wait_years", "years from interview", "预期领取等待年数"),
        ):
            code = f"fn065_w2_{component_code}_{plan_code}_"
            rec = raw[(raw.wave.astype(str) == wave) & (raw.variable.astype(str).str.lower() == code)]
            if len(rec) != 1:
                raise SystemExit(f"Expected exactly one official catalog row for {wave}/{code}; found {len(rec)}")
            rec = rec.iloc[0]
            rows.append({
                "wave": wave, "code": rec.variable,
                "concept_id": f"pension_expected_claim_{dimension}_{plan_slug}",
                "concept_label": f"{plan_label}养老金{component_label}",
                "domain": "social protection", "module": rec.module,
                "source_label": rec.variable_label,
                "mapping_status": f"{wave} official questionnaire route and scheme-specific timing component verified; candidate only",
                "construct": f"{dimension.replace('_', ' ')} at expected receipt for {plan_slug.replace('_', ' ')} pension",
                "scheme_hint": "new_rural_social" if plan_slug == "rural_resident" else plan_slug,
                "caveat": "The age-versus-years selector is a separate C metadata field. Keep age and years-from-interview distinct; preserve plan-specific route. Unknown, refusal, and skip are not zero. Codebook frequencies are not analysis sample sizes.",
                "source_archive": rec.source, "unit": unit,
                "value_label_status": "continuous questionnaire timing component; codebook frequencies omitted",
                "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
                "source_item": f"FN065_W2 plan selector {plan_code}; age/year numerical child field",
                "value_semantics": "expected benefit claim timing; scheme-specific numeric age or elapsed years",
                "official_source": f"CHARLS {wave} official questionnaire FN065_W2 and Codebook FN065_W2 plan-specific fields",
            })

# Resident-pension participation/contribution start dates. The waves use
# distinct question routes and field codes, but preserve plan and calendar
# component as explicit dimensions rather than combining year/month blindly.
for wave in ("2013", "2015"):
    stem = "fn061_w2" if wave == "2013" else "fn061_w3"
    for plan_code, plan_slug, plan_label in (("1", "rural_resident", "农村/新农保"), ("2", "residents", "城乡居民"), ("3", "urban_residents", "城镇居民")):
        for component_code, component, unit, component_label in (
            ("1", "year", "calendar year", "开始缴费年份"),
            ("2", "month", "calendar month; 0=month not remembered", "开始缴费月份"),
        ):
            code = f"{stem}_{component_code}_{plan_code}_"
            rec = raw[(raw.wave.astype(str) == wave) & (raw.variable.astype(str).str.lower() == code)]
            if len(rec) != 1:
                raise SystemExit(f"Expected exactly one official catalog row for {wave}/{code}; found {len(rec)}")
            rec = rec.iloc[0]
            rows.append({
                "wave": wave, "code": rec.variable,
                "concept_id": f"pension_resident_plan_contribution_start_{component}_{plan_slug}",
                "concept_label": f"{plan_label}养老金{component_label}",
                "domain": "social protection", "module": rec.module,
                "source_label": rec.variable_label,
                "mapping_status": f"{wave} official questionnaire field, plan label, and date component reviewed; candidate only",
                "construct": f"reported {component} when respondent began paying/participating in {plan_slug} pension",
                "scheme_hint": "new_rural_social" if plan_slug == "rural_resident" else plan_slug,
                "caveat": ("Plan-specific date component; routes differ by wave (2013 asks after the respondent reports contributing; 2015 follows the selected plan/current status section). "
                           "Do not infer a complete date or participation duration from a missing component. Month 0 means not remembered, not January; unknown/refusal/skip are not zero."),
                "source_archive": rec.source, "unit": unit,
                "value_label_status": "official questionnaire/codebook date component reviewed; frequencies omitted",
                "value_label_source": f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
                "source_item": f"{stem.upper()} selected resident pension plan {plan_code}",
                "value_semantics": "calendar contribution/participation start date component; plan and year/month remain separate",
                "official_source": f"CHARLS {wave} official questionnaire and Codebook {stem.upper()} plan-specific fields",
            })

# Wave 1 date of beginning contributions to the selected rural/resident plan.
# This is a distinct event from pension benefit receipt dates above.
for component_code, component, unit, component_label in (
    ("1", "year", "calendar year", "开始缴费年份"),
    ("2", "month", "calendar month; 0=month not remembered", "开始缴费月份"),
):
    code = f"fn010_{component_code}"
    rec = raw[(raw.wave.astype(str) == "2011") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official catalog row for 2011/{code}; found {len(rec)}")
    rec = rec.iloc[0]
    rows.append({
        "wave": "2011", "code": rec.variable,
        "concept_id": f"pension_resident_plan_contribution_start_{component}_rural_resident",
        "concept_label": f"农村/新农保养老金{component_label}",
        "domain": "social protection", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "2011 baseline questionnaire and Codebook field, date component, and route reviewed; candidate only",
        "construct": f"reported {component} when respondent began contributing to selected rural/resident pension plan",
        "scheme_hint": "new_rural_social",
        "caveat": ("2011 FN010 is asked only after FN009=Yes and within the FN002=3/4/5 selected rural/residents/urban-residents plan route; the question wording says rural pension even where the selected plan is residents/urban residents. Preserve the original selected-plan context and do not silently equate the item with all plan-specific 2013/2015 measures. Year and month are separate; month 0 means not remembered, not January; skipped/missing is not No or zero."),
        "source_archive": rec.source, "unit": unit,
        "value_label_status": "2011 baseline questionnaire and Codebook route reviewed; frequencies omitted",
        "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        "source_item": "FN009=Yes; FN002 selected rural/resident/urban-resident plan",
        "value_semantics": "calendar contribution start date component; keep original route and year/month separate",
        "official_source": "CHARLS 2011 baseline questionnaire and Codebook FN009-FN010",
    })

# Exact 2011 baseline pension fields reviewed against the baseline household
# questionnaire and the 2011 Codebook. These are kept wave-specific because
# the routes, pension schemes, and response units differ across sections.
reviewed_2011_specs = {
    "fn015": ("pension_resident_transfer_status_current_recipient", "正在领取居民养老金者是否由其他养老保险转入", "categorical (1=Yes, 2=No)", "resident-pension transfer status among current recipients", "The correct 2011 baseline household questionnaire labels FN015 as the transfer question among current resident-pension recipients (FN002=4); the 2011 Codebook fn015 label/categories agree. FN016 is asked only after Yes. Keep this current-recipient route separate from the enrolled-but-not-necessarily-receiving FN065 route and from 2013 FN063_W2."),
    "fn016": ("resident_pension_transfer_source_current_recipient", "正在领取居民养老金者的转入来源", "categorical (1=Rural pension, 2=Firm basic pension, 3=Other)", "source pension program among current resident-pension recipients", "The correct 2011 baseline household questionnaire labels FN016 as the conditional source question among current resident-pension recipients (FN002=4); the 2011 Codebook fn016 categories agree. Asked only after FN015=Yes. Keep separate from the enrolled-plan FN066/FN064_W2 route; other text is not published."),
    "fn036_1": ("pension_employer_expected_monthly_benefit", "工作单位养老金预期待遇（月金额）", "Yuan/month", "expected monthly employer-plan pension benefit", "The correct 2011 baseline household questionnaire uses FN036_1 for Yuan/month; Codebook fn036_1 is Amount. Conditional on FN034=Yes or FN035=1. Keep separate from final-pay percentage and all social-pension amounts."),
    "fn036_2": ("pension_employer_expected_benefit_final_pay_percentage", "工作单位养老金预期待遇（退休前工资比例）", "percent of final pay", "expected employer-plan benefit as final-pay percentage", "The correct 2011 baseline household questionnaire uses FN036_2 for percent of final pay; Codebook fn036_2 is Percentage. Conditional on FN034=Yes or FN035=1. Do not convert to Yuan or merge with monthly amounts."),
    "fn051_1": ("pension_2011_commercial_premium_start_year", "2011年商业养老保险开始缴费年份", "calendar year", "commercial pension premium start date component", "Commercial pension route only. Keep year separate from month; month 0 means not remembered, and missing/skip is not zero."),
    "fn051_2": ("pension_2011_commercial_premium_start_month", "2011年商业养老保险开始缴费月份", "calendar month; 0=not remembered", "commercial pension premium start date component", "Commercial pension route only. Keep month separate from year; month 0 means not remembered, not January."),
    "fn060_1": ("pension_2011_selected_resident_plan_contribution_start_year", "2011年所选居民类养老保险开始缴费年份", "calendar year", "start date of contributions to selected pension plan", "Asked after FN039 selects rural/residents/urban-residents plan (3/4/5); preserve the selected plan context and do not equate across schemes or later waves. Keep year and month separate."),
    "fn060_2": ("pension_2011_selected_resident_plan_contribution_start_month", "2011年所选居民类养老保险开始缴费月份", "calendar month; 0=not remembered", "start date of contributions to selected pension plan", "Asked after FN039 selects rural/residents/urban-residents plan (3/4/5); preserve the selected plan context and do not equate across schemes or later waves. Month 0 means not remembered, not January."),
    "fn065": ("pension_resident_transfer_status", "已参保居民养老金是否由其他养老保险转入", "categorical (1=Yes, 2=No)", "resident-pension transfer status among enrolled participants", "The correct 2011 baseline questionnaire routes FN065 to enrolled residents-pension participants (FN039=4); FN066 follows only after Yes. This matches the 2013 FN063_W2 enrolled-plan question; keep separate from 2011 FN015 current-recipient route."),
    "fn066": ("resident_pension_transfer_source", "已参保居民养老金转入来源", "categorical (1=Rural pension, 2=Firm basic pension, 3=Other)", "transfer source among enrolled resident-pension participants", "The correct 2011 baseline questionnaire routes FN066 to FN039=4 enrolled residents-pension participants, after FN065=Yes; response categories match 2013 FN064_W2. Keep separate from the 2011 current-recipient FN016 route; other text is not published."),
}
for code, (concept, display, unit, construct, caveat) in reviewed_2011_specs.items():
    rec = raw[(raw.wave.astype(str) == "2011") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official 2011 catalog row for {code}; found {len(rec)}")
    rec = rec.iloc[0]
    rows.append({
        "wave": "2011", "code": rec.variable, "concept_id": concept,
        "concept_label": display, "domain": "social protection", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "2011 baseline questionnaire and Codebook exact field identity, route, and response semantics reviewed; candidate only",
        "construct": construct, "scheme_hint": ("commercial" if code.startswith("fn051") else "selected_resident_plan" if code.startswith("fn060") else "residents" if code in {"fn015", "fn016", "fn065", "fn066"} else "employer_pension"),
        "caveat": caveat + " Official source frequencies are metadata only, not analysis sample sizes; unknown/refused/skip values must not be converted to zero.",
        "source_archive": rec.source, "unit": unit,
        "value_label_status": "official questionnaire and Codebook field identity/unit reviewed; frequencies omitted",
        "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        "value_labels": "1=Yes; 2=No" if code in {"fn015", "fn065"} else "1=Rural pension; 2=Firm basic pension; 3=Other" if code in {"fn016", "fn066"} else "", "source_item": f"2011 baseline Work, Retirement and Pension questionnaire FN{code[2:].upper()}; exact source field verified",
        "value_semantics": construct,
        "official_source": "CHARLS 2011 baseline household questionnaire and Codebook, Work, Retirement and Pension section",
    })

# Exact 2013 status counterpart to 2011 FN065/fn065. The 2013 questionnaire
# uses FN063_W2 and the Codebook/release catalog uses fn063_w2_2_.
rec = raw[(raw.wave.astype(str) == "2013") & (raw.variable.astype(str).str.lower() == "fn063_w2_2_")]
if len(rec) != 1:
    raise SystemExit(f"Expected exactly one official 2013 catalog row for fn063_w2_2_; found {len(rec)}")
rec = rec.iloc[0]
rows.append({
    "wave": "2013", "code": rec.variable, "concept_id": "pension_resident_transfer_status",
    "concept_label": "城乡居民养老金是否由其他养老保险转入", "domain": "social protection",
    "module": rec.module, "source_label": rec.variable_label,
    "mapping_status": "2013 questionnaire and Codebook identify FN063_W2 transfer status with same response options and enrolled-plan route as 2011 FN065; candidate only",
    "construct": "resident-pension transfer status", "scheme_hint": "residents",
    "caveat": "Asked only when the selected residents-pension route is present. The 2013 code field fn063_w2_2_ represents this enrolled-plan status item; FN064_W2 source is separate and asked only after Yes. Keep separate from 2011 FN015 current-recipient route and do not infer a transfer from missing/skip values.",
    "source_archive": rec.source, "unit": "categorical (1=Yes, 2=No)",
    "value_label_status": "official questionnaire and Codebook response categories reviewed; frequencies omitted",
    "value_label_source": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "value_labels": "1=Yes; 2=No", "source_item": "2013 FN063_W2 residents-pension transfer status among enrolled participants",
    "value_semantics": "resident-pension transfer status among enrolled participants", "official_source": "CHARLS 2013 Questionnaire FN063_W2 and Codebook fn063_w2_2_",
})

# 2013 pension source/work-unit context fields reviewed against the wave-specific
# questionnaire and Codebook. These remain distinct categorical candidates;
# province and free-text fields are metadata and are never published as values.
reviewed_2013_specs = {
    "fn007_w2_1_": ("pension_source_work_unit_reference", "养老金来源对应的单位关系", "categorical (1=current work unit, 2=last work unit, 3=retirement-processing unit, 4=none)", "pension source work-unit reference", "Government/institution route selected by FN006_W2=1. This records which work-unit reference supplied the pension; conditional route only, not a respondent address."),
    "fn007_w2_2_": ("pension_source_work_unit_reference", "养老金来源对应的单位关系", "categorical (1=current work unit, 2=last work unit, 3=retirement-processing unit, 4=none)", "pension source work-unit reference", "Firm-basic-pension route selected by FN006_W2=2. Keep the pension scheme context; conditional route only."),
    "fn009_w2_1_": ("pension_source_work_unit_employer_type", "养老金来源单位类型", "categorical (1=government, 2=institution, 3=NGO, 4=firm, 5=individual, 6=other)", "employer type of pension source work unit", "Asked only if FN007_W2=4 (none of the preloaded work units); government/institution pension branch. Preserve the conditional route."),
    "fn009_w2_2_": ("pension_source_work_unit_employer_type", "养老金来源单位类型", "categorical (1=government, 2=institution, 3=NGO, 4=firm, 5=individual, 6=other)", "employer type of pension source work unit", "Asked only if FN007_W2=4 (none of the preloaded work units); firm pension branch. Preserve the conditional route."),
    "fn010_w2_1_": ("pension_source_work_unit_geographic_scope", "养老金来源单位与常住地的空间关系", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of pension source work unit", "Government/institution pension branch, asked only for FN007_W2=4. Map only the coarse response category; do not expose or geocode any linked location text."),
    "fn010_w2_2_": ("pension_source_work_unit_geographic_scope", "养老金来源单位与常住地的空间关系", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of pension source work unit", "Firm pension branch, asked only for FN007_W2=4. Map only the coarse response category; do not expose or geocode any linked location text."),
    "fn031_w2": ("firm_supplementary_pension_participation_geographic_scope", "企业补充养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of firm supplementary pension participation", "Asked only for participation/receipt in the firm supplementary pension (FN030_W2 not No); detailed location fields are not included in the public atlas."),
    "fn044_w2": ("commercial_pension_participation_geographic_scope", "商业养老保险参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of commercial pension participation", "Conditional on the commercial-pension route; preserve current-residence reference and do not expose linked location text."),
    "fn059_w2_1_": ("social_pension_participation_geographic_scope", "社会养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of social pension participation", "Rural pension field; plan-specific response. Do not pool with other plan rows without plan context."),
    "fn059_w2_2_": ("social_pension_participation_geographic_scope", "社会养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of social pension participation", "Residents' pension field; plan-specific response. Do not pool with other plan rows without plan context."),
    "fn059_w2_3_": ("social_pension_participation_geographic_scope", "社会养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of social pension participation", "Urban-residents pension field; plan-specific response. Do not pool with other plan rows without plan context."),
}
labels_2013 = {
    "fn007_w2_1_": "1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
    "fn007_w2_2_": "1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
    "fn009_w2_1_": "1=Government; 2=Institutions; 3=NGO; 4=Firm; 5=Individual; 6=Other",
    "fn009_w2_2_": "1=Government; 2=Institutions; 3=NGO; 4=Firm; 5=Individual; 6=Other",
    "fn010_w2_1_": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn010_w2_2_": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn031_w2": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn044_w2": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn059_w2_1_": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn059_w2_2_": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn059_w2_3_": "1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
}
for code, (concept, display, unit, construct, caveat) in reviewed_2013_specs.items():
    rec = raw[(raw.wave.astype(str) == "2013") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official 2013 catalog row for {code}; found {len(rec)}")
    rec = rec.iloc[0]
    rows.append({
        "wave": "2013", "code": rec.variable, "concept_id": concept,
        "concept_label": display, "domain": "social protection", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "2013 questionnaire and Codebook item, response categories, and conditional route reviewed; candidate only",
        "construct": construct, "scheme_hint": "firm_basic" if "firm" in code or code.endswith("_2_") else "government_institution_or_plan_specific",
        "caveat": caveat + " Codebook frequencies are not sample sizes for analysis; missing/skip values are not No or zero.",
        "source_archive": rec.source, "unit": unit,
        "value_label_status": "official 2013 questionnaire and Codebook categories reviewed; frequencies omitted",
        "value_label_source": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
        "value_labels": labels_2013[code], "source_item": f"2013 Work, Retirement and Pension questionnaire {code}",
        "value_semantics": construct, "official_source": f"CHARLS 2013 Questionnaire/Codebook {code}",
    })

# 2015 residual pension fields crosswalked only where the Wave 3 questionnaire
# and Codebook confirm the route and construct. 2015 firm-transfer variables
# remain separate from the broader 2011/2013 resident-pension transfer concept.
reviewed_2015_specs = {
    "fn003_w2_1_2_": ("pension_benefit_start_date_components", "事业单位养老金开始领取年份", "calendar year", "reported pension benefit start date component", "2015 FN002_W2 plan selection identifies the government-affiliated institution pension route. Keep year separate from month and do not infer missing dates."),
    "fn003_w2_2_2_": ("pension_benefit_start_date_components", "事业单位养老金开始领取月份", "calendar month; 0=not remembered", "reported pension benefit start date component", "2015 FN002_W2 plan selection identifies the government-affiliated institution pension route. Month 0 means not remembered, not January; keep separate from year."),
    "fn007_w2_1_": ("pension_source_work_unit_reference", "养老金来源对应的单位关系", "categorical (1=current work unit, 2=last work unit, 3=retirement-processing unit, 4=none)", "pension source work-unit reference", "Government/institution pension route selected by FN006_W2=1. Conditional route only."),
    "fn007_w2_2_": ("pension_source_work_unit_reference", "养老金来源对应的单位关系", "categorical (1=current work unit, 2=last work unit, 3=retirement-processing unit, 4=none)", "pension source work-unit reference", "Firm pension route selected by FN006_W2=2. Preserve the pension scheme context."),
    "fn009_w2_1_": ("pension_source_work_unit_employer_type", "养老金来源单位类型", "categorical (1=government, 2=institution, 3=NGO, 4=firm, 5=individual, 6=other)", "employer type of pension source work unit", "Asked only if FN007_W2=4; government/institution route."),
    "fn009_w2_2_": ("pension_source_work_unit_employer_type", "养老金来源单位类型", "categorical (1=government, 2=institution, 3=NGO, 4=firm, 5=individual, 6=other)", "employer type of pension source work unit", "Asked only if FN007_W2=4; firm route."),
    "fn010_w2_1_": ("pension_source_work_unit_geographic_scope", "养老金来源单位与常住地的空间关系", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of pension source work unit", "Government/institution branch, asked only after FN007_W2=4. Keep only the coarse category, not location text."),
    "fn010_w2_2_": ("pension_source_work_unit_geographic_scope", "养老金来源单位与常住地的空间关系", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of pension source work unit", "Firm branch, asked only after FN007_W2=4. Keep only the coarse category, not location text."),
    "fn044_w2": ("commercial_pension_participation_geographic_scope", "商业养老保险参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of commercial pension participation", "Conditional on the commercial-pension participation/receipt route; no linked location text is included."),
    "fn059_w2_1_": ("social_pension_participation_geographic_scope", "社会养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of social pension participation", "New Rural pension plan; preserve plan context."),
    "fn059_w2_2_": ("social_pension_participation_geographic_scope", "社会养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of social pension participation", "Residents' pension plan; preserve plan context."),
    "fn059_w2_3_": ("social_pension_participation_geographic_scope", "社会养老金参保地点范围", "categorical (1=same as permanent address, 2=another village in same county, 3=other, 4=abroad)", "coarse geographic scope of social pension participation", "Urban residents' pension plan; preserve plan context."),
    "fn063_w2_2_": ("pension_resident_transfer_from_firm_status_2015", "居民养老金是否由企业养老金转入（2015）", "categorical (1=Yes, 2=No)", "residents-pension transfer from firm-pension status", "2015 Wave 3 only. Asked on the residents-pension route and specifically asks whether the pension came from the firm pension. Do not merge with 2011/2013 broader other-pension transfer status."),
    "fn063_w2_3_": ("pension_resident_transfer_from_firm_status_2015", "居民养老金是否由企业养老金转入（2015）", "categorical (1=Yes, 2=No)", "residents-pension transfer from firm-pension status", "2015 Wave 3 only. Urban-residents pension route; preserve plan context and do not merge with 2011/2013 broader transfer status."),
    "fn064_w2_2_": ("pension_resident_transfer_source_2015", "居民养老金转入来源（2015）", "categorical; Codebook lists Firm pension", "source pension program for transferred residents' pension", "Conditional on the residents-pension transfer-from-firm status. Keep this 2015 firm-only route separate from broader source categories in 2011/2013."),
    "fn064_w2_3_": ("pension_resident_transfer_source_2015", "居民养老金转入来源（2015）", "categorical; Codebook lists Firm pension", "source pension program for transferred residents' pension", "Conditional on the urban-residents pension transfer-from-firm status. Keep this plan-specific route."),
    "fn064_w2_1_2_": ("pension_years_since_firm_pension_transfer_2015", "居民养老金从企业养老金转入年数（2015）", "string; nominal duration in years, parsing unresolved", "reported years since transfer from firm pension", "2015 Wave 3 only, conditional on the plan-specific firm-pension transfer route. Controlled local QA confirms the reported unit is years by official field title and route matches, but responses are stored as strings and one plan field contains nonnumeric text; preserve raw strings and do not coerce until official release encoding is clarified."),
    "fn064_w2_1_3_": ("pension_years_since_firm_pension_transfer_2015", "城镇居民养老金从企业养老金转入年数（2015）", "string; nominal duration in years, parsing unresolved", "reported years since transfer from firm pension", "2015 Wave 3 only, conditional on the plan-specific firm-pension transfer route. Controlled local QA confirms the reported unit is years by official field title and route matches, but responses are stored as strings and one plan field contains nonnumeric text; preserve raw strings and do not coerce until official release encoding is clarified."),
    "fn057_w3_1_1_": ("pension_age_status_at_scheme_start_2015", "居民类养老金初次开展时的领取年龄状态（2015）", "categorical (1=age-qualified and began receiving; 2=age-qualified but did not receive; 3=not yet age-qualified)", "age eligibility and receipt status when the scheme began", "New Rural pension route, conditional on FN057_W3_0 selection. Retain all three nominal states; do not reduce to a binary age indicator."),
    "fn057_w3_1_2_": ("pension_age_status_at_scheme_start_2015", "居民类养老金初次开展时的领取年龄状态（2015）", "categorical (1=age-qualified and began receiving; 2=age-qualified but did not receive; 3=not yet age-qualified)", "age eligibility and receipt status when the scheme began", "Residents' pension route, conditional on FN057_W3_0 selection. Retain all three nominal states."),
    "fn057_w3_1_3_": ("pension_age_status_at_scheme_start_2015", "居民类养老金初次开展时的领取年龄状态（2015）", "categorical (1=age-qualified and began receiving; 2=age-qualified but did not receive; 3=not yet age-qualified)", "age eligibility and receipt status when the scheme began", "Urban residents' pension route, conditional on FN057_W3_0 selection. Retain all three nominal states."),
    "fn057_w3_2_1_": ("pension_children_enrollment_required_for_nonpayment_2015", "居民类养老金初次开展时是否因子女参保而可免缴（2015）", "categorical (1=Yes, 2=No)", "whether children's enrollment was required for respondent to receive without personal payment", "New Rural pension route, conditional on the FN057_W3_0 and prior eligibility route; do not equate to actual child payment or a current contribution."),
    "fn057_w3_2_2_": ("pension_children_enrollment_required_for_nonpayment_2015", "居民类养老金初次开展时是否因子女参保而可免缴（2015）", "categorical (1=Yes, 2=No)", "whether children's enrollment was required for respondent to receive without personal payment", "Residents' pension route; preserve plan context and routed denominator."),
    "fn057_w3_2_3_": ("pension_children_enrollment_required_for_nonpayment_2015", "居民类养老金初次开展时是否因子女参保而可免缴（2015）", "categorical (1=Yes, 2=No)", "whether children's enrollment was required for respondent to receive without personal payment", "Urban residents' pension route; preserve plan context and routed denominator."),
    "fn057_w3_4_1_": ("pension_current_claim_age_eligibility_2015", "当前是否达到居民类养老金领取年龄（2015，待代码本核对）", "categorical (1=Yes, 2=No)", "current age eligibility for selected social pension", "Questionnaire asks whether current official-ID age has reached the plan's claim age; the matching Codebook title describes a different children-payment route. Retain as blocked pending official release field-title reconciliation."),
    "fn057_w3_4_2_": ("pension_current_claim_age_eligibility_2015", "当前是否达到居民类养老金领取年龄（2015，待代码本核对）", "categorical (1=Yes, 2=No)", "current age eligibility for selected social pension", "Questionnaire asks whether current official-ID age has reached the plan's claim age; Codebook field title conflicts. Retain blocked pending reconciliation."),
    "fn057_w3_4_3_": ("pension_current_claim_age_eligibility_2015", "当前是否达到居民类养老金领取年龄（2015，待代码本核对）", "categorical (1=Yes, 2=No)", "current age eligibility for selected social pension", "Questionnaire asks whether current official-ID age has reached the plan's claim age; Codebook field title conflicts. Retain blocked pending reconciliation."),
    "fn068_w3_1_": ("pension_age_eligible_at_scheme_start_2015", "居民类养老金初次开展时是否达到领取年龄并直接领取（2015）", "categorical (1=Yes, 2=No)", "age-qualified at initial scheme implementation and receiving without personal payment", "New Rural pension route. The questionnaire excludes cases where children paid; preserve as a historical scheme-entry condition."),
    "fn068_w3_2_": ("pension_age_eligible_at_scheme_start_2015", "居民类养老金初次开展时是否达到领取年龄并直接领取（2015）", "categorical (1=Yes, 2=No)", "age-qualified at initial scheme implementation and receiving without personal payment", "Residents' pension route. The questionnaire excludes cases where children paid; preserve plan context."),
    "fn068_w3_3_": ("pension_age_eligible_at_scheme_start_2015", "居民类养老金初次开展时是否达到领取年龄并直接领取（2015）", "categorical (1=Yes, 2=No)", "age-qualified at initial scheme implementation and receiving without personal payment", "Urban residents' pension route. The questionnaire excludes cases where children paid; preserve plan context."),
    "fn068_w3_1_1_": ("pension_children_enrollment_required_for_nonpayment_2015", "居民类养老金初次开展时是否因子女参保而可免缴（2015）", "categorical (1=Yes, 2=No)", "whether local implementation required children to enroll before respondent could receive without personal payment", "New Rural pension route. This is a historical policy/eligibility condition, not a child's identity or an actual payment amount."),
    "fn068_w3_1_2_": ("pension_children_enrollment_required_for_nonpayment_2015", "居民类养老金初次开展时是否因子女参保而可免缴（2015）", "categorical (1=Yes, 2=No)", "whether local implementation required children to enroll before respondent could receive without personal payment", "Residents' pension route; preserve plan context."),
    "fn068_w3_1_3_": ("pension_children_enrollment_required_for_nonpayment_2015", "居民类养老金初次开展时是否因子女参保而可免缴（2015）", "categorical (1=Yes, 2=No)", "whether local implementation required children to enroll before respondent could receive without personal payment", "Urban residents' pension route; preserve plan context."),
}
labels_2015 = {
    "fn007_w2_1_":"1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None", "fn007_w2_2_":"1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
    "fn009_w2_1_":"1=Government; 2=Institutions; 3=NGO; 4=Firm; 5=Individual; 6=Other", "fn009_w2_2_":"1=Government; 2=Institutions; 3=NGO; 4=Firm; 5=Individual; 6=Other",
    "fn010_w2_1_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad", "fn010_w2_2_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn044_w2":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn059_w2_1_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad", "fn059_w2_2_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad", "fn059_w2_3_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
    "fn063_w2_2_":"1=Yes; 2=No", "fn063_w2_3_":"1=Yes; 2=No", "fn064_w2_2_":"1=Firm pension", "fn064_w2_3_":"1=Firm pension",
    "fn057_w3_1_1_":"1=Age-qualified and receiving; 2=Age-qualified but not receiving; 3=Not yet age-qualified", "fn057_w3_1_2_":"1=Age-qualified and receiving; 2=Age-qualified but not receiving; 3=Not yet age-qualified", "fn057_w3_1_3_":"1=Age-qualified and receiving; 2=Age-qualified but not receiving; 3=Not yet age-qualified",
    "fn057_w3_2_1_":"1=Yes; 2=No", "fn057_w3_2_2_":"1=Yes; 2=No", "fn057_w3_2_3_":"1=Yes; 2=No", "fn057_w3_4_1_":"1=Yes; 2=No", "fn057_w3_4_2_":"1=Yes; 2=No", "fn057_w3_4_3_":"1=Yes; 2=No",
    "fn068_w3_1_":"1=Yes; 2=No", "fn068_w3_2_":"1=Yes; 2=No", "fn068_w3_3_":"1=Yes; 2=No", "fn068_w3_1_1_":"1=Yes; 2=No", "fn068_w3_1_2_":"1=Yes; 2=No", "fn068_w3_1_3_":"1=Yes; 2=No",
}
for code, (concept, display, unit, construct, caveat) in reviewed_2015_specs.items():
    rec=raw[(raw.wave.astype(str)=="2015") & (raw.variable.astype(str).str.lower()==code)]
    if len(rec)!=1: raise SystemExit(f"Expected exactly one official 2015 catalog row for {code}; found {len(rec)}")
    rec=rec.iloc[0]
    rows.append({"wave":"2015","code":rec.variable,"concept_id":concept,"concept_label":display,"domain":"social protection","module":rec.module,"source_label":rec.variable_label,"mapping_status":"2015 Wave 3 questionnaire and Codebook exact item/route reviewed; candidate only","construct":construct,"scheme_hint":"2015_wave3_plan_specific","caveat":caveat+" Preserve structural skips; do not infer No or zero. Codebook frequencies are not analysis sample sizes.","source_archive":rec.source,"unit":unit,"value_label_status":"official questionnaire and Codebook categories reviewed; frequencies omitted","value_label_source":"sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt","value_labels":labels_2015.get(code,""),"source_item":f"2015 Wave 3 questionnaire {code}","value_semantics":construct,"official_source":"CHARLS 2015 Wave 3 Questionnaire and Codebook"})

# The release contains string interval-bound fields for three pension amount
# questions. Keep them searchable as blocked components, never as numeric values.
interval_specs_2013 = {
    "fn036_w2_bracketbracket_min": ("pension_firm_supplementary_db_expected_benefit_bracket_bounds", "企业补充养老金DB计划预期待遇区间边界", "FN036_W2 DB-plan route confirmed in controlled local QA, but Min/Max endpoints are not consistently paired and bracket rows have no FN036_W2 payment-form selector; retain as unresolved string bounds."),
    "fn036_w2_bracketbracket_max": ("pension_firm_supplementary_db_expected_benefit_bracket_bounds", "企业补充养老金DB计划预期待遇区间边界", "FN036_W2 DB-plan route confirmed in controlled local QA, but Min/Max endpoints are not consistently paired and bracket rows have no FN036_W2 payment-form selector; retain as unresolved string bounds."),
    "fn077_w2_bracketbracket_min": ("pension_new_rural_current_benefit_bracket_bounds", "新农保当前月待遇区间边界", "FN077_W2 route and explicit Yuan/month unit confirmed in the questionnaire and controlled local QA; Min/Max endpoints are not consistently paired, so retain as a bound rather than a respondent's exact monthly amount."),
    "fn077_w2_bracketbracket_max": ("pension_new_rural_current_benefit_bracket_bounds", "新农保当前月待遇区间边界", "FN077_W2 route and explicit Yuan/month unit confirmed in the questionnaire and controlled local QA; Min/Max endpoints are not consistently paired, so retain as a bound rather than a respondent's exact monthly amount."),
    "fn094_w2_bracketbracket_min": ("pension_other_plan_expected_benefit_bracket_bounds", "其他养老金预期待遇区间边界", "FN094_W2 eligible route confirmed in controlled local QA, but Min/Max endpoints are not consistently paired and bracket rows have no FN094_W2 monthly/lump-sum selector; retain as unresolved string bounds."),
    "fn094_w2_bracketbracket_max": ("pension_other_plan_expected_benefit_bracket_bounds", "其他养老金预期待遇区间边界", "FN094_W2 eligible route confirmed in controlled local QA, but Min/Max endpoints are not consistently paired and bracket rows have no FN094_W2 monthly/lump-sum selector; retain as unresolved string bounds."),
}
for code, (concept, display, caveat) in interval_specs_2013.items():
    rec = raw[(raw.wave.astype(str) == "2013") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official 2013 catalog row for {code}; found {len(rec)}")
    rec = rec.iloc[0]
    rows.append({"wave":"2013", "code":rec.variable, "concept_id":concept, "concept_label":display, "domain":"social protection", "module":rec.module, "source_label":rec.variable_label, "mapping_status":"DO NOT ANALYZE as a numeric amount; Codebook identifies a string interval bound, exact response interpretation unresolved", "construct":"censored/interval pension benefit response bound", "scheme_hint":"pension_amount", "caveat":caveat + " Do not assign a midpoint, convert to a numeric benefit, or treat as an independent exposure; Codebook frequencies are not analytic sample sizes.", "source_archive":rec.source, "unit":"string interval bound; unit/sequence unresolved", "value_label_status":"Codebook identifies a string bound; frequencies omitted", "value_label_source":"sources_official/CHARLS_2013_Codebook_extracted.txt", "value_labels":"", "source_item":code, "value_semantics":"interval bound only; not an exact pension amount", "official_source":f"CHARLS 2013 Codebook {code}"})

# Unfolding brackets are substantive response components, but they are not
# numeric benefit amounts. Preserve each Yuan threshold and category label,
# group by the distinct routed pension question, and block point-value use.
bracket_specs = {
    "fn064_1": ("pension_resident_expected_benefit_bracket_sequence", "城乡居民养老金预期待遇展开区间回答", "1=Less than 250 yuan; 2=About 250 yuan; 3=More than 250 yuan"),
    "fn064_2": ("pension_resident_expected_benefit_bracket_sequence", "城乡居民养老金预期待遇展开区间回答", "1=Less than 500 yuan; 2=About 500 yuan; 3=More than 500 yuan"),
    "fn064_3": ("pension_resident_expected_benefit_bracket_sequence", "城乡居民养老金预期待遇展开区间回答", "1=Less than 1,000 yuan; 2=About 1,000 yuan; 3=More than 1,000 yuan"),
    "fn064_4": ("pension_resident_expected_benefit_bracket_sequence", "城乡居民养老金预期待遇展开区间回答", "1=Less than 2,000 yuan (only category listed in Codebook)"),
    "fn070_1": ("pension_other_plan_expected_benefit_bracket_sequence", "其他养老金预期待遇展开区间回答", "2=About 250 yuan (only category listed in Codebook)"),
    "fn070_2": ("pension_other_plan_expected_benefit_bracket_sequence", "其他养老金预期待遇展开区间回答", "1=Less than 500 yuan; 3=More than 500 yuan"),
    "fn070_3": ("pension_other_plan_expected_benefit_bracket_sequence", "其他养老金预期待遇展开区间回答", "1=Less than 1,000 yuan; 3=More than 1,000 yuan"),
    "fn070_4": ("pension_other_plan_expected_benefit_bracket_sequence", "其他养老金预期待遇展开区间回答", "1=Less than 2,000 yuan; 3=More than 2,000 yuan"),
}
for code, (concept, display, value_labels) in bracket_specs.items():
    rec = raw[(raw.wave.astype(str) == "2011") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official 2011 catalog row for {code}; found {len(rec)}")
    rec = rec.iloc[0]
    item = "FN063/FN064" if code.startswith("fn064") else "FN069/FN070"
    rows.append({
        "wave": "2011", "code": rec.variable, "concept_id": concept,
        "concept_label": display, "domain": "social protection", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "DO NOT ANALYZE as a numeric amount; local QA found route or payment-form selectors unresolved; preserve threshold-specific response categories",
        "construct": f"threshold-specific unfolding-bracket response sequence for {item}",
        "scheme_hint": "resident_pension" if code.startswith("fn064") else "other_pension",
        "caveat": f"Part of the conditional {item} expected-benefit route. This field is one threshold response within a multi-field sequence, not a Yuan value or independent amount. Controlled local QA found incomplete response-component patterns; FN064 records include route mismatches and do not consistently retain the FN063 selector, while FN070 bracket rows lack the FN069 selector. Preserve the exact threshold and category; do not assign a midpoint, combine thresholds into a point estimate, annualize, or assume skipped fields are zero. Payment form/period and response sequence remain unresolved.",
        "source_archive": rec.source, "unit": "categorical response at Yuan threshold; amount form/period unresolved",
        "value_label_status": "Codebook category wording transcribed; frequencies omitted; only Codebook-listed categories are shown",
        "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        "value_labels": value_labels, "source_item": item,
        "value_semantics": "threshold-specific ordinal response component; not a monetary value",
        "official_source": f"CHARLS 2011 baseline questionnaire {item} and Codebook {code}",
    })

# Wave 4 pension residual fields reviewed against the 2018 questionnaire and
# Codebook. Broad location categories are retained as E; detailed address
# children and response-format/bracket fields are classified as C elsewhere.
location_labels_2018 = "1=Same as current residence; 2=Other township/village/neighborhood in current-residence county/city/district; 3=Other place; 997=Don't know"
reviewed_2018_specs = {
    "fn070_w4": ("pension_benefit_receipt_location_relative_to_residence", "养老金领取地点与当前居住地的粗略关系", "categorical", "coarse location category for receipt of named pension benefit", "Current-residence-based broad category only; keep pension-plan route and the 2018 category scheme. The province/county/township text fields are excluded from the public association layer."),
    **{f"fn006_w4_{i}_": ("pension_benefit_receipt_location_relative_to_residence", "养老金领取地点与当前居住地的粗略关系", "categorical", "coarse location category for receipt of named pension benefit", f"Loop {i} of the formal-pension section; preserve the selected plan identity and loop-specific denominator. This is a broad response category, not an address text value.") for i in range(1, 5)},
    **{f"fn007_w4_{i}_": ("pension_program_participation_location_relative_to_residence", "养老金/保险参保地点与当前居住地的粗略关系", "categorical", "coarse location category for enrollment or contribution to named plan", f"Loop {i} of the formal-pension section; preserve the selected plan identity and loop-specific denominator. This is a broad response category, not an address text value.") for i in range(1, 5)},
    "fn080_w4": ("pension_benefit_receipt_location_relative_to_residence", "养老金领取地点与当前居住地的粗略关系", "categorical", "coarse location category for receipt of named pension benefit", "Land-expropriated-farmer pension route; preserve the named-plan context. Detailed address children are excluded."),
    "fn042_w4": ("pension_benefit_receipt_location_relative_to_residence", "养老金领取地点与当前居住地的粗略关系", "categorical", "coarse location category for receipt of named pension benefit", "Named employee-pension route; preserve plan context. Detailed address children are excluded."),
    "fn096_w4": ("pension_benefit_receipt_location_relative_to_residence", "养老金领取地点与当前居住地的粗略关系", "categorical", "coarse location category for receipt of named pension benefit", "Other-pension route; preserve route and do not expose linked location text."),
    "fn078_w4": ("pension_benefit_receipt_location_relative_to_residence", "养老金领取地点与当前居住地的粗略关系", "categorical", "coarse location category for receipt of named pension benefit", "Pension-plan-specific receipt route; preserve plan context and do not expose linked location text."),
    "fn056_w4": ("life_insurance_benefit_receipt_location_relative_to_residence_2018", "人寿保险赔付领取地点与当前居住地的粗略关系（2018）", "categorical", "coarse location category for receipt of a life-insurance payout", "Life-insurance payout route; keep separate from pension receipt location and exclude detailed address children."),
    "fn074_w4": ("pension_program_participation_location_relative_to_residence", "养老金/保险参保地点与当前居住地的粗略关系", "categorical", "coarse location category for enrollment or contribution to named plan", "Life-insurance participation route; preserve plan type and exclude detailed address children."),
    "fn079_w4": ("pension_program_participation_location_relative_to_residence", "养老金/保险参保地点与当前居住地的粗略关系", "categorical", "coarse location category for enrollment or contribution to named plan", "Land-expropriated-farmer pension route; preserve plan context and exclude detailed address children."),
    "fn044_w2": ("pension_program_participation_location_relative_to_residence", "养老金/保险参保地点与当前居住地的粗略关系", "categorical", "coarse location category for enrollment or contribution to named plan", "Commercial/other pension route; preserve the 2018 current-residence reference and do not substitute permanent-address categories from earlier waves."),
    "fn034_w4": ("pension_program_participation_location_relative_to_residence", "养老金/保险参保地点与当前居住地的粗略关系", "categorical", "coarse location category for enrollment or contribution to named plan", "Named employee/supplementary-plan contribution route; preserve plan context and exclude detailed address children."),
    "fn059_w2": ("pension_program_participation_location_relative_to_residence", "养老金/保险参保地点与当前居住地的粗略关系", "categorical", "coarse location category for enrollment or contribution to named plan", "Residents' pension enrollment route; preserve plan context and exclude detailed address children."),
    "fn033_w2": ("pension_enrollment_duration_years_2018", "参加当前养老金计划年数（2018）", "years", "self-reported years enrolled in named pension plan", "2018 questionnaire explicitly includes years enrolled through different employers in the same pension program; retain the 2018-specific definition and plan route."),
    "fn058_w4": ("pension_resident_plan_participation_or_receipt_status_2018", "城乡/新农/城镇居民养老保险参保或领取状态（2018）", "categorical (1=Yes, 2=No)", "screening status for participation, expected receipt, or current receipt in the social-pension plan family", "This is an any-route screening item, not current receipt alone. Preserve its denominator and do not interpret skipped downstream items as No."),
    "fn058_w4_a": ("pension_resident_plan_type_2018", "居民类养老保险计划类型（2018）", "categorical multi-option", "selected residents/new-rural/urban-residents pension program type", "Asked after the social-pension family screen; retain the unknown-type category and plan-specific route."),
    "fn066_w2_1": ("pension_formal_plan_expected_monthly_benefit_2018", "职工/机关事业单位养老金预期月待遇（2018）", "Yuan/month", "expected monthly pension benefit from selected formal pension plan", "Conditional on the selected named formal plan and expectation route; retain -1/unknown as missing and do not impute skipped payment forms."),
    "fn066_w2_2": ("pension_formal_plan_expected_lump_sum_benefit_2018", "职工/机关事业单位养老金预期一次性待遇（2018）", "Yuan lump sum", "expected lump-sum pension benefit from selected formal pension plan", "Conditional on the selected named formal plan and lump-sum route; keep separate from monthly benefit and preserve -1/unknown as missing."),
    "fn056_w2_8": ("life_insurance_claim_amount", "人寿保险已领取赔付金额", "CNY", "reported life-insurance payout amount", "Life-insurance claim route. Retain exact source unit and route; -1/unknown is not a benefit amount."),
}
for code, (concept, display, unit, construct, caveat) in reviewed_2018_specs.items():
    rec = raw[(raw.wave.astype(str) == "2018") & (raw.variable.astype(str).str.lower() == code)]
    if len(rec) != 1:
        raise SystemExit(f"Expected exactly one official 2018 catalog row for {code}; found {len(rec)}")
    rec = rec.iloc[0]
    is_location = code in {"fn070_w4", "fn080_w4", "fn042_w4", "fn096_w4", "fn078_w4", "fn056_w4", "fn074_w4", "fn079_w4", "fn044_w2", "fn034_w4", "fn059_w2"} or code.startswith(("fn006_w4_", "fn007_w4_"))
    rows.append({"wave":"2018", "code":rec.variable, "concept_id":concept, "concept_label":display, "domain":"social protection", "module":rec.module, "source_label":rec.variable_label, "mapping_status":"2018 Wave 4 questionnaire and Codebook item, unit/categories, and route reviewed; candidate only", "construct":construct, "scheme_hint":"2018_wave4_plan_specific", "caveat":caveat + " Codebook frequencies are not analysis sample sizes; structural skips are not No or zero.", "source_archive":rec.source, "unit":unit, "value_label_status":"official 2018 questionnaire and Codebook categories reviewed; frequencies omitted", "value_label_source":"sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt", "value_labels":location_labels_2018 if is_location else ("1=Yes; 2=No" if code == "fn058_w4" else "1=Urban and Rural Resident Pension; 2=New Rural Resident Pension; 3=Urban Resident Pension; 4=Don't know the type" if code == "fn058_w4_a" else ""), "source_item":f"2018 Wave 4 questionnaire {code}", "value_semantics":construct, "official_source":"CHARLS 2018 Questionnaire and Codebook"})

# Interval/unfolding bracket columns belong to a parent response, not to an
# independent exposure. Link them only when the parent amount field has an
# explicit mapping above; keep unmatched brackets for the audit instead of
# guessing across neighboring questions.
parent_by_wave_code = {(r["wave"], r["code"].lower()): r for r in rows}
bracket_suffix = re.compile(r"(?:_bracketbracket_(?:min|max)|_bracket_(?:min|max)|__(?:min|max)|_(?:min|max))$", re.I)
for rec in raw.itertuples(index=False):
    wave, code = str(rec.wave), str(rec.variable).lower()
    label, module = str(rec.variable_label), str(rec.module)
    if wave not in {"2011", "2013", "2015", "2018"} or not code.startswith("fn"):
        continue
    # The 2018 life-insurance bracket fields are C-only response bounds. Keep
    # them in the catalog-role audit without inheriting the parent's E concept.
    if wave == "2018" and code in {"fn056_w2_8_min", "fn056_w2_8_max"}:
        continue
    if not re.search(r"bracket", code + " " + label, re.I):
        continue
    parent_code = bracket_suffix.sub("", code)
    parent = parent_by_wave_code.get((wave, parent_code))
    if parent is None:
        # Some CHARLS releases name the parent in the bracket label and retain
        # a trailing underscore on the original response code.
        m = re.search(r"of\s+(fn[\w]+)", label, re.I)
        if m:
            possible = [m.group(1).lower(), m.group(1).lower().rstrip("_") + "_", m.group(1).lower().rstrip("_")]
            parent = next((parent_by_wave_code.get((wave, candidate)) for candidate in possible
                           if parent_by_wave_code.get((wave, candidate)) is not None), None)
    if parent is None:
        continue
    bound = "lower" if re.search(r"min", code + " " + label, re.I) else "upper" if re.search(r"max", code + " " + label, re.I) else "unresolved"
    inherited = dict(parent)
    inherited.update({
        "code": rec.variable, "source_label": label,
        "mapping_status": "linked source component; interval/unfolding bound only; not a standalone amount estimate",
        "construct": parent["construct"],
        "caveat": parent["caveat"] + " Bracket fields are retained as interval-response components; do not substitute them for an exact amount or treat them as independent exposures.",
        "source_archive": rec.source,
    })
    rows.append(inherited)

# FN097 is a categorical expectation about future/old-age financial resources,
# not a measure of pension receipt, enrollment, or income. Its core categories
# recur in 2013/2015/2018, but the 2018 question wording and skip denominator
# differ; preserve wave-specific caveats instead of implying full equivalence.
old_age_support_specs = {
    "2013": {
        "source_item": "2013 Work, Retirement and Pension questionnaire FN097_w2; FN098_w2 child follow-up",
        "mapping_status": "2013 questionnaire wording, five response categories, and child follow-up route verified; candidate only",
        "caveat": "Subjective anticipated financial support source for old age, not actual support received, current pension coverage, or income. Response 1=Children routes to FN098_w2 (choose all applicable children); other responses do not enter that child roster. Preserve this categorical item separately from the child roster and income/benefit measures.",
    },
    "2015": {
        "source_item": "2015 Wave 3 Work, Retirement and Pension questionnaire FN097_w2; FN098_w2 child follow-up",
        "mapping_status": "2015 questionnaire wording, five response categories, and child follow-up route verified; candidate only",
        "caveat": "Subjective anticipated financial support source for old age, not actual support received, current pension coverage, or income. Response 1=Children routes to FN098_w2 (choose all applicable children); other responses do not enter that child roster. Preserve this categorical item separately from the child roster and income/benefit measures.",
    },
    "2018": {
        "source_item": "2018 Wave 4 Pension questionnaire FN097_W2; FN098_W2 child follow-up",
        "mapping_status": "2018 questionnaire wording, five response categories, and conditional route verified; candidate only",
        "caveat": "Hypothetical resource if the respondent becomes too old to work, not actual support received, current pension coverage, or income. The questionnaire defines commercial pension insurance as directly purchased life insurance with regular premiums and recurring benefits from the contracted age. Response 1=Children routes to FN098_W2 (choose all applicable children); responses 2–5 end the pension section. FN097_W2 is reached through wave-specific pension screening/skip logic, so do not assume its denominator is identical to 2013/2015. Keep wave wording, route, and denominator distinct; do not assert full cross-wave equivalence.",
    },
}
old_age_support_labels = (
    "1=Children; 2=Savings; 3=Pension or retirement salary; "
    "4=Commercial pension insurance; 5=Other"
)
for row in rows:
    spec = old_age_support_specs.get(str(row.get("wave", "")))
    if spec and str(row.get("code", "")).lower() == "fn097_w2" and row.get("concept_id") == "old_age_financial_support_source":
        row.update(spec)
        row.update({
            "mapping_status": spec["mapping_status"],
            "construct": "respondent-reported expected financial resource for old age (single categorical response)",
            "caveat": spec["caveat"],
            "unit": "categorical; one primary response",
            "value_label_status": "official questionnaire response categories and route reviewed; Codebook frequencies omitted",
            "value_label_source": f"sources_official/CHARLS_{row['wave']}_Questionnaire_extracted.txt; sources_official/CHARLS_{row['wave']}_Codebook_extracted.txt",
            "value_labels": old_age_support_labels,
            "value_semantics": "single categorical expected old-age resource; child roster is a separate conditional follow-up",
            "official_source": f"CHARLS {row['wave']} Questionnaire and Codebook",
        })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "pension_exposure_variable_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["construct", "concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"), source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "pension_exposure_concept_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"pension mappings={len(out)}; concepts={out.concept_id.nunique()}; constructs={out.construct.nunique()}")


