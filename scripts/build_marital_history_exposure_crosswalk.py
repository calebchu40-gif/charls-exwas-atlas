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
df = pd.DataFrame(rows)
if df.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave/code row")
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Wrote {len(df)} wave-field mappings for {df.concept_id.nunique()} marital-history concepts")
