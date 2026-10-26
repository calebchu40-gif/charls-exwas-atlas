"""Validate prepared private CHARLS wave tables and emit disclosure-safe QA."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
import pyreadstat
from project_paths import QA_OUTPUT_DIR, require_private_path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def missing_required_sample_flags(wave: str, column_names: list[str]) -> list[str]:
    """List wave-specific sample flags required to gate prepared tables."""
    required = {"crosssection", "longitudinal"} if wave == "2013" else set()
    available = {name.lower() for name in column_names}
    return sorted(required - available)


def source_record_status(wave: str, record: dict | None) -> str:
    """Check whether a prepared table records its local source-file identities.

    Local hashes document bytes only; they do not authenticate an official
    release. Wave 1 additionally requires hashes for the separate PSU, Weight,
    and Blood files because those are distinct CHARLS release items.
    """
    if not isinstance(record, dict):
        return "source_record_missing"
    sources = record.get("source_inputs")
    if not isinstance(sources, dict):
        sources = {}
    archive = record.get("source_archive") or sources.get("all_data_archive")
    required = {"all_data_archive": archive}
    if wave == "2011":
        required.update({role: sources.get(role) for role in ("psu", "weight", "blood")})

    for role, source in required.items():
        if not isinstance(source, dict):
            return f"missing_{role}_source_record"
        if not str(source.get("filename", "")).strip():
            return f"invalid_{role}_source_record"
        try:
            if int(source.get("bytes", 0)) <= 0:
                return f"invalid_{role}_source_record"
        except (TypeError, ValueError):
            return f"invalid_{role}_source_record"
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(source.get("sha256", ""))):
            return f"invalid_{role}_source_record"
    return "local_source_hashes_recorded_official_identity_unverified"


def get_match_rate_0_to_1(record):
    """Read the current field name or legacy misnamed proportion field."""
    value = record.get("match_rate_0_to_1")
    if value is None or pd.isna(value):
        value = record.get("match_pct_of_base_nonmissing")
    return None if value is None or pd.isna(value) else float(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--output-dir", type=Path, default=QA_OUTPUT_DIR,
                    help="Private local directory for validation reports; defaults outside synchronized folders")
    ap.add_argument("--manifest", type=Path,
                    help="Private prepared_data_manifest.json; defaults beside --data-dir")
    args = ap.parse_args()
    args.data_dir = require_private_path(args.data_dir)
    args.output_dir = require_private_path(args.output_dir)
    manifest_path = require_private_path(args.manifest or (args.data_dir / "prepared_data_manifest.json"))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        manifest = {}
    manifest_waves = {
        str(item.get("wave")): item for item in manifest.get("waves", [])
        if isinstance(item, dict) and item.get("wave") is not None
    } if isinstance(manifest, dict) else {}
    rows, module_rows = [], []
    for wave in ("2011", "2013", "2015", "2018", "2020"):
        f = args.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        data, _ = pyreadstat.read_dta(str(f), usecols=["ID", "wave"])
        _, meta = pyreadstat.read_dta(str(f), metadataonly=True)
        id_missing = int(data.ID.isna().sum())
        id_duplicate = int(data.ID.dropna().duplicated().sum())
        wave_vals = sorted(data.wave.dropna().unique().tolist())
        required_sample_flags = {"crosssection", "longitudinal"} if wave == "2013" else set()
        missing_sample_flags = missing_required_sample_flags(wave, meta.column_names)
        provenance_status = source_record_status(wave, manifest_waves.get(wave))
        row = {"wave": wave, "rows": len(data), "columns": meta.number_columns,
               "ID_missing_rows": id_missing, "duplicate_ID_rows": id_duplicate,
               "wave_values": ",".join(map(str, wave_vals)), "file_bytes": f.stat().st_size,
               "sha256": sha256(f),
               "required_sample_flags": ";".join(sorted(required_sample_flags)),
               "missing_required_sample_flags": ";".join(missing_sample_flags),
               "source_record_status": provenance_status,
               "readback": "PASS"}
        if id_missing or id_duplicate or wave_vals != [float(wave)] or missing_sample_flags:
            row["readback"] = "CHECK"
        rows.append(row)
        qf = args.data_dir / f"merge_qa_{wave}.csv"
        q = pd.read_csv(qf, encoding="utf-8-sig")
        for rec in q.to_dict("records"):
            module_rows.append({"wave": wave, "module": rec.get("module"),
                                "merge_key": rec.get("merge_key"),
                                "source_rows": rec.get("source_rows"),
                                "matched_base_rows": rec.get("matched_base_rows"),
                                "match_rate_0_to_1": get_match_rate_0_to_1(rec),
                                "note": rec.get("other_id_mismatch_counts")})

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "prepared_wave_validation_v1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(module_rows).to_csv(out / "prepared_module_merge_qa_v1.csv", index=False, encoding="utf-8-sig")
    (out / "prepared_wave_validation_v1.json").write_text(
        json.dumps({"tables": rows, "all_readback_pass": all(r["readback"] == "PASS" for r in rows),
                    "local_source_hash_records_complete": all(
                        r["source_record_status"] == "local_source_hashes_recorded_official_identity_unverified"
                        for r in rows
                    ),
                    "official_source_identity_verified_by_this_script": False,
                    "privacy": "aggregate QA only; no participant values or IDs included"},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    for row in rows:
        print(row["wave"], row["rows"], row["columns"], row["ID_missing_rows"],
              row["duplicate_ID_rows"], row["readback"], row["source_record_status"])


if __name__ == "__main__":
    main()
