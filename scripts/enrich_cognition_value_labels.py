"""Add verified CHARLS codebook labels for a small, explicit cognition subset."""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "audit" / "cognition_item_variable_mapping_v1.csv"
JSON = ROOT / "site-prototype" / "dist" / "cognition_items_v1.json"
LABELS = {
    (2011, "dc004"): "1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor",
    (2013, "dc004"): "1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor",
    (2015, "dc004"): "1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor",
    (2018, "dc004"): "1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor",
    (2020, "dc006"): "1=Excellent; 2=Very Good; 3=Good; 4=Fair; 5=Poor; 997=Don't Know (codebook category)",
}
SOURCE = "Official CHARLS wave codebook; see audit/cognition_value_label_review_v1.md"
STATUS = "official response categories transcribed; special/missing-code completeness pending"

FIELD_LABELS = {}
FIELD_LABELS[(2013, "dc006_cnt")] = ("1=1 repeat; 2=2 repeats; 3=3 repeats", "2013 official codebook values for number of word-list repeats; codebook frequency counts are not shown; verify whether initial presentation is counted before deriving or pooling")
for code in ["dc001", "dc002", "dc003", "dc004", "dc005"]:
    FIELD_LABELS[(2020, code)] = ("1=Correct; 2=Error; 997=Don't Know; 999=Refused", "2020 codebook response categories; confirm structural/routing missingness in the data")
for step in range(1, 6):
    FIELD_LABELS[(2020, f"dc007_{step}")] = ("1=Record Answer; 997=Don't Know; 999=Refused", "2020 codebook response-status categories; answer content is stored in the paired _1 field")
    FIELD_LABELS[(2020, f"dc007_{step}_1")] = ("", "continuous raw subtraction response; Codebook extreme maxima occur; valid range and scoring require authorized raw-data QA")
FIELD_LABELS[(2020, "dc008")] = ("1=Used; 2=Not Used", "2020 codebook response categories")
FIELD_LABELS[(2020, "dc009")] = ("1=Correct; 2=Error; 3=Not Assessed; 997=Don't Know; 999=Refused", "2020 codebook response categories; separate not-assessed from incorrect")
for item in range(48, 68):
    FIELD_LABELS[(2018, f"dc{item:03d}_w4")] = ("1=Yes; 5=No; 8=Don't Know", "official 2018 codebook response categories; WRE word-recognition item; no score derived")

# 2018 object-learning checkboxes: the item's matching code means selected,
# while 0 means that checkbox was not selected. The s97 field is a separate
# not-assessed marker and must not be turned into a wrong answer.
for round_no in range(1, 6):
    prefix = f"dc013_w4_{round_no}"
    FIELD_LABELS[(2018, f"{prefix}_s1")] = ("0=No; 1=Ball", "2018 official Codebook multi-response item field; checkbox-specific No is not equivalent to task failure")
    FIELD_LABELS[(2018, f"{prefix}_s2")] = ("0=No; 2=Flag", "2018 official Codebook multi-response item field; checkbox-specific No is not equivalent to task failure")
    FIELD_LABELS[(2018, f"{prefix}_s3")] = ("0=No; 3=Tree", "2018 official Codebook multi-response item field; checkbox-specific No is not equivalent to task failure")
    FIELD_LABELS[(2018, f"{prefix}_s4")] = ("0=No; 4=None", "2018 official Codebook multi-response none-of-the-above field")
    FIELD_LABELS[(2018, f"{prefix}_s97")] = ("0=No; 97=Not Assessed", "2018 official Codebook separate assessment-status field; not an incorrect recall response")
for suffix, answer in [("s1", "Ball"), ("s2", "Flag"), ("s3", "Tree")]:
    FIELD_LABELS[(2018, f"dc015_w4_{suffix}")] = (f"0=No; {suffix[1:]}={answer}", "2018 official Codebook multi-response delayed-recall item field; preserve separate item coding")
