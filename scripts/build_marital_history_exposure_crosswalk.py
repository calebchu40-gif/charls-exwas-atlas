"""Build wave-specific marriage-history exposure candidates."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "marital_history_exposure_crosswalk_v1.csv"

specs = [
    ("2011", "be003", "lifetime_marriage_count", "累计结婚次数",
     "How Many Times Have You Been Married", "Nonnegative integer count of lifetime marriages; questionnaire soft check flags values greater than 2.",
     "Asked at baseline; follow-up marriage-detail route depends on count. This is a self-reported count, not marital status.",
     "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"),
    ("2013", "be003", "lifetime_marriage_count", "累计结婚次数",
     "How Many Times Have You Been Married", "Nonnegative integer count of lifetime marriages; questionnaire soft check flags values greater than 2.",
     "In 2013 the lifetime count is asked for NEWIW; returning interviewees are routed to the since-last-interview item. Do not treat as a repeated-wave measure for all respondents.",
     "sources_official/CHARLS_2013_Questionnaire_extracted.txt"),
    ("2013", "be003_w2_1", "marriage_count_since_last_interview", "上次访问以来结婚次数",
     "How Many Times Have You Been Married Since Last Interview", "Nonnegative integer count of marriage events since last interview; not a lifetime count.",
     "Asked on the returning-interview route; follow-up marriage details are conditional on a positive response. Interview type and item route define the denominator.",
     "sources_official/CHARLS_2013_Questionnaire_extracted.txt"),
    ("2015", "be003_w2_1", "marriage_count_since_last_interview", "上次访问以来结婚次数",
     "How Many Times Have You Been Married Since Last Interview", "Nonnegative integer count of marriage events since last interview; not a lifetime count.",
     "2015 questionnaire restricts this item by the marital-status/interview-type route; further marriage details are conditional on a positive count. Check wave-specific eligibility before defining a denominator.",
     "sources_official/CHARLS_2015_Questionnaire_extracted.txt"),
    ("2011", "be005", "parental_marriage_cash_goods_value", "结婚时父母给予的现金和物品价值",
     "Value of Cash and Goods Received from Parents When Married", "Continuous amount in Yuan; historical nominal amount, not inflation-adjusted.",
     "Asked only when the lifetime marriage count equals one. The 2011 codebook reports a minimum of -2000, which is not a plausible amount under the question wording; resolve its meaning/special-value handling before any analysis. Do not combine with 2013 without checking currency-year comparability.",
     "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"),
    ("2013", "be005", "parental_marriage_cash_goods_value", "结婚时父母给予的现金和物品价值",
     "Total Value of Cash and Goods Received When Married", "Continuous amount in Yuan; historical nominal amount, not inflation-adjusted.",
     "Asked on the single-marriage branch. The value represents parents' total cash and goods, including housing, given to both spouses at marriage; not a household wealth measure. For follow-up respondents, verify whether the branch denominator is controlled by lifetime BE003 or interval BE003_W2_1 before analysis. Do not combine waves before code-range, price-year, and denominator review.",
     "sources_official/CHARLS_2013_Questionnaire_extracted.txt"),
]

# Source-reviewed life-course event timing. These are wave-specific candidate
# exposures, not current marital status or automatic adjustment variables.
reviewed_specs = [
    ("2011", "be007", "first_marriage_end_year", "首次婚姻结束年份",
     "Year Your First Marriage End", "Calendar year (1900–2011); questionnaire hard check requires year >= BE006.",
     "Asked within the baseline marriage-history route after the respondent reports a first marriage. This records event timing, not current marital status; retain route and verify authorized-release special values.",
     "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "continuous/date component; no discrete labels"),
    ("2011", "be008", "first_marriage_end_reason", "首次婚姻结束原因",
     "Why End Your First Marriage", "1=Death of spouse; 2=Divorce",
     "Conditional first-marriage history item. A spouse's death and divorce are distinct event types; do not merge with current marital status or infer timing from this response.",
     "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "official questionnaire response categories reviewed; frequencies omitted"),
    ("2013", "be009_1", "most_recent_marriage_year", "最近一次婚姻年份",
     "When Was Your Most Recent Marriage: Year", "Calendar year (1900–2013); hard check requires year >= BE007.",
     "Asked on the marriage-history follow-up route for eligible respondents reporting a marriage event; questionnaire routing and interview type define the denominator. Do not treat as a repeated-wave measure for all respondents.",
     "sources_official/CHARLS_2013_Questionnaire_extracted.txt", "continuous/date component; no discrete labels"),
    ("2013", "be009_2", "most_recent_marriage_month", "最近一次婚姻月份",
     "When Was Your Most Recent Marriage: Month", "0=Do not remember; 1–12=calendar month",
     "Asked on the marriage-history follow-up route for eligible respondents reporting a marriage event. Zero means month not remembered per questionnaire; preserve it as a distinct response, not January or a missing code.",
     "sources_official/CHARLS_2013_Questionnaire_extracted.txt", "official questionnaire response categories reviewed; frequencies omitted"),
]

raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
rows = []
for wave, code, concept, label_zh, label, semantics, caveat, questionnaire in specs:
    match = raw[(raw.wave == wave) & (raw.variable.str.lower() == code.lower())]
    if match.empty:
        raise SystemExit(f"Missing source catalog field: {wave} {code}")
    codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    qtext = (ROOT / questionnaire.replace("/", "\\")).read_text(encoding="utf-8", errors="ignore").lower()
    if code.lower() not in qtext:
        raise SystemExit(f"Official questionnaire does not contain {wave} {code}")
    rows.append({
        "wave": wave, "code": code, "concept_id": concept,
        "concept_label": label_zh, "domain": "social determinants",
        "module": str(match.iloc[0].module), "source_label": label,
        "value_labels": semantics,
        "value_label_status": "official wave questionnaire/codebook item definition reviewed; frequencies omitted",
        "value_label_source": f"{questionnaire}; {codebook}",
        "mapping_status": "wave-specific marital-history exposure candidate; item definition reviewed; analysis eligibility remains conditional",
        "construct": label_zh, "value_semantics": semantics,
        "caveat": caveat + " Numeric values are not cross-wave harmonization codes.",
        "source_archive": f"{match.iloc[0].source}; {questionnaire}; {codebook}",
        "questionnaire_source": questionnaire,
    })

for wave, code, concept, label_zh, label, semantics, caveat, questionnaire, label_status in reviewed_specs:
    match = raw[(raw.wave == wave) & (raw.variable.str.lower() == code.lower())]
    if match.empty:
        raise SystemExit(f"Missing source catalog field: {wave} {code}")
    codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    for rel in (questionnaire, codebook):
        if not (ROOT / rel).is_file():
            raise SystemExit(f"Missing official source: {rel}")
    cbtext = (ROOT / codebook).read_text(encoding="utf-8", errors="replace").replace("\x00", "").lower()
    if code.lower() not in cbtext:
        raise SystemExit(f"Official Codebook does not contain {wave} {code}")
    qtext = (ROOT / questionnaire).read_text(encoding="utf-8", errors="replace").replace("\x00", "").lower()
    if code.lower() not in qtext:
        raise SystemExit(f"Official questionnaire does not contain {wave} {code}")
    rows.append({
        "wave": wave, "code": code, "concept_id": concept,
        "concept_label": label_zh, "domain": "social determinants",
        "module": str(match.iloc[0].module), "source_label": label,
        "value_labels": semantics, "value_label_status": label_status,
        "value_label_source": f"{questionnaire}; {codebook}",
        "mapping_status": "wave-specific life-course marriage-history exposure candidate; questionnaire and Codebook item reviewed; analysis eligibility remains conditional",
        "construct": label_zh, "value_semantics": semantics,
        "caveat": caveat + " Codes and years are wave-specific; no cross-wave harmonization is implied.",
        "source_archive": f"{match.iloc[0].source}; {questionnaire}; {codebook}",
        "questionnaire_source": questionnaire,
    })
df = pd.DataFrame(rows)
if df.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave/code row")
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Wrote {len(df)} wave-field mappings for {df.concept_id.nunique()} marital-history concepts")
