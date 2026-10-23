"""Expose source-backed DA056 option identity without inventing response codes."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MAPPING = AUDIT / "social_exposure_crosswalk_v1.csv"
WAVES = ("2011", "2013", "2015")


def main() -> None:
    crosswalk = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    if "value_label_status" not in crosswalk:
        crosswalk["value_label_status"] = ""
    selected = crosswalk[
        crosswalk["concept_id"].eq("social_participation")
        & crosswalk["wave"].isin(WAVES)
        & crosswalk["code"].str.lower().str.startswith("da056")
    ].copy()
    if len(selected) != 41:
        raise SystemExit(f"Expected 41 2011-2015 DA056 source fields; found {len(selected)}")

    for idx, row in selected.iterrows():
        wave, code = str(row["wave"]), str(row["code"]).lower()
        source = ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt"
        text = source.read_text(encoding="utf-8", errors="replace").lower()
        if code not in text:
            raise SystemExit(f"Official Codebook field not found: {wave}/{code}")
        label_status = (
            "official Codebook identifies selected activity/device option; respondent-level storage, "
            "unselected state, and eligible denominator are unresolved; no response-value labels assigned"
        )
        if code.startswith("da056_w3"):
            semantics = (
                "Official 2015 Codebook identifies the selected internet-device option for this field. "
                "The listed number is an option/slot identifier in the descriptive table; it does not "
                "establish respondent-level coding or the representation of unselected devices. Do not "
                "infer No from absence; confirm released-data storage and routed denominator before analysis."
            )
        elif wave == "2011":
            semantics = (
                "Official 2011 Codebook identifies this fixed activity category, but its summary lists the "
                "selected category without a verified respondent-level negative/unselected code. Preserve "
                "the fixed activity identity; do not infer No from absence or treat the option index as an "
                "individual response without authorized-release QA."
            )
        else:
            semantics = (
                f"Official {wave} Codebook identifies this DA056 activity option. The number shown in its "
                "descriptive summary is the selected activity/option identifier; the summary does not verify "
                "respondent-level storage or how unselected options are represented. Do not infer No from "
                "absence; verify released-data coding and the eligible denominator before analysis."
            )
        row["value_labels"] = ""
        row["value_label_status"] = label_status
        row["value_label_source"] = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        row["value_semantics"] = semantics
        row["mapping_status"] = label_status
        row["caveat"] = semantics
        if not row.get("questionnaire_source"):
            questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
            row["questionnaire_source"] = f"sources_official/{questionnaire}"
        crosswalk.loc[idx, row.index] = row
        selected.loc[idx, row.index] = row
    crosswalk.to_csv(MAPPING, index=False, encoding="utf-8-sig")

    topic_path = ROOT / "site-prototype" / "dist" / "social_exposures_v1.json"
    topics = json.loads(topic_path.read_text(encoding="utf-8"))
    topic = next(item for item in topics if item.get("concept_id") == "social_participation")
    lookup = {(str(row.wave), str(row.code).lower()): row for row in selected.itertuples(index=False)}
    updated = 0
    for item in topic.get("source_fields", []):
        key = (str(item.get("wave", "")), str(item.get("code", "")).lower())
        if key not in lookup:
            continue
        row = lookup[key]
        item["value_labels"] = ""
        item["value_label_source"] = row.value_label_source
        item["value_semantics"] = row.value_semantics
        item["note"] = row.value_label_status
        item["questionnaire_source"] = row.questionnaire_source
        updated += 1
    if updated != 41:
        raise SystemExit(f"Expected 41 topic records updated; found {updated}")
    topic_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")

    catalog_csv = AUDIT / "charls_atlas_candidate_fields_v0.csv"
    if catalog_csv.exists():
        catalog = pd.read_csv(catalog_csv, dtype=str, encoding="utf-8-sig").fillna("")
        for row in selected.to_dict("records"):
            mask = catalog["Source.Wave"].eq(row["wave"]) & catalog["Variable.Name"].str.lower().eq(row["code"].lower())
            if not mask.any():
                raise SystemExit(f"DA056 field missing from candidate catalogue: {row['wave']}/{row['code']}")
            catalog.loc[mask, "Value.Labels"] = ""
            catalog.loc[mask, "Value.Label.Source"] = row["value_label_source"]
            catalog.loc[mask, "Value.Label.Review"] = row["value_label_status"]
            catalog.loc[mask, "Harmonization.Status"] = row["value_semantics"]
        catalog.to_csv(catalog_csv, index=False, encoding="utf-8-sig")

    site_json = ROOT / "site-prototype" / "dist" / "catalog.json"
    if site_json.exists():
        records = json.loads(site_json.read_text(encoding="utf-8"))
        for row in selected.to_dict("records"):
            matches = [item for item in records if str(item.get("Source.Wave")) == row["wave"] and str(item.get("Variable.Name", "")).lower() == row["code"].lower()]
            if not matches:
                raise SystemExit(f"DA056 field missing from master site catalog: {row['wave']}/{row['code']}")
            for item in matches:
                item["Value.Labels"] = ""
                item["Value.Label.Source"] = row["value_label_source"]
                item["Value.Label.Review"] = row["value_label_status"]
                item["Harmonization.Status"] = row["value_semantics"]
                item["value_labels"] = ""
                item["value_label_source"] = row["value_label_source"]
                item["value_label_review"] = row["value_label_status"]
                item["harmonization_status"] = row["value_semantics"]
        site_json.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"DA056 source status reviewed: {len(selected)} fields; no response-value categories or frequencies assigned")


if __name__ == "__main__":
    main()
