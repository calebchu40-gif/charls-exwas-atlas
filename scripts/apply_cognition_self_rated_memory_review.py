"""Apply the five-wave source review for the single-item self-rated memory outcome."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "audit/cognition_item_variable_mapping_v1.csv"
TOPIC = ROOT / "site-prototype/dist/cognition_items_v1.json"
CATALOG_CSV = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
CATALOG_JSON = ROOT / "audit/charls_atlas_candidate_fields_v0.json"

TARGETS = {
    "2011": ("dc004", "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", 4680, "CHARLS_2011_Codebook_extracted.txt", 63551),
    "2013": ("dc004", "CHARLS_2013_Questionnaire_extracted.txt", 3904, "CHARLS_2013_Codebook_extracted.txt", 20243),
    "2015": ("dc004", "CHARLS_2015_Questionnaire_extracted.txt", 3372, "CHARLS_2015_Codebook_extracted.txt", 18798),
    "2018": ("dc004", "CHARLS_2018_Questionnaire_extracted.txt", 3753, "CHARLS_2018_Codebook_extracted.txt", 49298),
    "2020": ("dc006", "CHARLS_2020_Questionnaire_Chinese_extracted.txt", 1731, "CHARLS_2020_Codebook_extracted.txt", 6881),
}
MAPPING_STATUS = (
    "official questionnaire wording and 1–5 ordinal direction reviewed; retain wave-specific field; "
    "sample eligibility and special/missing-code completeness require release-level QA"
)
LABEL_STATUS = (
    "official Codebook response categories checked against questionnaire; 2020 includes 997=Don't Know; "
    "other special/missing codes require authorized-release dictionary QA"
)
SEMANTICS = (
    "Single-item subjective rating of current memory, not an objective memory-test score or dementia diagnosis. "
    "Codes 1–5 run from excellent to poor in all five waves; 2020 also lists 997=Don't Know. "
    "Keep wave-specific fields and missing codes. Do not derive or pool a score until sample eligibility, "
    "administration, and release-level missing-code handling are validated."
)
OFFICIAL_SOURCE = "Official CHARLS questionnaires and Codebooks; see audit/cognition_self_rated_memory_five_wave_review_2026-10-25.md"


def update() -> None:
    for wave, (_, qfile, qline, cfile, cline) in TARGETS.items():
        qtext = (ROOT / "sources_official" / qfile).read_text(encoding="utf-8", errors="replace")
        ctext = (ROOT / "sources_official" / cfile).read_text(encoding="utf-8", errors="replace")
        code, *_ = TARGETS[wave]
        if code.lower() not in qtext.lower() or code.lower() not in ctext.lower():
            raise ValueError(f"Official source is missing the expected self-rated memory field: {wave}/{code}")
        if wave == "2020" and "997" not in qtext[qtext.lower().find(code.lower()):qtext.lower().find(code.lower()) + 400]:
            raise ValueError("2020 questionnaire no longer documents the 997 Don't Know response")

    data = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    selected = data.concept_id.eq("cog_subjective_memory")
    if set(data.loc[selected, "wave"].astype(str)) != set(TARGETS):
        raise ValueError("Expected exactly one mapped self-rated memory field in each of five waves")
    for index in data.index[selected]:
        wave = str(data.at[index, "wave"])
        code, qfile, qline, cfile, cline = TARGETS[wave]
        if str(data.at[index, "code"]).lower() != code:
            raise ValueError(f"Unexpected code for self-rated memory in {wave}")
        data.at[index, "note"] = SEMANTICS
        data.at[index, "mapping_status"] = MAPPING_STATUS
        data.at[index, "value_label_source"] = f"sources_official/{cfile}:L{cline}; sources_official/{qfile}:L{qline}"
        data.at[index, "value_label_status"] = LABEL_STATUS
    data.to_csv(MAPPING, index=False, encoding="utf-8-sig")

    topics = json.loads(TOPIC.read_text(encoding="utf-8"))
    topic = [x for x in topics if x.get("concept_id") == "cog_subjective_memory"]
    if len(topic) != 1 or len(topic[0].get("source_fields", [])) != 5:
        raise ValueError("Cognition topic payload is missing one of the five reviewed wave fields")
    topic[0]["status"] = "official questionnaire wording and ordered response direction reviewed across five waves; candidate outcome; analysis readiness not established"
    topic[0]["caveat"] = SEMANTICS
    for source in topic[0]["source_fields"]:
        wave = str(source["wave"])
        source["mapping_status"] = MAPPING_STATUS
        source["value_label_status"] = LABEL_STATUS
        source["value_semantics"] = SEMANTICS
        source["questionnaire_source"] = f"sources_official/{TARGETS[wave][1]}:L{TARGETS[wave][2]}"
        source["value_label_source"] = f"sources_official/{TARGETS[wave][3]}:L{TARGETS[wave][4]}"
    TOPIC.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")

    keys = {(wave, target[0]) for wave, target in TARGETS.items()}
    csv_data = pd.read_csv(CATALOG_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    count = 0
    for index, row in csv_data.iterrows():
        key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
        if key in keys and "p" in {part.strip().lower() for part in str(row.get("epcf", "")).split(",")}:
            csv_data.at[index, "Value.Label.Review"] = LABEL_STATUS
            csv_data.at[index, "Value.Label.Source"] = OFFICIAL_SOURCE
            csv_data.at[index, "Harmonization.Status"] = SEMANTICS
            csv_data.at[index, "Concept.Mapping.Status"] = MAPPING_STATUS
            count += 1
    if count != 5:
        raise ValueError(f"Expected to update exactly five phenotype catalog rows; found {count}")
    csv_data.to_csv(CATALOG_CSV, index=False, encoding="utf-8-sig")

    # The compact public catalogue merges same-named fields across waves and
    # has no wave-specific source key. For dc004 this would mix self-rated
    # memory (2011–2018) with the unrelated 2020 checking-day field. Keep this
    # review on the wave-resolved source catalogues only.
    for path in (CATALOG_JSON,):
        records = json.loads(path.read_text(encoding="utf-8"))
        matched = 0
        for row in records:
            key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
            if key in keys and "p" in {part.strip().lower() for part in str(row.get("epcf", "")).split(",")}:
                row["Value.Label.Review"] = LABEL_STATUS
                row["Value.Label.Source"] = OFFICIAL_SOURCE
                row["Harmonization.Status"] = SEMANTICS
                row["Concept.Mapping.Status"] = MAPPING_STATUS
                for field, value in (("value_label_review", LABEL_STATUS), ("value_label_source", OFFICIAL_SOURCE),
                                     ("harmonization_status", SEMANTICS)):
                    if field in row:
                        row[field] = value
                matched += 1
        if matched != 5:
            raise ValueError(f"Expected five reviewed memory rows in {path.relative_to(ROOT)}; found {matched}")
        path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Reviewed five wave-specific self-rated memory fields; retained release-level QA and no pooled score.")


if __name__ == "__main__":
    update()
