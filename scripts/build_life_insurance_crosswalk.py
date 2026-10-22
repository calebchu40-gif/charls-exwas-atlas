"""Build a questionnaire-reviewed CHARLS life-insurance exposure crosswalk.

Uses official variable labels and question wording only. Never reads respondent records.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
lookup = {(str(r.wave), str(r.variable).lower()): r for r in raw.itertuples(index=False)}
rows = []

SOURCES = {
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt (printed pp. 207–208)",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt (printed pp. 183–184)",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt (printed pp. 233–234)",
}
COMMON = "Candidate exposure only; preserve wave-specific route, special missing codes, and the source answer. Do not treat conditional blanks as No; no codebook frequencies are used."

def add(wave, code, concept, label, construct, *, unit="", values="", caveat=COMMON, status="official questionnaire and CodeBook wording reviewed; candidate mapping, route and analysis eligibility require review"):
    rec = lookup.get((wave, code.lower()))
    if rec is None:
        raise SystemExit(f"missing raw metadata: {wave}/{code}")
    rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": label,
        "domain": "social protection", "module": rec.module, "source_label": rec.variable_label,
        "mapping_status": status, "construct": construct, "value_labels": values,
        "value_label_status": "official questionnaire/codebook response categories; frequencies omitted" if values else "continuous or date component; see unit and source",
        "value_label_source": SOURCES[wave], "unit": unit,
        "caveat": caveat, "source_archive": rec.source,
    })

for wave in ("2013", "2015"):
    add(wave, "fn056_w2_1", "life_insurance_participation", "是否参加人寿保险（自报）", "self-reported participation in life insurance",
        values="1=Yes; 2=No", caveat=COMMON + " 2013/2015: no response skips the remainder of this life-insurance section; question asks participation, not payout receipt.")
    add(wave, "fn056_w2_2_1", "life_insurance_purchase_timing", "人寿保险开始参加时间", "reported life-insurance participation start year", unit="year", caveat=COMMON + " Paired year/month components; do not infer exact date when month is 0 or missing.")
    add(wave, "fn056_w2_2_2", "life_insurance_purchase_timing", "人寿保险开始参加时间", "reported life-insurance participation start month", unit="month", caveat=COMMON + " Paired year/month components; do not infer exact date when month is 0 or missing.")

for wave in ("2013", "2015", "2018"):
    type_values = "1=Term life insurance; 2=Whole life insurance; 3=Survivorship insurance" if wave != "2018" else "1=Term life insurance; 2=Whole life insurance; 3=Pure endowment insurance"
    type_values += "; 4=Endowment insurance; 5=Other"
    type_caveat = COMMON + (" 2018 questionnaire says to record the most important policy when multiple policies exist; preserve original category wording." if wave == "2018" else " 2013/2015 asks which type the respondent participated in; other-type text is not a standardized category.")
    add(wave, "fn056_w2_3", "life_insurance_policy_type", "人寿保险类型（自报）", "reported life-insurance policy type", values=type_values, caveat=type_caveat)
    add(wave, "fn056_w2_7", "life_insurance_claim_or_reimbursement_status", "是否曾从人寿保险获得赔付/报销", "self-reported life-insurance payout/reimbursement status", values="1=Yes; 2=No",
        caveat=COMMON + (" 2018 asks ever received a payout; Yes skips ahead to benefit receipt timing." if wave == "2018" else " 2013/2015 asks whether reimbursement was received; No skips the amount question."))
    add(wave, "fn056_w2_9_1", "life_insurance_expected_benefit_monthly", "人寿保险预期月领取金额", "expected life-insurance benefit amount per month", unit="CNY/month")
    add(wave, "fn056_w2_9_2", "life_insurance_expected_benefit_lump_sum", "人寿保险预期一次性领取金额", "expected life-insurance lump-sum benefit amount", unit="CNY lump sum")

for wave in ("2013", "2015"):
    add(wave, "fn056_w2_4", "life_insurance_premium_payer", "人寿保险缴费承担者", "reported payer of life-insurance premium",
        values="1=Myself; 2=My Children; 3=Other Family Member or Relative; 4=Others")

for wave in ("2013", "2015", "2018"):
    if wave == "2013":
        add(wave, "fn056_w2_5", "life_insurance_premium_payment_frequency", "人寿保险缴费频率", "reported life-insurance premium payment frequency",
            values="1=Monthly; 2=Quarterly (questionnaire option; absent from the CodeBook response-category table); 3=Every 6 months; 4=Annually",
            status="official questionnaire response menu reviewed; CodeBook response-category table omits questionnaire option 2; frequencies excluded",
            caveat=COMMON + " The 2013 questionnaire defines codes 1=Monthly, 2=Quarterly, 3=Half a year, and 4=Annually. The official CodeBook response-category table lists 1, 3, and 4; it does not list option 2. The quarterly payment amount child (FN056_W2_6_2) is separately marked No Observations in the CodeBook. This is a questionnaire-menu versus observed-category coverage difference, not contradictory labels. Preserve the questionnaire-defined label if code 2 occurs in an approved release; do not infer the category's presence or absence from another wave. No frequencies are copied.")
    elif wave == "2015":
        add(wave, "fn056_w2_5", "life_insurance_premium_payment_frequency", "人寿保险缴费频率", "reported life-insurance premium payment frequency",
            values="1=Monthly; 2=Quarterly; 3=Every 6 months; 4=Annual",
            caveat=COMMON + " Frequency is a separate response from premium amount; do not interpret the frequency code as an amount.")
    else:
        add(wave, "fn056_w2_5", "life_insurance_premium_payment_frequency", "人寿保险缴费频率", "reported life-insurance premium payment frequency",
            values="1=Monthly; 2=Quaterly; 3=Half a Year; 4=Annually",
            caveat=COMMON + " Frequency is a separate response from premium amount; do not interpret the frequency code as an amount.")
    for suffix, unit in (("1", "CNY/month"), ("2", "CNY/quarter"), ("3", "CNY/half-year"), ("4", "CNY/year")):
        code = f"fn056_w2_6_{suffix}"
        add(wave, code, "life_insurance_premium_amount", "人寿保险缴费金额（按缴费周期）", "reported life-insurance premium amount by payment period", unit=unit,
            caveat=COMMON + " Unit is period-specific and varies by field; any annualization must be separately derived from the reported frequency and preserve source amount.")

for wave in ("2013", "2015"):
    add(wave, "fn056_w2_8", "life_insurance_claim_amount", "人寿保险已获赔付/报销金额", "reported life-insurance reimbursement amount", unit="CNY",
        caveat=COMMON + " Asked only on the reported reimbursement route; a zero amount is not assumed from a missing response.")

add("2018", "fn073_w4", "life_insurance_current_receive_expect_or_contribute", "人寿保险当前领取、预期领取或缴费（合并题）", "combined self-report of current receipt, expected receipt, or current contribution",
    values="1=Yes, participate or receive; 2=No", caveat=COMMON + " This 2018 combined item is not identical to the 2013/2015 participation-only item; retain as a separate concept. A No answer skips the life-insurance section.")

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "life_insurance_exposure_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"life-insurance crosswalk: {len(out)} mappings, {out.concept_id.nunique()} concepts")
