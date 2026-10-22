"""Validate prepared private CHARLS wave tables and emit disclosure-safe QA."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import pyreadstat


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    rows, module_rows = [], []
    for wave in ("2011", "2013", "2015", "2018", "2020"):
        f = args.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        data, _ = pyreadstat.read_dta(str(f), usecols=["ID", "wave"])
        _, meta = pyreadstat.read_dta(str(f), metadataonly=True)
        id_missing = int(data.ID.isna().sum())
        id_duplicate = int(data.ID.dropna().duplicated().sum())
        wave_vals = sorted(data.wave.dropna().unique().tolist())
        row = {"wave": wave, "rows": len(data), "columns": meta.number_columns,
               "ID_missing_rows": id_missing, "duplicate_ID_rows": id_duplicate,
               "wave_values": ",".join(map(str, wave_vals)), "file_bytes": f.stat().st_size,
               "sha256": sha256(f), "readback": "PASS"}
        if id_missing or id_duplicate or wave_vals != [float(wave)]:
            row["readback"] = "CHECK"
        rows.append(row)
        qf = args.data_dir / f"merge_qa_{wave}.csv"
        q = pd.read_csv(qf, encoding="utf-8-sig")
        for rec in q.to_dict("records"):
            module_rows.append({"wave": wave, "module": rec.get("module"),
                                "merge_key": rec.get("merge_key"),
                                "source_rows": rec.get("source_rows"),
                                "matched_base_rows": rec.get("matched_base_rows"),
                                "match_pct_of_base_nonmissing": rec.get("match_pct_of_base_nonmissing"),
                                "note": rec.get("other_id_mismatch_counts")})

    out = args.project_dir / "audit"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "prepared_wave_validation_v1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(module_rows).to_csv(out / "prepared_module_merge_qa_v1.csv", index=False, encoding="utf-8-sig")
    (out / "prepared_wave_validation_v1.json").write_text(
        json.dumps({"tables": rows, "all_readback_pass": all(r["readback"] == "PASS" for r in rows),
                    "privacy": "aggregate QA only; no participant values or IDs included"},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    for row in rows:
        print(row["wave"], row["rows"], row["columns"], row["ID_missing_rows"],
              row["duplicate_ID_rows"], row["readback"], row["sha256"])


if __name__ == "__main__":
    main()
