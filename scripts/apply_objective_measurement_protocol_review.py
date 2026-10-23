"""Reconcile chair-stand setup and pre-BP behavior metadata to official instruments."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "audit/measurement_protocol_crosswalk_v1.csv"
MANUAL_2011 = "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt"
DOCS = {
    "2011": ROOT / MANUAL_2011,
    "2013": ROOT / "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt",
    "2015": ROOT / "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt",
}


def apply() -> None:
    for path in DOCS.values():
        if not path.exists():
            raise FileNotFoundError(path)
    text = {wave: path.read_text(encoding="utf-8", errors="replace").casefold() for wave, path in DOCS.items()}
    checks = {
        "2011": ("li875", "within the 30 minutes prior to completing the blood pressure test", "li007", "record the chair height from floor to seat"),
        "2013": ("qh006", "record the chair height from floor to seat"),
        "2015": ("qh006_1", "other chair, height"),
    }
    for wave, terms in checks.items():
        missing = [term for term in terms if term.casefold() not in text[wave]]
        if missing:
            raise ValueError(f"Official physical-examination source {wave} missing expected terms: {missing}")
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        columns = list(rows[0])

    for row in rows:
        wave, code = row["wave"], row["code"].casefold()
        if row["concept_id"] == "bp_recent_pretest_behavior" and wave == "2011" and code == "qa017":
            row.update({
                "value_semantics": "2011 physical-examination manual asks whether the respondent smoked, exercised, consumed alcohol, or ate within 30 minutes before the blood-pressure test (manual item LI875); the released-field Codebook label is QA017.",
                "mapping_status": "official 2011 physical-examination manual and Codebook reviewed; QA017 release-field label reconciled to manual LI875 wording; C metadata only",
                "caveat": "Blood-pressure measurement context only; not habitual behavior, diet exposure, or a blood-draw fasting indicator. Preserve the manual LI875 versus Codebook QA017 identifier distinction.",
                "source_document": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official.doc; sources_official/CHARLS_2011_Codebook_extracted.txt",
            })
        elif row["concept_id"] == "chair_stand_test_chair_setup" and wave == "2011" and code == "qh006":
            row.update({
                "value_semantics": "2011 Codebook lists released-field QH006 as Height; the official physical-examination manual records chair height from floor to seat as LI007. This is likely chair-test setup metadata, but the QH006/LI007 release-identifier relationship remains unresolved.",
                "mapping_status": "HOLD FOR RELEASE FIELD IDENTITY RECONCILIATION; 2011 official manual and Codebook differ on item code",
                "caveat": "Do not interpret as respondent standing height (QI002), and do not claim QH006=LI007 until the release-level crosswalk is confirmed. No response values are inferred.",
                "source_document": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official.doc; sources_official/CHARLS_2011_Codebook_extracted.txt",
            })
        elif row["concept_id"] == "chair_stand_test_chair_setup" and wave == "2013" and code == "qh006":
            row.update({
                "value_semantics": "Chair height from floor to seat, recorded in centimeters as repeated-chair-stand protocol setup metadata.",
                "mapping_status": "official 2013 Biomarker Questionnaire and Codebook reviewed; C measurement metadata only",
                "caveat": "Protocol/setup field, not respondent height or a health outcome. Keep separate from the 2015 chair-type selector.",
                "source_document": "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
            })
        elif row["concept_id"] == "chair_stand_test_chair_setup" and wave == "2015" and code == "qh006":
            row.update({
                "value_labels": "1=CHARLS chair with 42 cm height; 2=Other chair",
                "value_semantics": "Nominal chair-type selector. If code 2, the other chair's height is recorded separately in QH006_1 (cm).",
                "mapping_status": "official 2015 Biomarker Questionnaire and Codebook reviewed; C measurement metadata only",
                "caveat": "Chair-type/protocol field, not respondent height or an outcome; QH006_1 is the conditional continuous chair-height field.",
                "source_document": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
            })
        elif row["concept_id"] == "chair_stand_test_chair_setup" and wave == "2015" and code == "qh006_1":
            row.update({
                "value_semantics": "Height in centimeters of the other chair; asked only when QH006 selects Other chair.",
                "mapping_status": "official 2015 Biomarker Questionnaire and Codebook reviewed; C measurement metadata only",
                "caveat": "Conditional chair setup, not respondent standing height or an outcome. A blank outside the QH006=Other chair route is structural, not zero.",
                "source_document": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
            })

    if not any(r["concept_id"] == "chair_stand_test_chair_setup" and r["wave"] == "2015" and r["code"].casefold() == "qh006_1" for r in rows):
        rows.append({
            "concept_id": "chair_stand_test_chair_setup",
            "concept_label": "重复椅子起立测试座椅设置",
            "domain": "measurement metadata",
            "wave": "2015",
            "code": "qh006_1",
            "module": "Biomarker",
            "source_label": "Height of Other Chair",
            "value_labels": "",
            "value_semantics": "Height in centimeters of the other chair; asked only when QH006 selects Other chair.",
            "mapping_status": "official 2015 Biomarker Questionnaire and Codebook reviewed; C measurement metadata only",
            "caveat": "Conditional chair setup, not respondent standing height or an outcome. A blank outside the QH006=Other chair route is structural, not zero.",
            "source_document": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
            "source_archive": "CHARLS2015r.zip",
        })
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    # Keep the placeholder-review ledger aligned with the field-specific source adjudication.
    review_path = ROOT / "audit/c_placeholder_metadata_review_v1.csv"
    if review_path.exists():
        with review_path.open(encoding="utf-8-sig", newline="") as f:
            review_rows = list(csv.DictReader(f))
            review_columns = list(review_rows[0]) if review_rows else []
        for row in review_rows:
            if row.get("metadata_family") != "chair setup for repeated chair-stand test":
                continue
            key = (row.get("wave"), row.get("code", "").casefold())
            if key == ("2011", "qh006"):
                row["official_source"] = "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official.doc; sources_official/CHARLS_2011_Codebook_extracted.txt"
                row["review_status"] = "HOLD: manual LI007 versus Codebook QH006; measurement metadata only until release identity is reconciled"
                row["catalog_note"] = "QH006/LI007 item-code discrepancy; likely chair-test setup metadata, but do not claim equivalence until release identity is reconciled. Not respondent height."
            elif key == ("2013", "qh006"):
                row["official_source"] = "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"
                row["review_status"] = "official questionnaire and Codebook reviewed; C measurement metadata only"
                row["catalog_note"] = "Chair height from floor to seat in centimeters; protocol setup metadata, not respondent height or phenotype."
            elif key == ("2015", "qh006"):
                row["official_source"] = "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"
                row["review_status"] = "official questionnaire and Codebook reviewed; measurement metadata only"
                row["value_labels"] = "1=CHARLS chair with 42 cm height; 2=Other chair"
                row["catalog_note"] = "Nominal standard-chair/other-chair selector; QH006_1 records other-chair height in centimeters conditionally."
            elif key == ("2015", "qh006_1"):
                row["official_source"] = "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"
                row["review_status"] = "official questionnaire and Codebook reviewed; measurement metadata only"
                row["catalog_note"] = "Conditional other-chair height in centimeters after QH006=Other chair; structural absence is not zero."
        with review_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=review_columns)
            writer.writeheader()
            writer.writerows(review_rows)


if __name__ == "__main__":
    apply()
