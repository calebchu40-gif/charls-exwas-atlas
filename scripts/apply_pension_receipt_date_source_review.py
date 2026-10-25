"""Apply source-only review to pension receipt-start date components.

This review uses public questionnaires and codebooks only. It does not inspect
participant records or infer distributions, missing-code behavior, or analysis
eligibility from codebook summaries.
"""
from __future__ import annotations

import re
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "audit/pension_exposure_variable_mapping_v1.csv"
LABEL_AUDIT = ROOT / "audit/pension_codebook_value_labels_v1.csv"
SOURCE_CROSSWALK = ROOT / "audit/ep_concept_source_crosswalk_v1.csv"
CATALOG_CSV = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
CATALOG_JSON = ROOT / "audit/charls_atlas_candidate_fields_v0.json"
MASTER_CATALOG = ROOT / "site-prototype/dist/catalog.json"
E_CATALOG = ROOT / "site-prototype/dist/catalog_e.json"
CONCEPT = "pension_benefit_start_date_components"


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def main() -> None:
    frame = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    selected = frame[(frame.concept_id == CONCEPT) & frame.wave.astype(str).isin({"2013", "2018"})]
    expected = {"2013": 22, "2018": 14}
    counts = selected.groupby("wave").size().astype(int).to_dict()
    if counts != expected or selected.duplicated(["wave", "code"]).any():
        raise SystemExit(f"Unexpected pension start-date target rows: {counts}; expected {expected}")

    locked = {
        ("2013", "fn081_w2_2"): (
            "DO NOT ANALYZE: questionnaire extraction repeats the year subfield identifier for the month; Codebook identifies _2 as month; reconcile exact release questionnaire before using.",
            "2013 FN081 month subfield identity conflicts between questionnaire extraction and Codebook; retain as unresolved and do not relabel from inference.",
        ),
        ("2013", "fn095_w2_1"): (
            "DO NOT ANALYZE: 2013 Codebook labels this field No Observations; verify exact authorized release and field presence first.",
            "2013 Codebook marks FN095 year as No Observations; candidate metadata only, not an observed analytic measure.",
        ),
        ("2013", "fn095_w2_2"): (
            "DO NOT ANALYZE: 2013 Codebook labels this field No Observations; verify exact authorized release and field presence first.",
            "2013 Codebook marks FN095 month as No Observations; candidate metadata only, not an observed analytic measure.",
        ),
    }
    qnames = {"2013": "CHARLS_2013_Questionnaire_extracted.txt", "2018": "CHARLS_2018_Questionnaire_extracted.txt"}
    for idx, row in selected.iterrows():
        wave, code = str(row.wave), str(row.code).lower()
        cbname = f"CHARLS_{wave}_Codebook_extracted.txt"
        qpath = ROOT / "sources_official" / qnames[wave]
        cbpath = ROOT / "sources_official" / cbname
        questionnaire = qpath.read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        codebook = cbpath.read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        if compact(code) not in compact(codebook):
            raise SystemExit(f"Official Codebook field not located: {wave}/{code}")
        stem = re.match(r"[a-z]+\d+", code).group(0)
        if stem.lower() not in questionnaire.lower():
            raise SystemExit(f"Official questionnaire item not located: {wave}/{code}")

        source = f"sources_official/{qnames[wave]}; sources_official/{cbname}"
        role = "year" if re.search(r"(?:^|_)1(?:_|$)", code) else "month"
        note = (
            f"Pension-receipt start-date {role} component. Keep paired with its wave-, plan-, and route-specific counterpart; "
            "this is a recalled calendar component, not a duration or an independently validated exposure. "
            "Questionnaire/codebook source review only; confirm release storage, special missing values, denominator, and route before analysis."
        )
        status = "official questionnaire/Codebook field and item identity reviewed; continuous date component; release coding and analysis eligibility pending"
        unit = "calendar year component" if role == "year" else "calendar month component; questionnaire notes 0 may mean month not remembered"
        key = (wave, code)
        if key in locked:
            status, note = locked[key]
            unit = "unresolved; do not analyze"
        # Preserve item-level slot identity: in 2018 FN003 currently contains
        # only year slots in this atlas family. Do not synthesize month rows.
        frame.at[idx, "mapping_status"] = status
        frame.at[idx, "value_label_status"] = status
        frame.at[idx, "value_label_source"] = source
        frame.at[idx, "value_labels"] = ""
        frame.at[idx, "unit"] = unit
        frame.at[idx, "value_semantics"] = note
        prior = str(row.caveat).strip(" ;")
        frame.at[idx, "caveat"] = (prior + "; " + note).strip("; ") if note not in prior else prior

    frame.to_csv(MAPPING, index=False, encoding="utf-8-sig")
    labels = pd.read_csv(LABEL_AUDIT, dtype=str, encoding="utf-8-sig").fillna("")
    for row in selected.itertuples(index=False):
        key = (str(row.wave), str(row.code).lower())
        mask = labels.wave.astype(str).eq(key[0]) & labels.code.astype(str).str.lower().eq(key[1])
        if int(mask.sum()) != 1:
            raise SystemExit(f"Expected one pension label audit row for {key}; got {int(mask.sum())}")
        source_row = frame[(frame.wave.astype(str) == key[0]) & (frame.code.astype(str).str.lower() == key[1])].iloc[0]
        labels.loc[mask, "value_label_status"] = source_row.value_label_status
        labels.loc[mask, "value_label_source"] = source_row.value_label_source
        labels.loc[mask, "value_labels"] = ""
    labels.to_csv(LABEL_AUDIT, index=False, encoding="utf-8-sig")
    crosswalk = pd.read_csv(SOURCE_CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    for row in selected.itertuples(index=False):
        key = (str(row.wave), str(row.code).lower())
        mask = (crosswalk.Wave.astype(str).eq(key[0])
                & crosswalk["Source.Code"].astype(str).str.lower().eq(key[1])
                & crosswalk["Concept.ID"].astype(str).eq(CONCEPT))
        if int(mask.sum()) != 1:
            raise SystemExit(f"Expected one E/P source-crosswalk row for {key}; got {int(mask.sum())}")
        source_row = frame[(frame.wave.astype(str) == key[0]) & (frame.code.astype(str).str.lower() == key[1])].iloc[0]
        crosswalk.loc[mask, "Unit"] = source_row.unit
        crosswalk.loc[mask, "Value.Semantics"] = source_row.value_semantics
        crosswalk.loc[mask, "Mapping.Status"] = source_row.mapping_status
        crosswalk.loc[mask, "Caveat"] = source_row.caveat
        crosswalk.loc[mask, "Source.Document"] = source_row.value_label_source
    crosswalk.to_csv(SOURCE_CROSSWALK, index=False, encoding="utf-8-sig")
    updates = {
        (str(row.wave), str(row.code).lower()): row
        for row in frame.loc[selected.index].itertuples(index=False)
    }

    def sync_catalog_row(row: dict) -> bool:
        key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
        review = updates.get(key)
        if review is None or str(row.get("epcf", "")).lower() != "e":
            return False
        row["Value.Label.Review"] = review.value_label_status
        row["Value.Label.Source"] = review.value_label_source
        row["Value.Labels"] = ""
        if "value_label_review" in row:
            row["value_label_review"] = review.value_label_status
        if "value_label_source" in row:
            row["value_label_source"] = review.value_label_source
        if "value_labels" in row:
            row["value_labels"] = ""
        row["Concept.Mapping.Status"] = review.mapping_status
        row["Concept.Mapping.Caveat"] = review.caveat
        if "concept_mapping_statuses" in row:
            row["concept_mapping_statuses"] = review.mapping_status
        if "concept_mapping_caveats" in row:
            row["concept_mapping_caveats"] = review.caveat
        row["Concept.Unit.Candidates"] = f"{CONCEPT}={review.unit}"
        if "candidate_concept_units" in row:
            row["candidate_concept_units"] = f"{CONCEPT}={review.unit}"
        return True

    with CATALOG_CSV.open(encoding="utf-8-sig", newline="") as stream:
        import csv
        reader = csv.DictReader(stream)
        columns, records = list(reader.fieldnames or []), list(reader)
    matched = sum(sync_catalog_row(row) for row in records)
    if matched not in {0, 36}:
        raise SystemExit(f"Expected either no pension rows or all 36 wave-resolved rows in compact catalog CSV; updated {matched}")
    if matched:
        with CATALOG_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
    for path in (CATALOG_JSON, MASTER_CATALOG, E_CATALOG):
        records = json.loads(path.read_text(encoding="utf-8"))
        matched = sum(sync_catalog_row(row) for row in records)
        if path != MASTER_CATALOG and matched != 36:
            raise SystemExit(f"Expected 36 wave-resolved fields in {path.name}; updated {matched}")
        path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Reviewed 36 2013/2018 pension receipt-start date fields against public questionnaires and Codebooks; 3 source conflicts/No Observations fields remain locked; no participant data or frequencies used.")


if __name__ == "__main__":
    main()
