"""Propagate the audited 2011 FM055 classification hold to catalog outputs."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CODES = {"fm055_gb", "fm055_isco", "fm055_indc"}
STATUS = "candidate only; 2011 FM055 classification edition and lookup unverified; DO NOT ANALYZE until verified"
CAVEAT = "2011 FM055 coded child field only; keep GB occupation, ISCO occupation, and industry separate. Coding edition and official category lookup remain unverified; do not analyze or publish category frequencies until verified."


def main():
    crosswalk = pd.read_csv(AUDIT / "work_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    reviewed = crosswalk[(crosswalk.wave == "2011") & crosswalk.code.str.lower().isin(CODES)]
    if set(reviewed.code.str.lower()) != CODES:
        raise SystemExit(f"Expected exactly the three 2011 FM055 coded child fields; found {sorted(reviewed.code.str.lower())}")
    status_by_code = {r.code.lower(): r.mapping_status for r in reviewed.itertuples()}
    caveat_by_code = {r.code.lower(): r.caveat for r in reviewed.itertuples()}

    for name in ("charls_atlas_candidate_fields_v0.csv",):
        path = AUDIT / name
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
        mask = df["Source.Wave"].astype(str).eq("2011") & df["Variable.Name"].astype(str).str.lower().isin(CODES)
        if int(mask.sum()) != 3:
            raise SystemExit(f"{name}: expected 3 exact wave-field rows, found {int(mask.sum())}")
        df.loc[mask, "Concept.Mapping.Status"] = df.loc[mask, "Variable.Name"].str.lower().map(status_by_code)
        df.loc[mask, "Concept.Mapping.Caveat"] = df.loc[mask, "Variable.Name"].str.lower().map(caveat_by_code)
        df.loc[mask, "Review.Flag"] = "DO NOT ANALYZE until the 2011 FM055 occupation/industry coding edition and official category lookup are verified"
        df.to_csv(path, index=False, encoding="utf-8-sig")

    targets = [
        AUDIT / "charls_atlas_candidate_fields_v0.json",
        ROOT / "site-prototype" / "dist" / "catalog.json",
        ROOT / "site-prototype" / "dist" / "catalog_e.json",
    ]
    for path in targets:
        rows = json.loads(path.read_text(encoding="utf-8"))
        count = 0
        for row in rows:
            code = str(row.get("Variable.Name", "")).lower()
            if str(row.get("Source.Wave", "")) != "2011" or code not in CODES:
                continue
            row["Concept.Mapping.Status"] = status_by_code[code]
            row["Concept.Mapping.Caveat"] = caveat_by_code[code]
            row["Review.Flag"] = "DO NOT ANALYZE until the 2011 FM055 occupation/industry coding edition and official category lookup are verified"
            for field, value in (("concept_mapping_statuses", status_by_code[code]), ("concept_mapping_caveats", caveat_by_code[code])):
                if field in row:
                    row[field] = value
            count += 1
        if count != 3:
            raise SystemExit(f"{path.name}: expected 3 exact wave-field rows, found {count}")
        # These generated catalogue shards are deliberately compact; retain
        # their established format so a three-row review does not reformat
        # every field in a multi-megabyte JSON file.
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    print("Propagated the 2011 FM055 classification hold to 3 field rows in CSV/JSON source and site catalogs.")


if __name__ == "__main__":
    main()
