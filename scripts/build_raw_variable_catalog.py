"""Build a metadata-only variable inventory from CHARLS wave archives.

No participant-level records are exported. DTA archives are extracted only to
temporary directories so Pyreadstat can read Stata metadata; temporary files
are removed automatically.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pyreadstat


WAVE_ARCHIVES = {
    "2011": ("rar", "household_and_community_questionnaire_data.rar"),
    "2013": ("zip", "CHARLS2013_Dataset.zip"),
    "2015": ("zip", "CHARLS2015r.zip"),
    "2018": ("zip", "CHARLS2018r.zip"),
    "2020": ("zip", "CHARLS2020r.zip"),
}


def sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def inspect_dta(path: Path, wave: str, module: str, origin: str):
    _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
    labels = meta.column_labels or [""] * len(meta.column_names)
    for name, label in zip(meta.column_names, labels):
        yield {
            "wave": wave,
            "module": module,
            "variable": name,
            "variable_label": label or "",
            "module_rows": meta.number_rows,
            "module_columns": meta.number_columns,
            "source": origin,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path, help="CHARLS uploaded-data root")
    parser.add_argument("--out", required=True, type=Path, help="Output CSV")
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    raw = root / "原始数据+问卷2011~2020"
    rows = []
    archive_summary = []

    for wave, (kind, filename) in WAVE_ARCHIVES.items():
        archive = next((raw / wave).glob(filename))
        if kind == "zip":
            with zipfile.ZipFile(archive) as zf:
                bad_member = zf.testzip()
                if bad_member:
                    raise RuntimeError(f"ZIP integrity failure in {archive}: {bad_member}")
                members = [n for n in zf.namelist() if n.lower().endswith(".dta")]
                archive_summary.append({"wave": wave, "archive": archive.name, "sha1": sha1(archive),
                                        "integrity": "PASS", "dta_modules": len(members)})
                with tempfile.TemporaryDirectory(prefix=f"charls_{wave}_") as td:
                    tmp = Path(td)
                    for member in members:
                        dta = tmp / Path(member).name
                        dta.write_bytes(zf.read(member))
                        rows.extend(inspect_dta(dta, wave, dta.stem, archive.name))
        else:
            with tempfile.TemporaryDirectory(prefix="charls_2011_") as td:
                result = subprocess.run(["tar", "-xf", str(archive), "-C", td],
                                        capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(f"Cannot read RAR {archive}: {result.stderr}")
                modules = sorted(Path(td).rglob("*.dta"))
                archive_summary.append({"wave": wave, "archive": archive.name, "sha1": sha1(archive),
                                        "integrity": "ARCHIVE_READ_PASS", "dta_modules": len(modules)})
                for dta in modules:
                    rows.extend(inspect_dta(dta, wave, dta.stem, archive.name))
        # Baseline blood assays are a separate CHARLS release file, not the
        # household/community archive.
        if wave == "2011":
            blood = raw / wave / "Blood_20140429.dta"
            rows.extend(inspect_dta(blood, wave, "Blood_Assays", blood.name))

    # Harmonized releases are crosswalk references, not replacements for raw
    # wave data. Keep them distinguishable in the same catalog.
    for version in ("C", "D"):
        folder = raw / f"Harmonized_CHARLS_{version}"
        dta = next(folder.glob("H_CHARLS_*_Data.dta"))
        rows.extend(inspect_dta(dta, f"Harmonized_{version}", "Harmonized_All", dta.name))

    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["wave", "module", "variable", "variable_label", "module_rows", "module_columns", "source"]
    with out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary_path = out.with_name("raw_archive_module_summary.json")
    summary_path.write_text(json.dumps(archive_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"catalog_rows={len(rows)}")
    print(f"waves={json.dumps({w: sum(r['wave'] == w for r in rows) for w in WAVE_ARCHIVES}, ensure_ascii=False)}")
    print(f"out={out}")
    print(f"archive_summary={summary_path}")


if __name__ == "__main__":
    main()

