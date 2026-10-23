"""Apply official 2018 HA004 amount units and slot-routing caveats."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
Q = "CHARLS_2018_Questionnaire_extracted.txt"
CB = "CHARLS_2018_Codebook_extracted.txt"
TOTAL = {f"ha004_w4_1_{slot}_" for slot in range(1, 8)}
UNIT = {f"ha004_w4_2_{slot}_" for slot in range(1, 6)}
FIELDS = {("2018", code): "total" for code in TOTAL} | {("2018", code): "unit" for code in UNIT}
CATALOG_FIELDS = ("Concept.Unit.Candidates", "Unit", "Value.Labels", "Value.Label.Source", "Value.Label.Review", "Harmonization.Status")


def metadata(code: str) -> dict[str, str]:
    kind = FIELDS[("2018", code.lower())]
    is_total = kind == "total"
    unit = "10,000 Yuan" if is_total else "1,000 Yuan/square metre"
    measure = "total property value" if is_total else "unit-area property value"
    question_code = "HA004_W4_1" if is_total else "HA004_W4_2"
    caveat = (
        f"Official 2018 HA&I questionnaire asks the current market {measure} for the indexed household property, "
        f"reported in {unit}. The paired HA004 selector for this same slot determines total-price versus unit-price "
        "format. Keep property slots separate; these are household-property records, not stable person-level property IDs. "
        "Do not combine total price with unit-area price, sum slots into net worth, or infer a missing format from the amount. "
        "Preserve routing, refusal/don't-know and bracket semantics; Codebook summary extrema are not analytic limits. "
        "Verify special codes and eligible denominator in the authorized release before modeling."
    )
    status = f"official 2018 questionnaire and Codebook identify {measure}; continuous amount in {unit}; no discrete labels"
    source = f"sources_official/{Q}; sources_official/{CB}"
    return {
        "Concept.Unit.Candidates": unit,
        "Unit": unit,
        "Value.Labels": "",
        "Value.Label.Source": source,
        "Value.Label.Review": status,
        "Harmonization.Status": caveat,
        "candidate_concept_units": unit,
        "value_labels": "",
        "value_label_source": source,
        "value_label_review": status,
        "harmonization_status": caveat,
        "Caveat": caveat,
        "unit": unit,
        "construct": f"2018 household property {measure} by indexed property slot ({question_code})",
        "caveat": caveat,
    }


def update_csv(path: Path, wave_col: str, code_col: str, columns: tuple[str, ...]) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r[wave_col]), str(r[code_col]).lower()) in FIELDS, axis=1)
    found = set(zip(df.loc[selected, wave_col], df.loc[selected, code_col].str.lower()))
    if found != set(FIELDS):
        raise ValueError(f"{path}: source field coverage mismatch; missing={sorted(set(FIELDS)-found)}")
    for i in df.index[selected]:
        row = metadata(str(df.at[i, code_col]))
        for column in columns:
            df.at[i, column] = row[column]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    selected = [r for r in rows if (str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower()) in FIELDS]
    found = {(str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) for r in selected}
    if found != set(FIELDS):
        raise ValueError(f"{path}: source field coverage mismatch; missing={sorted(set(FIELDS)-found)}")
    for row in selected:
        row.update(metadata(str(row["Variable.Name"])))
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(selected)


def main() -> None:
    q = (ROOT / "sources_official" / Q).read_text(encoding="utf-8", errors="ignore").casefold()
    cb = (ROOT / "sources_official" / CB).read_text(encoding="utf-8", errors="ignore").casefold()
    if "10,000 yuan" not in q or "1,000 yuan/square meter" not in q or "total value for house[7]" not in cb or "unit value for house[5]" not in cb:
        raise ValueError("official questionnaire/Codebook verification failed for HA004 unit or slot coverage")
    n = update_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv", "Source.Wave", "Variable.Name", CATALOG_FIELDS)
    for path in (ROOT / "audit/ep_concept_source_crosswalk_v1.csv",):
        n += update_csv(path, "Wave", "Source.Code", ("Unit", "Caveat"))
    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json"):
        n += update_json(path)
    housing_path = ROOT / "site-prototype/dist/housing_catalog_v1.json"
    housing = json.loads(housing_path.read_text(encoding="utf-8"))
    selected = [r for r in housing if (str(r.get("wave", "")), str(r.get("code", "")).lower()) in FIELDS]
    found = {(str(r["wave"]), str(r["code"]).lower()) for r in selected}
    if found != set(FIELDS):
        raise ValueError(f"{housing_path}: source field coverage mismatch; missing={sorted(set(FIELDS)-found)}")
    for row in selected:
        row.update(metadata(str(row["code"])))
    selectors = [r for r in housing if str(r.get("wave", "")) == "2018" and str(r.get("code", "")).lower() in {f"ha004_w4_{slot}_" for slot in range(1, 8)}]
    for row in selectors:
        row.update({
            "value_labels": "1=Total Value; 2=Unit Value",
            "value_label_source": f"sources_official/{Q}; sources_official/{CB}",
            "value_label_status": "official questionnaire and Codebook response-format categories; frequencies omitted",
            "mapping_status": "C measurement metadata; response-format selector, not an exposure",
            "construct": "household property total-price versus unit-price response-format selector by indexed slot",
            "caveat": "Use only to interpret the corresponding same-slot HA004 amount. Total price and unit-area price have incompatible units and must remain separate.",
        })
    if len(selectors) != 7:
        raise ValueError(f"{housing_path}: expected seven HA004 format selectors, found {len(selectors)}")
    housing_path.write_text(json.dumps(housing, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n += len(selected)
    print(f"Applied official 2018 HA004 units and slot caveats to {n} catalog rows; no participant values or frequencies included.")


if __name__ == "__main__":
    main()
