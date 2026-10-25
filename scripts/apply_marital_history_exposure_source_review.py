"""Propagate official source review to the four new marriage-history E fields."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MAP = AUDIT / "marital_history_exposure_crosswalk_v1.csv"


def propagate() -> None:
    mapping = pd.read_csv(MAP, dtype=str, encoding="utf-8-sig").fillna("")
    codes = {("2011", "be007"), ("2011", "be008"), ("2013", "be009_1"), ("2013", "be009_2")}
    targets = {(r.wave, r.code.lower(), r.module): r._asdict() for r in mapping.itertuples(index=False) if (r.wave, r.code.lower()) in codes}
    if len(targets) != 4:
        raise SystemExit(f"Expected four reviewed marriage-history E mappings; found {len(targets)}")
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists(): continue
        count = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for (wave, code, module), item in targets.items():
                mask = df["Source.Wave"].eq(wave) & df["Variable.Name"].str.lower().eq(code) & df["Data.File.Name"].eq(module) & df["epcf"].str.lower().eq("e")
                if not mask.any(): continue
                df.loc[mask, "category"] = "social determinants"
                df.loc[mask, "subcategory"] = "marital history and marriage transfers"
                df.loc[mask, "Candidate.Status"] = item["mapping_status"]
                df.loc[mask, "Harmonization.Status"] = item["value_semantics"] + " " + item["caveat"]
                df.loc[mask, "Review.Flag"] = item["caveat"] + "; documented source mapping is a candidate only; not an approved test variable"
                df.loc[mask, "Value.Labels"] = item["value_labels"]
                df.loc[mask, "Value.Label.Source"] = item["value_label_source"]
                df.loc[mask, "Value.Label.Review"] = item["value_label_status"]
                count += int(mask.sum())
            if count != 4: raise SystemExit(f"Expected four E mappings in {rel}; updated {count}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            rows = json.loads(path.read_text(encoding="utf-8"))
            for row in rows:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")))
                if key not in targets or str(row.get("epcf", "")).lower() != "e": continue
                item = targets[key]
                row.update({"category": "social determinants", "subcategory": "marital history and marriage transfers", "Candidate.Status": item["mapping_status"], "Harmonization.Status": item["value_semantics"] + " " + item["caveat"], "Review.Flag": item["caveat"] + "; documented source mapping is a candidate only; not an approved test variable", "Value.Labels": item["value_labels"], "Value.Label.Source": item["value_label_source"], "Value.Label.Review": item["value_label_status"]})
                count += 1
            if count != 4: raise SystemExit(f"Expected four E mappings in {rel}; updated {count}")
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Propagated official questionnaire/Codebook review to four marriage-history E rows; routed denominators retained.")


if __name__ == "__main__": propagate()
