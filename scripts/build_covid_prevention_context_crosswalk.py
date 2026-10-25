"""Map questionnaire-grounded 2020 COVID prevention/context and response-change fields.

This is a metadata-only builder. It reads the raw variable dictionary and
official questionnaire/Codebook text, never respondent records or frequencies.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
QUESTIONNAIRE_REL = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt"
CODEBOOK_REL = "sources_official/CHARLS_2020_Codebook_extracted.txt"
QUESTIONNAIRE = (ROOT / QUESTIONNAIRE_REL).read_text(encoding="utf-8", errors="replace")
CODEBOOK = (ROOT / CODEBOOK_REL).read_text(encoding="utf-8", errors="replace")

E_ROWS: list[dict[str, str]] = []
P_ROWS: list[dict[str, str]] = []


def codebook_categories(code: str) -> list[str]:
    """Return only explicitly coded checkbox categories; discard frequencies."""
    lines = CODEBOOK.splitlines()
    heading = re.compile(rf"^\s*{re.escape(code)}\s*:", re.I)
    start = next((i for i, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        return []
    labels: list[str] = []
    for line in lines[start + 1:]:
        # Do not let a following variable's table leak into the current field.
        if re.match(r"^\s*[A-Za-z][A-Za-z0-9_]*\s*:", line):
            break
        if re.search(r"\bTotal\b", line, re.I):
            break
        # Checkbox variable sections explicitly print values such as "0 No" and
        # "4 Yes". Never include frequency/percent columns or infer absent codes.
        match = re.match(r"^\s*(\d+)\s+(No|Yes)\s+[\d,]+\s+[\d.]+\s*$", line, re.I)
        if match:
            labels.append(f"{match.group(1)}={match.group(2).title()}")
    return labels


def add(role: str, codes: list[str], concept: str, label: str, domain: str,
        question: str, construct: str, caveat: str, unit: str = "",
        value_labels: str = "") -> None:
    target = E_ROWS if role == "e" else P_ROWS
    for code in codes:
        key = code.lower()
        source = RAW[(RAW.wave.astype(str) == "2020") & RAW.variable.str.lower().eq(key)]
        if len(source) != 1:
            raise SystemExit(f"Expected one raw-dictionary field for 2020/{code}, found {len(source)}")
        if question.lower() not in QUESTIONNAIRE.lower():
            raise SystemExit(f"Questionnaire anchor missing for 2020/{code}: {question}")
        if key not in CODEBOOK.lower():
            raise SystemExit(f"Codebook field heading missing for 2020/{code}")
        row = source.iloc[0]
        categories = codebook_categories(code)
        if categories:
            labels = "; ".join(categories)
            label_status = (
                "Official 2020 Codebook explicitly coded checkbox labels transcribed; frequencies omitted; "
                "only printed codes are shown; unselected storage and routed denominator require authorized-release QA"
            )
        elif value_labels:
            labels = value_labels
            label_status = (
                "Questionnaire response options transcribed; Codebook category wording checked and frequencies omitted; "
                "release coding, special values and route require authorized-release QA"
            )
        else:
            labels = ""
            label_status = (
                "Official 2020 Questionnaire and Codebook field identity reviewed; no extractable "
                "categorical labels for this field; no categories inferred; unit, special values, "
                "route and release storage require authorized-release QA"
            )
        target.append({
            "wave": "2020", "code": code, "concept_id": concept,
            "concept_label": label, "domain": domain, "module": row.module,
            "source_label": row.variable_label, "construct": construct,
            "unit": unit, "value_labels": labels,
            "mapping_status": "2020 official Questionnaire and Codebook field identity checked; candidate metadata only; verify authorized-release coding, route, eligibility and sample design before analysis",
            "value_label_status": label_status,
            "value_label_source": f"{QUESTIONNAIRE_REL}; {CODEBOOK_REL}",
            "source_document": f"{QUESTIONNAIRE_REL}; {CODEBOOK_REL}",
            "source_question": question,
            "caveat": caveat,
        })


PREVENTION = "VA001"
add("e", [f"va001_s{i}" for i in range(1, 9)], "covid_prevention_measure_awareness_2020",
    "新冠预防措施认知（2020）", "Pandemic prevention and information context",
    PREVENTION, "2020 respondent-level awareness checklist for specified preventive measures and other measures",
    "Checklist item fields represent awareness/selection, not observed adherence or individual infection dose. Option 8 is an other-measure response with a separate description; the release dictionary has no separate field for questionnaire option 10. Do not infer an unselected state from a blank without release-specific storage validation.",
    value_labels="Questionnaire options 1–7: handwashing; alcohol/disinfectants; avoid handshaking; masks/gloves; avoid travel; avoid gatherings; social distancing; option 8=Other (description not included in this field). Field-specific response codes require release QA.")
add("e", ["va001_s9"], "covid_no_awareness_prevention_2020", "不了解新冠疫情或预防措施（2020）",
    "Pandemic prevention and information context", "VA001", "Exclusive response indicating the respondent did not know about the pandemic or preventive measures",
    "This is an explicit exclusive lack-of-awareness response, not a preventive action. Keep it separate from the checklist of known measures; verify its exclusive routing and release storage.")
add("e", [f"va002_s{i}" for i in range(1, 11)], "covid_prevention_information_sources_2020",
    "新冠防护信息来源（2020）", "Pandemic prevention and information context",
    "VA002", "2020 respondent-level multiple-response sources for prevention information",
    "Information access is a social-context candidate; the final option is exclusive. Do not treat the set as a validated information-literacy score or infer non-selection from missing fields.",
    value_labels="Questionnaire options 1–10: TV; newspaper; online media; radio; family/friends/community; healthcare practitioner; village broadcast; poster; other; no external source (exclusive). Field-specific response codes require release QA.")
add("e", ["va003"], "covid_mask_use_during_pandemic_2020", "疫情期间外出佩戴口罩（2020）",
    "Pandemic prevention and information context", "VA003", "Ordinal self-report of masking when going out during the pandemic",
    "Four questionnaire categories include did not go out; retain this as a distinct response, not as never wearing a mask. One-wave retrospective self-report; no causal interpretation.",
    value_labels="1=Always; 2=Sometimes; 3=Never; 4=Did not go out during the pandemic")
add("e", ["va004"], "covid_current_outdoor_masking_2020", "当前外出与佩戴口罩情况（2020）",
    "Pandemic prevention and information context", "VA004", "Current going-out and masking status",
    "Keep the no-outing category separate from not wearing a mask; current status is a 2020 interview-time measure, not pandemic-period behavior.",
    value_labels="1=Wears a mask when going out; 2=Does not wear a mask when going out; 3=Does not go out at all")
add("e", ["va005"], "covid_current_masking_status_2020", "当前佩戴口罩状态（2020）",
    "Pandemic prevention and information context", "VA005", "Current mask status and transition from prior mask use",
    "Questionnaire includes continued use, stopped-use, never-use and no-outing routes; preserve all categories and do not combine with VA004 as duplicate observations.",
    value_labels="1=Still wears when going out; 2=Wore during pandemic but not now; 3=Never wears a mask; 4=Has not gone out since the pandemic")
add("e", ["va005_1"], "covid_mask_nonuse_duration_2020", "停止佩戴口罩时长（2020）",
    "Pandemic prevention and information context", "VA005", "Conditional elapsed months since stopping mask use",
    "Conditional on VA005 stopped-use route; preserve -1 and month-response handling under the official release. Not a general duration for all respondents.",
    unit="Months; conditional on VA005 option 2")
add("e", ["va006_s1", "va006_s2"], "covid_preventive_stockpiling_2020", "疫情初期防护与生活物资储备（2020）",
    "Pandemic prevention and information context", "VA006", "Multiple-response purchases above usual during the three days after Wuhan closure",
    "Short, explicitly dated self-reported stockpiling behavior; do not infer an individual exposure dose or treat the exclusive none option as an independent exposure.",
    value_labels="1=Food/cooking oil/vegetables; 2=Masks/hand sanitizer/disinfectant; field-specific response codes require release QA")
add("e", ["va006_s3"], "covid_no_preventive_stockpiling_2020", "疫情初期未额外储备物资（2020）",
    "Pandemic prevention and information context", "VA006", "Exclusive none-of-the-above response to the dated stockpiling checklist",
    "This is an explicit exclusive response, not a missing value and not interchangeable with unselected positive checklist items. Confirm release storage and conflicts before analysis.")
add("e", ["va007"], "covid_government_response_perception_2020", "对政府疫情防控措施严格程度的评价（2020）",
    "Pandemic prevention and information context", "VA007", "Respondent rating of whether government containment measures were too strict, appropriate, or insufficiently strict",
    "A single-item perception of the policy context, not an objective policy stringency measure or validated attitude scale. Questionnaire and Codebook use nonidentical wording for response 2; preserve the source discrepancy and do not harmonize it silently.",
    value_labels="1=Too strict; 2=Appropriate; 3=Not strict enough")
next(row for row in E_ROWS if row["code"] == "va007")["value_label_status"] = (
    "Questionnaire response options transcribed; Codebook wording differs for response 2 (Satisfied vs Appropriate); "
    "source discrepancy retained; frequencies omitted; release coding requires authorized-release QA"
)

add("e", ["vb001_s2"], "covid_confirmed_or_suspected_household_contact_2020", "家庭成员新冠疑似/确诊接触（2020）",
    "Pandemic infection and quarantine context", "VB001", "Household member reported as confirmed or suspected case",
    "Household-contact context, not a respondent diagnosis; keep household and non-cohabiting contacts separate. Questionnaire item is select-all-that-apply.")
add("e", ["vb001_s3"], "covid_confirmed_or_suspected_nonhousehold_relative_contact_2020", "非同住亲属新冠疑似/确诊接触（2020）",
    "Pandemic infection and quarantine context", "VB001", "Non-cohabiting relative reported as confirmed or suspected case",
    "Social contact context only; not respondent infection status. Preserve the select-all route and source-specific storage.")
add("e", ["vb001_s4"], "covid_confirmed_or_suspected_acquaintance_contact_2020", "熟人新冠疑似/确诊接触（2020）",
    "Pandemic infection and quarantine context", "VB001", "Acquaintance reported as confirmed or suspected case",
    "Social contact context only; not respondent infection status. Preserve the select-all route and source-specific storage.")
add("p", ["vb001_s1"], "covid_confirmed_or_suspected_respondent_2020", "受访者新冠疑似/确诊报告（2020）",
    "Pandemic-related health outcomes", "VB001", "Respondent self identified as confirmed or suspected case",
    "The item combines confirmed and suspected status in the questionnaire wording; do not relabel as laboratory-confirmed infection. Preserve exclusive none/refusal routes and validate released-data coding.")
for code, relation, label in [
    ("vb002_s1", "household", "同住家庭成员新冠病例康复/死亡报告（2020）"),
    ("vb002_s2", "nonhousehold_relative", "非同住亲属新冠病例康复/死亡报告（2020）"),
    ("vb002_s3", "acquaintance", "熟人新冠病例康复/死亡报告（2020）"),
]:
    add("p", [code], f"covid_contact_recovery_or_death_{relation}_2020", label,
        "Pandemic-related social-network outcomes", "VB002", f"Respondent reports recovery status or death among a confirmed/suspected case in the {relation.replace('_', ' ')} relationship group",
        "A conditional, respondent-reported social-network outcome following the VB001 confirmed/suspected-case screen; it is not the respondent's health outcome and does not establish cause of death. Preserve relation group, survey skip, exclusive none and refusal semantics.")
add("p", ["vb004"], "covid_hospitalization_days_2020", "新冠治疗住院天数（2020）",
    "Pandemic-related health outcomes", "VB004", "Self-reported hospital stay for coronavirus treatment",
    "Questionnaire instructs 0 if not hospitalized and -1 if unable to answer; retain conditional eligibility, special values, and the distinction between no hospitalization and missing.",
    unit="Days")
add("p", ["vb012"], "covid_testing_utilization_2020", "是否接受过新冠检测（2020）",
    "Pandemic-related healthcare utilization", "VB012", "Whether the respondent had ever been tested for coronavirus by the 2020 interview",
    "A pandemic-specific healthcare-utilization outcome, not infection status or a positive-test result. The conditional last-test year/month are timing metadata and are not treated as separate outcomes.")
add("e", ["vb005_s1", "vb005_s2", "vb005_s3", "vb005_s4"], "covid_quarantine_exposure_reason_2020", "新冠隔离/医学观察经历原因（2020）",
    "Pandemic infection and quarantine context", "VB005", "Select-all quarantine/medical-observation reasons excluding hospitalization in the question stem",
    "Travel, close contact, residential-building closure and hospital-related quarantine are distinct contexts. Positive-test and exclusive no-quarantine options are not included in this exposure concept; preserve unknown/refusal options outside the candidate matrix.",
    value_labels="Questionnaire options 1–4: travel; close contact; apartment/building closed; hospital-related quarantine. Field-specific response codes require release QA")
add("e", ["xquarantined"], "covid_any_quarantine_derived_2020", "是否有新冠隔离经历（官方派生指标，2020）",
    "Pandemic infection and quarantine context", "XQuarantined", "Official auxiliary indicator derived from selection of any VB005 reason 1–5",
    "Derived from VB005 options 1–5 according to the official questionnaire auxiliary-variable definition; overlaps the reason-specific candidate fields and should not be entered in the same model with them without a prespecified estimand. Verify the released derivation and coding before use.",
    value_labels="0=No; 1=Yes")
add("p", ["vb005_s5"], "covid_positive_test_quarantine_reason_2020", "因核酸检测阳性隔离（2020）",
    "Pandemic-related health outcomes", "VB005", "Positive nucleic-acid test as a quarantine reason",
    "This checklist flag is a self-reported positive-test reason, not a complete infection history; do not equate a blank with a negative test.")
add("e", ["vb008"], "covid_total_quarantine_days_2020", "新冠隔离总天数（2020）",
    "Pandemic infection and quarantine context", "VB008", "Total duration across multiple quarantine experiences",
    "Questionnaire asks for summed days across episodes and uses -1 for unable to answer; distinguish conditional nonparticipation from zero and retain the official questionnaire's handling of repeated episodes.",
    unit="Days")
add("e", [f"vb009_s{i}" for i in range(1, 5)], "covid_quarantine_location_2020", "新冠隔离地点（2020）",
    "Pandemic infection and quarantine context", "VB009", "Conditional multiple-response location checklist among respondents with a quarantine experience",
    "Location choices (hospital, centralized observation site, own residence, other) are a conditional context candidate, not a dose or validated facility-quality measure. Do not infer nonselection from blanks or generalize beyond the routed quarantine group.")
add("e", ["vb010"], "covid_quarantine_out_of_pocket_cost_2020", "新冠隔离期间个人支付费用（2020）",
    "Pandemic economic and social context", "VB010", "Self-reported quarantine accommodation and food cost",
    "Conditional on quarantine experience; household/individual payer scope and currency-unit storage must be verified in the authorized release. Do not turn skips into zero.",
    unit="Yuan")
add("e", ["vb011"], "covid_quarantine_social_contact_2020", "隔离期间可见/交谈的同场人员（2020）",
    "Pandemic infection and quarantine context", "VB011", "Social contact availability at quarantine site",
    "Conditional on quarantine experience; distinguish yes/no from don't know/refusal, and do not imply a measured social-support scale.",
    value_labels="1=Yes; 2=No; 997=Don't know; 999=Refuse")

add("e", ["vc000"], "covid_fear_related_self_isolation_days_2020", "疫情期间因担心感染居家隔离最长天数（2020）",
    "Pandemic infection and quarantine context", "VC000", "Longest self-isolation period attributed to infection fear outside quarantine",
    "The questionnaire explicitly excludes quarantine through a routing phrase and defines 0 for no such episode or going out every day; preserve -1 unable-to-answer and avoid double-counting formal quarantine.",
    unit="Days")
add("e", ["vc001"], "covid_residence_during_lunar_new_year_outbreak_2020", "春节疫情暴发期间居住地（2020）",
    "Pandemic infection and quarantine context", "VC001", "Self-reported residence location during the defined outbreak period",
    "One-wave historical residence context, not a geocoded exposure or measured community transmission rate; retain location-category and free-text routing separately.",
    value_labels="1=Same village/community; 2=Other village/community in same county; 3=Other county/district; 4=Other area (Hong Kong, Macao, Taiwan or abroad); 999=Refuse")

activity_specs = [
    ("vc002", "outdoor_frequency", "疫情期间每日外出频率变化"),
    ("vc003", "outdoor_time", "疫情期间每日户外时长变化"),
    ("vc004", "vigorous_activity", "疫情期间剧烈活动时长变化"),
    ("vc005", "moderate_activity", "疫情期间中等强度活动时长变化"),
    ("vc006", "light_activity", "疫情期间轻体力活动时长变化"),
    ("vc007", "neighbor_visits", "疫情期间探访邻居频率变化"),
    ("vc008", "mahjong_cards", "疫情期间棋牌活动频率变化"),
    ("vc009", "square_dancing", "疫情期间广场舞频率变化"),
    ("vc010", "phone_contact", "疫情期间电话/短信联系频率变化"),
    ("vc011", "internet_contact", "疫情期间互联网社交联系频率变化"),
    ("vc014", "smoking", "疫情期间吸烟量变化"),
    ("vc015", "alcohol", "疫情期间饮酒量变化"),
    ("vc016", "sleep", "疫情期间睡眠时长变化"),
    ("vc017", "food_intake", "疫情期间每日进食量变化"),
]
for code, construct, label in activity_specs:
    add("p", [code], f"covid_period_{construct}_change_2020", label,
        "Pandemic-related behavioral and functioning outcomes", code.upper(),
        "Retrospective ordinal comparison with a hypothetical no-pandemic situation during the specified outbreak period",
        "This is a self-reported change relative to a hypothetical counterfactual, not absolute activity, intake or exposure. Preserve the one-wave time window, response direction and item-specific never/no-device routes; do not combine items into an unvalidated score.",
        value_labels="1=Increased a lot; 2=Increased a little; 3=Unchanged; 4=Decreased a little; 5=Decreased a lot")
for code, construct, label in [
    ("vc007", "neighbor_visits", "探访邻居"), ("vc008", "mahjong_cards", "棋牌活动"),
    ("vc009", "square_dancing", "广场舞"), ("vc010", "phone_contact", "电话/短信联系"),
    ("vc011", "internet_contact", "互联网社交联系"),
]:
    target = next(r for r in P_ROWS if r["code"] == code)
    target["value_labels"] += "; 6=Never done this" if code in {"vc007", "vc008", "vc009", "vc010", "vc011"} else ""
for code in ("vc010", "vc011"):
    next(r for r in P_ROWS if r["code"] == code)["value_labels"] += "; 7=No such devices in then-residence" if code == "vc010" else "; 6=No such devices in then-residence; 7=Never done this"
next(r for r in P_ROWS if r["code"] == "vc010")["value_labels"] = "1=Increased a lot; 2=Increased a little; 3=Unchanged; 4=Decreased a little; 5=Decreased a lot; 6=No such devices in then-residence; 7=Never done this"
next(r for r in P_ROWS if r["code"] == "vc011")["value_labels"] = "1=Increased a lot; 2=Increased a little; 3=Unchanged; 4=Decreased a little; 5=Decreased a lot; 6=No such devices in then-residence; 7=Never done this"
for code in ("vc007", "vc008", "vc009"):
    next(r for r in P_ROWS if r["code"] == code)["value_labels"] = "1=Increased a lot; 2=Increased a little; 3=Unchanged; 4=Decreased a little; 5=Decreased a lot; 6=Never done this"
for code, cid, label in [
    ("vc012", "covid_fear_symptom_2020", "疫情相关恐惧感（2020）"),
    ("vc013", "covid_anxiety_symptom_2020", "疫情相关压力/焦虑感（2020）"),
]:
    add("p", [code], cid, label, "Pandemic-related behavioral and functioning outcomes", code.upper(),
        "Self-reported frequency of pandemic-related fear or stress/anxiety during the defined outbreak period",
        "Single-item, pandemic-specific emotional response; not a validated general depression/anxiety scale. Preserve the four ordered responses, don't-know/refusal codes and time frame.",
        value_labels="1=Rarely or not at all; 2=Not much; 3=Sometimes or half of the time; 4=Most of the time; 997=Don't know; 999=Refuse")

restriction_specs = [
    (1, "strictest", "严格封闭社区"), (2, "resident_entry_exit", "居民出入受限"),
    (3, "visitor_exclusion", "限制非居民进入"), (4, "conditional_visitor_access", "访客有条件进入"),
]
for i, key, label in restriction_specs:
    concept = f"covid_residential_restriction_{key}_2020"
    add("e", [f"vd001_s{i}", f"vd001_{i}"], concept, f"疫情期间社区管控：{label}（2020）",
        "Pandemic-related community environment", "VD001",
        "Wave-5 community/residential-area restriction type and corresponding duration",
        "The questionnaire states periods for restriction types should not overlap and totals should be within the interview-month window; types are ordered by strictness. Retain type and duration as linked but separate source fields, preserve -1 and route/response semantics, and do not sum durations without checking non-overlap and release coding.",
        unit="Indicator: field-specific selection code; duration: days")
add("p", ["vd002"], "covid_square_dancing_cancellation_days_2020", "疫情期間广场舞活动取消天数（2020）",
    "Pandemic-related behavioral and functioning outcomes", "VD002", "Days of outdoor dancing cancellation",
    "One-wave self-reported duration of cancelled public recreation; do not treat as measured activity dose or sum with household restriction durations.",
    unit="Days")
add("p", ["vd003"], "covid_mahjong_cancellation_days_2020", "疫情期间棋牌公共活动取消天数（2020）",
    "Pandemic-related behavioral and functioning outcomes", "VD003", "Days of cancellation of public mahjong/card recreation",
    "One-wave self-reported duration of cancelled public recreation; do not treat as individual activity dose or combine with VD002 without an estimand.",
    unit="Days")

for role, rows, filename in [
    ("e", E_ROWS, AUDIT / "pandemic_context_exposure_crosswalk_2020_v1.csv"),
    ("p", P_ROWS, AUDIT / "pandemic_context_phenotype_crosswalk_2020_v1.csv"),
]:
    frame = pd.DataFrame(rows)
    keys = frame[["wave", "code"]].assign(code=lambda d: d.code.str.lower())
    if keys.duplicated().any():
        raise SystemExit(f"Duplicate {role.upper()} wave-field keys in pandemic crosswalk")
    frame.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"{filename.relative_to(ROOT)}: {len(frame)} unique source fields; {frame.concept_id.nunique()} concepts; no respondent data or frequencies")
