"""Build a protected Wave 2 age-input table with source-resolved DOB routes.

The script does not calculate age and never writes respondent-level fields
outside the configured protected CHARLS workspace. For a confirmed preloaded
Wave 2 DOB, it resolves the calendar only through an exact transformed-ID and
date match to the official Wave 1 respondent record; discordant/unmatched rows
remain explicitly unresolved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat

CODE_SCRIPTS = Path.cwd() / "scripts"
if CODE_SCRIPTS.is_dir():
    sys.path.insert(0, str(CODE_SCRIPTS))

from audit_2013_weights_intake import verify_official_weights_archive
from prepare_charls_wave_tables import normalize_key
from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, QA_OUTPUT_DIR, require_private_path


W2_COLS = ["ID", "ba001_w2_1", "zba002_1", "zba002_2", "zba002_3",
           "ba002_1", "ba002_2", "ba002_3", "ba003", "ba004"]
W1_COLS = ["ID", "householdID", "ba002_1", "ba002_2", "ba002_3", "ba003", "ba004"]
WEIGHT_COLS = ["ID", "iyear", "imonth"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def protected(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"Input/output must remain under protected root: {resolved}")
    return resolved


def read_required(path: Path, columns: list[str]) -> pd.DataFrame:
    frame, meta = pyreadstat.read_dta(str(path), usecols=columns)
    absent = sorted(set(columns) - set(frame.columns))
    if absent:
        raise ValueError(f"{path.name} is missing required fields: {absent}")
    return frame


def transform_wave1_id(household_id: pd.Series, individual_id: pd.Series) -> pd.Series:
    hh = normalize_key(household_id)
    person = normalize_key(individual_id)
    if not hh.str.fullmatch(r"\d{9}").fillna(False).all():
        raise ValueError("Wave 1 householdID does not uniformly match the documented 9-digit form")
    if not person.str.fullmatch(r"\d{11}").fillna(False).all():
        raise ValueError("Wave 1 ID does not uniformly match the documented 11-digit form")
    return hh + "0" + person.str[-2:]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weights-archive", type=Path, required=True)
    ap.add_argument("--weights-dta", type=Path, required=True)
    ap.add_argument("--wave1", type=Path, default=WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta")
    ap.add_argument("--wave2", type=Path, default=WAVE_DATA_DIR / "CHARLS_wave2013_person_analytic.dta")
    ap.add_argument("--prepared-manifest", type=Path,
                    default=WAVE_DATA_DIR / "prepared_data_manifest.json")
    ap.add_argument("--output", type=Path,
                    default=WAVE_DATA_DIR / "CHARLS_wave2013_age_inputs_source_bound.dta")
    ap.add_argument("--qa-output", type=Path,
                    default=QA_OUTPUT_DIR / "wave2_age_input_source_reconciliation_private.json")
    args = ap.parse_args()
    for name in ("weights_archive", "weights_dta", "wave1", "wave2", "prepared_manifest", "output", "qa_output"):
        setattr(args, name, protected(getattr(args, name)))

    archive_sha1, member = verify_official_weights_archive(args.weights_archive)
    with zipfile.ZipFile(args.weights_archive) as zf, zf.open(member) as source:
        digest = hashlib.sha256()
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    if sha256_file(args.weights_dta) != digest.hexdigest():
        raise ValueError("Weights.dta differs from its verified official ZIP member")

    manifest = json.loads(args.prepared_manifest.read_text(encoding="utf-8"))
    entries = {str(item.get("wave")): item for item in manifest.get("waves", [])}
    for wave, path in (("2011", args.wave1), ("2013", args.wave2)):
        entry = entries.get(wave, {}).get("prepared_output", {})
        if entry.get("filename") != path.name or entry.get("sha256") != sha256_file(path):
            raise ValueError(f"Wave {wave} prepared table does not match its protected manifest")

    w2 = read_required(args.wave2, W2_COLS)
    w1 = read_required(args.wave1, W1_COLS)
    weights = read_required(args.weights_dta, WEIGHT_COLS)
    weights_missing_id_rows = 0
    for label, frame in (("Wave 1", w1), ("Wave 2", w2)):
        frame["ID"] = normalize_key(frame["ID"])
        if frame["ID"].isna().any() or frame["ID"].duplicated().any():
            raise ValueError(f"{label} ID is missing or nonunique")
    weights["ID"] = normalize_key(weights["ID"])
    weights_missing_id_rows = int(weights["ID"].isna().sum())
    # The official release contains a small number of records with no person ID.
    # They cannot be respondent-linked; retain their count in protected QA only.
    weights = weights.loc[weights["ID"].notna()].copy()
    if weights["ID"].duplicated().any():
        raise ValueError("Official Weights person IDs are nonunique")
    if weights["iyear"].isna().any() or weights["imonth"].isna().any():
        # Preserve source missingness; do not silently create an interview date.
        pass

    w1["wave2_id_from_official_transform"] = transform_wave1_id(w1["householdID"], w1["ID"])
    if w1["wave2_id_from_official_transform"].duplicated().any():
        raise ValueError("Official Wave 1 ID transformation creates duplicate Wave 2 keys")
    base = w1.rename(columns={c: f"{c}_w1" for c in W1_COLS})
    base = base.rename(columns={"wave2_id_from_official_transform": "ID"})
    merged = w2.merge(base, on="ID", how="left", validate="one_to_one", indicator="_w1_match")
    merged = merged.merge(weights[WEIGHT_COLS], on="ID", how="left", validate="one_to_one",
                          indicator="_weight_match")

    def same_date(row: pd.Series) -> bool:
        fields = [("zba002_1", "ba002_1_w1"), ("zba002_2", "ba002_2_w1"),
                  ("zba002_3", "ba002_3_w1")]
        for a, b in fields:
            x = pd.to_numeric(pd.Series([row[a]]), errors="coerce").iloc[0]
            y = pd.to_numeric(pd.Series([row[b]]), errors="coerce").iloc[0]
            if pd.isna(x) or pd.isna(y) or float(x) != float(y):
                return False
        return True

    route = pd.to_numeric(merged["ba001_w2_1"], errors="coerce")
    matched = merged["_w1_match"].eq("both")
    agreement = merged.apply(same_date, axis=1)
    corrected = route.eq(2)
    confirmed = route.eq(1)
    merged["dob_route_status"] = "unresolved_route_or_missing"
    merged.loc[corrected, "dob_route_status"] = "wave2_corrected_date_use_wave2_calendar"
    merged.loc[confirmed & matched & agreement, "dob_route_status"] = "preload_confirmed_wave1_exact_date_calendar_linked"
    merged.loc[confirmed & matched & ~agreement, "dob_route_status"] = "preload_confirmed_date_disagrees_with_wave1"
    merged.loc[confirmed & ~matched, "dob_route_status"] = "preload_confirmed_no_wave1_match"

    merged["dob_year_source"] = pd.NA
    merged["dob_month_source"] = pd.NA
    merged["dob_day_source"] = pd.NA
    merged["dob_calendar_source"] = pd.NA
    # A respondent-confirmed preload is usable as a birth-date candidate even
    # when its original calendar cannot be reconciled; retain the calendar as
    # missing so the downstream interval method can use only the year.
    merged.loc[confirmed, "dob_year_source"] = merged.loc[confirmed, "zba002_1"]
    merged.loc[confirmed, "dob_month_source"] = merged.loc[confirmed, "zba002_2"]
    merged.loc[confirmed, "dob_day_source"] = merged.loc[confirmed, "zba002_3"]
    merged.loc[corrected, "dob_year_source"] = merged.loc[corrected, "ba002_1"]
    merged.loc[corrected, "dob_month_source"] = merged.loc[corrected, "ba002_2"]
    merged.loc[corrected, "dob_day_source"] = merged.loc[corrected, "ba002_3"]
    merged.loc[corrected, "dob_calendar_source"] = merged.loc[corrected, "ba003"]
    linked = confirmed & matched & agreement
    merged.loc[linked, "dob_calendar_source"] = merged.loc[linked, "ba003_w1"]
    merged["age_fallback_ba004_w2"] = merged["ba004"]
    merged["age_derivation_status"] = "not_calculated_conversion_and_partial_date_rules_pending"
    merged["interview_year_source"] = merged["iyear"]
    merged["interview_month_source"] = merged["imonth"]

    keep = ["ID", "dob_route_status", "dob_year_source", "dob_month_source", "dob_day_source",
            "dob_calendar_source", "age_fallback_ba004_w2", "interview_year_source",
            "interview_month_source", "age_derivation_status"]
    out = merged[keep]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    pyreadstat.write_dta(out, str(tmp), version=15,
                         file_label="Protected Wave 2 source-resolved age inputs; age not calculated")
    os.chmod(tmp, 0o600)
    os.replace(tmp, args.output)
    counts = merged["dob_route_status"].value_counts(dropna=False).to_dict()
    qa = {
        "status": "source_reconciliation_complete_age_not_calculated",
        "privacy": "aggregate QA only; no IDs, row-level dates, or participant values in this report",
        "official_weights_archive_sha1": archive_sha1,
        "weights_archive_member": Path(member).name,
        "weights_dta_sha256": sha256_file(args.weights_dta),
        "wave1_source_sha256": sha256_file(args.wave1),
        "wave2_source_sha256": sha256_file(args.wave2),
        "prepared_manifest_sha256": sha256_file(args.prepared_manifest),
        "output_sha256": sha256_file(args.output),
        "wave2_rows": int(len(merged)),
        "route_status_counts": {str(k): int(v) for k, v in counts.items()},
        "interview_year_missing": int(merged["iyear"].isna().sum()),
        "interview_month_missing": int(merged["imonth"].isna().sum()),
        "wave1_transform_match_rows": int(matched.sum()),
        "wave1_exact_dob_agreement_rows": int((matched & agreement).sum()),
        "official_weights_rows_without_person_id_excluded_from_join": weights_missing_id_rows,
        "next_gate": "verify date special-missing semantics; validate official lunar converter parity; prespecify partial-date and fallback rules",
    }
    args.qa_output.parent.mkdir(parents=True, exist_ok=True)
    args.qa_output.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(args.qa_output, 0o600)
    print("Wave 2 source-resolved age input preparation complete; age not calculated; QA remains protected.")


if __name__ == "__main__":
    main()
