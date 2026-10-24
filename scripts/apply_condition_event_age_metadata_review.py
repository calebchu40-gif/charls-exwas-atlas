"""Classify reviewed event/condition-age fields as C measurement metadata."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ("2013", "da007_w2_6_2"),
    ("2015", "da007_w2_6_2"),
    ("2018", "da007_w2_6_2"),
    ("2015", "zda065_1"),
}
FAMILY = "condition or event timing metadata"
NOTE = (
    "Age-at-event/onset field within a condition or prior-wave health-history route; "
    "not respondent current age, not a phenotype, and not an automatic adjustment covariate. "
    "Retain the originating condition and wave; confirm person linkage, skip codes and "
    "authorized-release storage before any analytic use."
)
STATUS = (
    "official questionnaire and Codebook item identity reviewed; continuous age-at-event/onset "
    "metadata; Codebook sample summaries omitted"
)


def read_sources(wave: str) -> tuple[str, str]:
    codebook_rel = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    questionnaire_rel = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt"
    codebook = (ROOT / codebook_rel).read_text(encoding="utf-8", errors="replace")
    questionnaire = (ROOT / questionnaire_rel).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    return codebook_rel, questionnaire_rel


def audit_records() -> list[dict[str, str]]:
    catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
    result = []
    for wave, code in sorted(TARGETS):
        codebook_rel, questionnaire_rel = read_sources(wave)
        codebook, questionnaire = (ROOT / codebook_rel).read_text(encoding="utf-8", errors="replace"), (ROOT / questionnaire_rel).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        compact_codebook = re.sub(r"[^a-z0-9]", "", codebook.lower())
        if re.sub(r"[^a-z0-9]", "", code.lower() + "age") not in compact_codebook:
            raise SystemExit(f"Official Codebook does not identify {wave}/{code} as an age field")
        if code == "da007_w2_6_2":
            if "recentheartattack" not in re.sub(r"[^a-z0-9]", "", codebook.lower()):
                raise SystemExit(f"Heart-attack route not verified for {wave}/{code}")
            route = "Age component of the recent-heart-attack timing item."
        else:
            q = re.sub(r"[^a-z0-9]", "", questionnaire.lower())
            if "atwhatagedidyoustarttosmokeonaregularbasis" not in q:
                raise SystemExit(f"Smoking-onset prompt not verified for {wave}/{code}")
            route = "Age component of the prior-wave smoking-history preload asking when regular smoking began."
        match = [r for r in catalog if str(r.get("Source.Wave", "")) == wave and str(r.get("Variable.Name", "")).lower() == code and str(r.get("epcf", "")).lower() == "c"]
        if len(match) != 1:
            raise SystemExit(f"Expected one C catalogue row for {wave}/{code}; found {len(match)}")
        result.append({
            "wave": wave,
            "code": code,
            "metadata_family": FAMILY,
            "official_sources": f"{questionnaire_rel}; {codebook_rel}",
            "source_field_label": str(match[0].get("Variable.Description", "")),
            "review_status": STATUS,
            "route_summary": route,
            "catalog_note": route + " " + NOTE,
        })
    return result


def update_row(row: dict[str, object], item: dict[str, str]) -> None:
    row["category"] = "measurement metadata"
    row["subcategory"] = FAMILY
    row["Candidate.Status"] = "official questionnaire and Codebook reviewed; condition/event timing metadata"
    row["Harmonization.Status"] = item["catalog_note"]
    row["Review.Flag"] = "C condition/event timing metadata; not a selected adjustment covariate"
    row["Value.Labels"] = ""
    row["Value.Label.Source"] = item["official_sources"]
    row["Value.Label.Review"] = STATUS
    row["value_labels"] = ""
    row["value_label_source"] = item["official_sources"]
    row["value_label_review"] = STATUS
    row["harmonization_status"] = item["catalog_note"]


def main() -> None:
    records = audit_records()
    (ROOT / "audit/condition_event_age_metadata_review_v1.csv").parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(ROOT / "audit/condition_event_age_metadata_review_v1.csv", index=False, encoding="utf-8-sig")
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for item in records:
                mask = df["Source.Wave"].eq(item["wave"]) & df["Variable.Name"].str.lower().eq(item["code"]) & df["epcf"].str.lower().eq("c")
                if int(mask.sum()) != 1:
                    raise SystemExit(f"Expected one target in {rel}: {item['wave']}/{item['code']}")
                for idx in df.index[mask]:
                    row = df.loc[idx].to_dict()
                    update_row(row, item)
                    for key, value in row.items():
                        if key in df.columns:
                            df.at[idx, key] = value
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            by_key = {(x["wave"], x["code"]): x for x in records}
            updated = 0
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                if key in by_key and str(row.get("epcf", "")).lower() == "c":
                    update_row(row, by_key[key])
                    updated += 1
            if updated != len(records):
                raise SystemExit(f"Expected {len(records)} rows in {rel}; updated {updated}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Reviewed {len(records)} condition/event age metadata fields; no Codebook sample summaries copied.")


if __name__ == "__main__":
    main()