FIELD_LABELS[(2018, "dc015_w4_s4")] = ("0=No; 4=None", "2018 official Codebook none-of-the-above checkbox")
FIELD_LABELS[(2018, "dc015_w4_s97")] = ("0=No; 97=Not Assessed", "2018 official Codebook separate assessment-status field; not an incorrect recall response")
FIELD_LABELS[(2018, "dc016_w4")] = ("1=Correct; 5=Error; 97=Not Assessed", "2018 official Codebook naming-task categories; preserve not-assessed separately")
FIELD_LABELS[(2018, "dc017_w4")] = ("1=Correct; 5=Error; 97=Not Assessed", "2018 official Codebook naming-task categories; preserve not-assessed separately")
FIELD_LABELS[(2018, "dc018_w4")] = ("1=Correct; 5=Error; 97=Not Assessed", "2018 official Codebook response categories; frequencies omitted")
FIELD_LABELS[(2018, "dc019_w4")] = ("1=Correct, respondent closed eyes; 2=Correct after instruction was read aloud; 5=Error; 97=Not Assessed", "2018 official Codebook response categories; preserve assisted-correct and not-assessed separately; frequencies omitted")
for code in ["dc020_w4", "dc021_w4", "dc022_w4", "dc023_w4", "dc024_w4"]:
    FIELD_LABELS[(2018, code)] = ("1=Correct; 5=Error; 97=Not Assessed", "2018 official Codebook response categories; preserve not-assessed separately; frequencies omitted")
for code in ["dc001_w4", "dc002_w4", "dc005_w4", "dc006_w4", "dc007_w4", "dc008_w4", "dc009_w4", "dc010_w4", "dc012_w4"]:
    FIELD_LABELS[(2018, code)] = ("1=Correct; 5=Error; 97=Not Assessed", "2018 official Codebook response categories; preserve not-assessed separately; frequencies omitted")
FIELD_LABELS[(2018, "dc024")] = ("1=Used; 2=Not Used", "2018 official Codebook response categories; instrument-use metadata, not cognitive performance")
for i in range(1, 6):
    FIELD_LABELS[(2018, f"dc014_w4_{i}")] = ("97=Don't Know; 98=Refused", "official Codebook extraction exposes only a partial response-code set; 97/98 are listed reason/response-status codes; do not infer other codes")
for code in ["dc042_w4", "dc043_w4"]:
    FIELD_LABELS[(2018, code)] = ("1=Correct; 5=Error; 97=Cannot Answer", "2018 official Codebook response categories; preserve cannot-answer separately; frequencies omitted")
FIELD_LABELS[(2018, "dc044_w4")] = ("1=Clearly indicate the route; 2=Address of market; 3=Name of market; 4=A vague answer; 5=Don't Know; 97=Cannot Answer", "2018 official Codebook response categories; preserve distinct answer levels and cannot-answer; frequencies omitted")
FIELD_LABELS[(2018, "dc045_w4")] = ("1=Point to window and then door; 2=Point to window only (no door available); 3=Point to door only (no window available); 4=Not Applicable; 5=Incorrect action; 97=Cannot Answer", "2018 official Codebook response categories; preserve not-applicable and cannot-answer separately; frequencies omitted")
for wave in [2011, 2013, 2015]:
    for i, component in [(1, "Year"), (2, "Month"), (3, "Day")]:
        FIELD_LABELS[(wave, f"dc001s{i}")] = (f"{i}={component} is correct", "official Codebook extraction exposes only a partial response-code set; only the correct category is listed; do not infer unlisted codes")
    FIELD_LABELS[(wave, "dc002")] = ("1=Day of week correct; 2=Day of week incorrect", "official Codebook response categories; frequencies omitted")
    FIELD_LABELS[(wave, "dc003")] = ("1=Season correct; 2=Season incorrect", "official Codebook response categories; frequencies omitted")
    FIELD_LABELS[(wave, "dc024")] = ("1=Yes; 2=No", "official Codebook categories for paper/pencil or other aid use; test-administration metadata, not cognitive performance")
    FIELD_LABELS[(wave, "dc025")] = ("1=Drew the picture; 2=Failed to draw the picture", "official Codebook response categories; frequencies omitted")
