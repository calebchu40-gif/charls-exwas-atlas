"""Apply wave-specific numeric building-floor and entrance-step measures."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    **{(w, "i008"): ("building floor number", "storeys", "Questionnaire asks which story the residence is on. Retain as an ordinal/numeric floor position; do not infer a harmonized height dose from Codebook extrema." ) for w in ("2011", "2013", "2015", "2018")},
    ("2020", "i006_1"): ("above-ground floor number", "storeys", "2020 records the above-ground storey in a separate numeric field; keep distinct from underground floor count."),
    ("2020", "i006_2"): ("underground floor number", "storeys", "2020 records the underground storey in a separate numeric field; retain its route and do not combine as a signed floor without an explicit rule."),
    ("2020", "i006"): ("above-ground versus underground residence selector", "", "2020 records whether the residence is on the ground/above-ground route or underground; the numeric floor count is in the routed child field, so retain selector and count separately."),
    ("2020", "i010"): ("steps to main entrance", "steps", "Counts steps to the household flat's main entrance; this is an access-barrier measure, not a respondent mobility test. Soft-check prompts are not cutoffs."),
}
SOURCES = {
    "2011": "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}


def apply(row: dict, wave: str, code: str) -> None:
    concept, unit, detail = FIELDS[(wave, code.lower())]
    source = f"sources_official/{SOURCES[wave]}"
    selector = (wave, code.lower()) == ("2020", "i006")
    labels = "1=On the ground; 2=Underground" if selector else ""
    status = f"official {wave} questionnaire identifies a wave-specific categorical {concept}; preserve alongside routed count fields" if selector else f"official {wave} questionnaire identifies a numeric {concept}; continuous/ordinal measure without discrete value labels"
    caveat = detail + " Verify authorized-release special values, skip routes, residence/respondent linkage and missingness before modeling. Questionnaire hard/soft checks do not establish valid analytic ranges. Cross-wave measurement equivalence is unapproved."
    row.update({
        "Concept.Unit.Candidates": unit, "Unit": unit, "Value.Labels": labels,
        "Value.Label.Source": source, "Value.Label.Review": status,
        "Harmonization.Status": caveat, "candidate_concept_units": unit,
        "value_labels": labels, "value_label_source": source,
        "value_label_review": status, "harmonization_status": caveat,
    })


def validate_sources() -> None:
    for wave, filename in SOURCES.items():
        text = (ROOT / "sources_official" / filename).read_text(encoding="utf-8", errors="ignore").casefold()
        codes = [c for (w, c) in FIELDS if w == wave]
        for code in codes:
            if code not in text:
                raise ValueError(f"questionnaire missing {wave} {code}")
        phrase = "steps" if wave == "2020" else "story" if wave != "2020" else "storey"
        if phrase not in text and wave != "2011":
            raise ValueError(f"questionnaire lacks expected building/access wording for {wave}")


def update_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, "Source.Wave"], df.loc[selected, "Variable.Name"].str.lower()))
    if seen != set(FIELDS):
        raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    cols = ("Concept.Unit.Candidates", "Unit", "Value.Labels", "Value.Label.Source", "Value.Label.Review", "Harmonization.Status")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        apply(row, str(row["Source.Wave"]), str(row["Variable.Name"]).lower())
        for key in cols:
            df.at[idx, key] = row[key]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_food_crosswalk_csv(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["wave"]), str(r["code"]).lower()) in FIELDS, axis=1)
    found = set(zip(df.loc[selected, "wave"], df.loc[selected, "code"].str.lower()))
    if found != set(FIELDS):
        raise ValueError(f"{path}: missing={sorted(set(FIELDS)-found)}, unexpected={sorted(found-set(FIELDS))}")
    reviewed = {}
    for idx in df.index[selected]:
        wave, code = str(df.at[idx, "wave"]), str(df.at[idx, "code"]).lower()
        row = {}
        apply(row, wave, code)
        df.at[idx, "mapping_status"] = row["Value.Label.Review"]
        df.at[idx, "caveat"] = row["Harmonization.Status"]
        reviewed[(wave, code)] = {"mapping_status": row["Value.Label.Review"], "caveat": row["Harmonization.Status"]}
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return reviewed


def update_final_source_index(path: Path, reviewed: dict[tuple[str, str], dict[str, str]]) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = (
        df["Source.File"].eq("audit/food_environment_crosswalk_v1.csv")
        & df.apply(lambda r: (str(r["Wave"]), str(r["Source.Code"]).lower()) in reviewed, axis=1)
    )
    found = {(str(r["Wave"]), str(r["Source.Code"]).lower()) for _, r in df[selected].iterrows()}
    if found != set(reviewed):
        raise ValueError(f"{path}: housing index mismatch; missing={sorted(set(reviewed)-found)}")
    for idx in df.index[selected]:
        key = (str(df.at[idx, "Wave"]), str(df.at[idx, "Source.Code"]).lower())
        df.at[idx, "Mapping.Status"] = reviewed[key]["mapping_status"]
        df.at[idx, "Caveat"] = reviewed[key]["caveat"]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if rows and "source_fields" in rows[0]:
        entries = [f for item in rows for f in item["source_fields"]]
        selected = [f for f in entries if (str(f.get("wave", "")), str(f.get("code", "")).lower()) in FIELDS]
        seen = {(str(f["wave"]), str(f["code"]).lower()) for f in selected}
        if seen != set(FIELDS):
            raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
        for f in selected:
            row = {}
            apply(row, str(f["wave"]), str(f["code"]).lower())
            f.update({"unit": row["Unit"], "value_labels": "", "value_label_status": row["Value.Label.Review"], "value_label_source": row["Value.Label.Source"], "mapping_status": row["Value.Label.Review"], "caveat": row["Harmonization.Status"], "note": row["Value.Label.Review"] + " " + row["Harmonization.Status"]})
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return len(selected)
    selected = [r for r in rows if (str(r.get(wave_key, "")), str(r.get(code_key, "")).lower()) in FIELDS]
    seen = {(str(r[wave_key]), str(r[code_key]).lower()) for r in selected}
    if not seen:
        return 0
    if seen != set(FIELDS):
        raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for r in selected:
        row = {}
        apply(row, str(r[wave_key]), str(r[code_key]).lower())
        r.update({k: v for k, v in row.items() if k in ("Concept.Unit.Candidates", "Unit", "Value.Labels", "Value.Label.Source", "Value.Label.Review", "Harmonization.Status", "candidate_concept_units", "value_labels", "value_label_source", "value_label_review", "harmonization_status")})
        if wave_key == "wave":
            r.update({"unit": row["Unit"], "value_labels": "", "value_label_status": row["Value.Label.Review"], "value_label_source": row["Value.Label.Source"], "mapping_status": row["Value.Label.Review"], "caveat": row["Harmonization.Status"]})
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n" if wave_key == "wave" else json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(selected)


def main() -> None:
    validate_sources()
    reviewed = update_food_crosswalk_csv(ROOT / "audit/food_environment_crosswalk_v1.csv")
    update_final_source_index(ROOT / "audit/ep_concept_source_crosswalk_v1.csv", reviewed)
    paths = [
        (ROOT / "audit/charls_atlas_candidate_fields_v0.csv", "csv"),
        (ROOT / "audit/charls_atlas_candidate_fields_v0.json", "source"),
        (ROOT / "site-prototype/dist/catalog.json", "source"),
        (ROOT / "site-prototype/dist/catalog_e.json", "source"),
        (ROOT / "site-prototype/dist/food_environment_v1.json", "food"),
    ]
    count = sum(update_csv(p) if kind == "csv" else update_json(p, "wave", "code") if kind == "food" else update_json(p, "Source.Wave", "Variable.Name") for p, kind in paths)
    print(f"Applied wave-specific building-floor/access metadata to {count} metadata field rows; no participant values or frequencies included.")


if __name__ == "__main__":
    main()