FIELD_LABELS[(2018, "dc028_w4_1")] = ("1=Refused; 3=Unable at old age; 4=Deaf; 5=Other", "2018 official Codebook lists categories 1, 3, 4, and 5 only; code 2 is not listed and completeness is unconfirmed; task nonresponse metadata, not a recall score")
for suffix, label in [("s1", "Administered verbally"), ("s2", "Interruption occurred during administration"), ("s3", "Respondent had difficulty reading the words"), ("s4", "None of the above")]:
    FIELD_LABELS[(2018, f"dc031_w4_{suffix}")] = (f"0=No; {suffix[1:]}={label}", "2018 official Codebook multi-response administration-condition indicator; frequencies omitted; measurement-condition metadata, not cognitive performance")

# Word-recall fields use different storage conventions across releases. Earlier
# codebooks list the selected word-list slot as the stored value; 2018 uses
# item-specific checkbox values (0=No, item code=selected); 2020 uses binary
# checkboxes for ten items plus explicit None/Refused options. Never transfer
# one wave's storage convention to another.
WORD_LABELS_2018 = {
    "dc028_w4": ["Butter", "Arm", "Shore", "Letter", "Queen", "Cabin", "Pole", "Ticket", "Grass", "Engine"],
    "dc029_w4": ["Pole", "Letter", "Butter", "Queen", "Arm", "Shore", "Grass", "Cabin", "Ticket", "Engine"],
    "dc030_w4": ["Shore", "Letter", "Arm", "Cabin", "Pole", "Ticket", "Engine", "Grass", "Butter", "Queen"],
    "dc047_w4": ["Shore", "Letter", "Arm", "Cabin", "Pole", "Ticket", "Engine", "Grass", "Butter", "Queen"],
}
for prefix, words in WORD_LABELS_2018.items():
    for i, word in enumerate(words, 1):
        FIELD_LABELS[(2018, f"{prefix}_s{i}")] = (f"0=No; {i}={word}", "2018 codebook item-specific binary storage; 0=no and item code=selected")
    FIELD_LABELS[(2018, f"{prefix}_s11")] = ("0=No; 11=None", "2018 codebook none-of-the-above checkbox")
    FIELD_LABELS[(2018, f"{prefix}_s12")] = ("0=No; 12=Refused to Recall", "2018 codebook refusal checkbox; not an incorrect answer")

for wave, prefixes, none_code, refusal_code in [
    (2011, ["dc006s", "dc027s"], 11, None),
    (2013, ["dc006_1_s", "dc006_2_s", "dc006_3_s", "dc027s"], 11, None),
    (2015, ["dc006s", "dc027s"], 11, 12),
]:
    for prefix in prefixes:
        for i in range(1, 11):
            FIELD_LABELS[(wave, f"{prefix}{i}")] = (f"{i}=Wordlist[{i}]", "Official codebook stored category is the word-list position; no unselected-value code inferred")
        FIELD_LABELS[(wave, f"{prefix}{none_code}")] = (f"{none_code}=None", "Official codebook none-of-the-above category; absence/unselected storage not inferred")
        if refusal_code:
            FIELD_LABELS[(wave, f"{prefix}{refusal_code}")] = (f"{refusal_code}=Refuse to Recall", "Official codebook refusal category; separate from no words recalled")

for prefix in ["dc012_s", "dc013_s", "dc014_s"]:
    for i in range(1, 11):
        FIELD_LABELS[(2020, f"{prefix}{i}")] = ("0=No; 1=Yes", "2020 codebook binary word-item checkbox; exact word-list position is in source_label")
for i in range(1, 11):
    FIELD_LABELS[(2020, f"dc028_s{i}")] = ("0=No; 1=Yes", "2020 official Codebook delayed-recall word-item checkbox; exact word-list position is in source_label")
for code, label in [
    ("dc012_s11", "11=Yes (None of the Above)"), ("dc012_s12", "12=Yes (Refused to Recall)"),
    ("dc012_s13", "13=Yes (Unable to Understand or Complete the Test)"),
    ("dc013_s11", "11=Yes (None of the Above)"), ("dc013_s12", "12=Yes (Refused to Recall)"),
    ("dc014_s11", "11=Yes (None of the Above)"), ("dc014_s12", "12=Yes (Refused to Recall)"),
]:
    FIELD_LABELS[(2020, code)] = (f"0=No; {label}", "official 2020 Codebook multi-response special-option checkbox; preserve separately from individual word responses; frequencies omitted")
FIELD_LABELS[(2020, "dc028_s11")] = ("0=No; 11=Yes (None of the Above)", "2020 official Codebook delayed-recall none-of-the-above checkbox")
FIELD_LABELS[(2020, "dc028_s12")] = ("0=No; 12=Yes (Refused to Recall)", "2020 official Codebook delayed-recall refusal checkbox; separate from no words recalled")
FIELD_LABELS[(2018, "dc026_w4")] = ("1=Correct; 5=Error; 8=Don't Know; 97=Refused; 99=Other", "2018 Codebook categories; cultural familiarity/education warning applies; frequencies omitted")
FIELD_LABELS[(2018, "dc026_w4_revised")] = ("1=Correct; 5=Error; 8=Don't Know; 97=Refused", "2018 Codebook alternate revised scoring field; exact revision rule unconfirmed; frequencies omitted")

def main():
    df = pd.read_csv(CSV, dtype=str).fillna("")
    if "value_labels" not in df.columns:
        df["value_labels"] = ""
    if "value_label_source" not in df.columns:
        df["value_label_source"] = ""
    if "value_label_status" not in df.columns:
        df["value_label_status"] = ""
    count = 0
    for i, row in df.iterrows():
        key = (int(row.wave), row.code)
        if row.concept_id == "cog_subjective_memory" and key in LABELS:
            df.at[i, "value_labels"] = LABELS[key]
            df.at[i, "value_label_source"] = SOURCE
            df.at[i, "value_label_status"] = STATUS
            count += 1
        if key in FIELD_LABELS:
            labels, status = FIELD_LABELS[key]
            df.at[i, "value_labels"] = labels
            df.at[i, "value_label_source"] = SOURCE
            df.at[i, "value_label_status"] = status
            count += 1
    items = json.loads(JSON.read_text(encoding="utf-8"))
    updated = 0
    for concept in items:
        for field in concept.get("source_fields", []):
            key = (int(field["wave"]), field["code"])
            if concept.get("concept_id") == "cog_subjective_memory" and key in LABELS:
                field["value_labels"] = LABELS[key]
                field["value_label_source"] = SOURCE
                field["value_label_status"] = STATUS
                updated += 1
            if key in FIELD_LABELS:
                field["value_labels"], field["value_label_status"] = FIELD_LABELS[key]
                field["value_label_source"] = SOURCE
                updated += 1
    hcap_marker = "Official CHARLS HCAP guidance"
    hcap_general = (
        "Official CHARLS HCAP guidance: 2018 HCAP was intended for respondents aged 60+. "
        "Literacy, Mandarin/dialect familiarity, vision, and hearing can affect test performance. "
        "Inspect nonnumeric responses and distinguish cannot-answer, don't-know, refusal, "
        "non-assessment, and other missingness; do not infer a cognitive error from missingness. "
        "Sensitivity restrictions by literacy/language/sensory impairment may change the target population "
        "or induce bias, so define the estimand before restricting the sample."
    )
    item_warnings = {
        "dc019_w4": "Official CHARLS HCAP Data Alert identifies this read-and-follow instruction as potentially affected by both literacy and vision.",
        "dc023_w4": "Official CHARLS HCAP Data Alert identifies sentence writing as potentially affected by literacy.",
        "dc024_w4": "Official CHARLS HCAP Data Alert identifies overlapping-pentagon copying as potentially affected by literacy and vision.",
        "dc016_w4": "Official CHARLS HCAP Data Alert identifies watch naming as potentially affected by vision.",
        "dc017_w4": "Official CHARLS HCAP Data Alert identifies pencil naming as potentially affected by vision.",
        "dc018_w4": "Official CHARLS HCAP Data Alert says phrase repetition may disadvantage non-Mandarin speakers.",
        "dc026_w4": "Official CHARLS HCAP Data Alert cautions that the cactus naming item may reflect cultural familiarity and education, not cognition alone.",
        "dc026_w4_revised": "Official CHARLS HCAP Data Alert's cultural-familiarity caution applies to this alternate scoring field as well; its revision rule remains unconfirmed.",
    }
    warning_prefixes = {
        "dc013_w4_1_s": "Official CHARLS HCAP Data Alert says the Mandarin-paraphrased three-object learning list may disadvantage non-Mandarin speakers.",
        "dc015_w4_s": "Official CHARLS HCAP Data Alert says the Mandarin-paraphrased three-object delayed-recall list may disadvantage non-Mandarin speakers.",
    }
    wave4_codes = {field["code"].lower() for concept in items for field in concept.get("source_fields", []) if str(field.get("wave")) == "2018"}
    required = {"dc019_w4", "dc023_w4", "dc024_w4", "dc016_w4", "dc017_w4", "dc018_w4", "dc026_w4", "dc026_w4_revised"}
    if not required.issubset(wave4_codes) or not any(code.startswith("dc013_w4_1_s") for code in wave4_codes) or not any(code.startswith("dc015_w4_s") for code in wave4_codes):
        raise SystemExit(f"Expected HCAP warning fields missing from cognition map: {sorted(required - wave4_codes)}")
    longitudinal_memory = (
        "Official CHARLS-HCAP User Guidance notes that Wave 4 ten-word memory content and administration differ "
        "from prior waves; three immediate-recall trials were used, elevating delayed recall scores. Raw Wave 4 "
        "memory scores must not be treated as directly comparable change; the guidance recommends equipercentile-equated "
        "scores for longitudinal memory analyses. The Data Alert also cautions that some CERAD words may be unfamiliar."
    )
    for concept in items:
        concept_id = concept.get("concept_id", "")
        fields_2018 = [f for f in concept.get("source_fields", []) if str(f.get("wave")) == "2018"]
        if not fields_2018:
            continue
        current = concept.get("caveat", "").strip()
        if hcap_marker not in current:
            concept["caveat"] = f"{current} {hcap_general}".strip()
        if concept_id in {"cog_word_immediate", "cog_word_delayed"} and "three immediate-recall trials were used" not in concept.get("caveat", ""):
            concept["caveat"] = f"{concept['caveat']} {longitudinal_memory}".strip()
        for field in fields_2018:
            code = field["code"].lower()
            warning = item_warnings.get(code)
            if not warning:
                warning = next((msg for prefix, msg in warning_prefixes.items() if code.startswith(prefix)), None)
            if warning:
                note = field.get("note", "").strip()
                if "Official CHARLS HCAP Data Alert" not in note:
                    field["note"] = f"{note} {warning} (2023 Data Alert; 2024 User Guidance).".strip()
    for i, row in df.iterrows():
        if str(row.wave) != "2018":
            continue
        code = row.code.lower()
        warning = item_warnings.get(code)
        if not warning:
            warning = next((msg for prefix, msg in warning_prefixes.items() if code.startswith(prefix)), None)
        if warning:
            note = str(row.get("note", "")).strip()
            if "Official CHARLS HCAP Data Alert" not in note:
                df.at[i, "note"] = f"{note} {warning} (2023 Data Alert; 2024 User Guidance).".strip()
    for i, row in df.iterrows():
        if str(row.wave) != "2018":
            continue
        code = str(row.code).lower()
        if re.fullmatch(r"dc03[2-9]_w4", code):
            df.at[i, "value_label_status"] = "continuous count measure; official Codebook identifies 15-second animal-fluency interval; summary statistics are QA flags, not valid-range evidence"
            df.at[i, "value_label_source"] = SOURCE
            df.at[i, "note"] = f"{str(row.get('note', '')).strip()} Continuous count; do not use Codebook Min/Max as valid range without data QA.".strip()
        if str(row.wave) in {"2011", "2013", "2015"} and re.fullmatch(r"dc0(19|20|21|22|23)", code):
            df.at[i, "value_label_status"] = "continuous raw subtraction response; Codebook extreme maxima occur; valid range and scoring require authorized raw-data QA"
            df.at[i, "value_label_source"] = SOURCE
            df.at[i, "note"] = f"{str(row.get('note', '')).strip()} Raw subtraction answer; Codebook summary extrema are not a validated range or scoring rule.".strip()
        if re.fullmatch(r"dc014_w4_[1-5]_1", code):
            df.at[i, "value_label_status"] = "continuous recorded response; Codebook extrema include implausible values; inspect authorized raw data before defining valid range or scoring"
            df.at[i, "value_label_source"] = SOURCE
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"verified cognition field labels/semantics: csv={count}; json={updated}")

if __name__ == "__main__":
    main()


