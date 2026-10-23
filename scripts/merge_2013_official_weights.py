"""Safely add official CHARLS 2013 sample flags/weights to a prepared table.

Run only on files in access-controlled local storage. The source file is the
official Wave 2 Weights.dta. By default this writes a separate DTA and an
aggregate-only QA report; it never changes the prepared source in place.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import pyreadstat

from prepare_charls_wave_tables import normalize_key
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path


REQUIRED_FLAGS = ("crosssection", "longitudinal")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def merge_official_weights(prepared: pd.DataFrame, weights: pd.DataFrame,
                           prepared_labels: dict[str, str] | None = None,
                           weight_labels: dict[str, str] | None = None):
    """Merge official Wave 2 flags by unique ID and return data plus aggregate QA."""
    if "ID" not in prepared or "ID" not in weights:
        raise ValueError("Both prepared table and Weights.dta must contain ID")
    names = {c.casefold(): c for c in weights.columns}
    missing = [flag for flag in REQUIRED_FLAGS if flag not in names]
    if missing:
        raise ValueError(f"Official 2013 Weights.dta is missing required flags: {missing}")

    base = prepared.copy()
    inc = weights.copy()
    base["ID"] = normalize_key(base["ID"])
    inc["ID"] = normalize_key(inc["ID"])
    if base["ID"].isna().any() or base["ID"].duplicated().any():
        raise ValueError("Prepared table IDs must be nonmissing and unique")
    if inc["ID"].isna().any() or inc["ID"].duplicated().any():
        raise ValueError("Official weights IDs must be nonmissing and unique")

    flag_cols = [names[f] for f in REQUIRED_FLAGS]
    weight_cols = [c for c in inc.columns if "weight" in c.casefold()]
    add_cols = list(dict.fromkeys(flag_cols + weight_cols))
    if not weight_cols:
        raise ValueError("Official Weights.dta has no weight variables")
    inc = inc[["ID"] + add_cols]

    # Existing weights can be retained only when all overlapping observed values
    # agree. Never silently overwrite a prepared value or alias a conflicting flag.
    for col in add_cols:
        if col not in base.columns:
            continue
        left = base.set_index("ID")[col]
        right = inc.set_index("ID")[col]
        common = left.index.intersection(right.index)
        lval, rval = left.loc[common], right.loc[common]
        both = lval.notna() & rval.notna()
        left_num = pd.to_numeric(lval.loc[both], errors="coerce")
        right_num = pd.to_numeric(rval.loc[both], errors="coerce")
        if left_num.notna().all() and right_num.notna().all():
            agrees = bool(((left_num - right_num).abs() <= 1e-12 + 1e-8 * right_num.abs()).all())
        else:
            agrees = lval.loc[both].astype(str).equals(rval.loc[both].astype(str))
        if not agrees:
            raise ValueError(f"Existing and official values conflict for {col}; no output written")
        # Fill holes from the official file, preserving existing nonmissing values,
        # then omit the duplicate incoming column to prevent suffix ambiguity.
        official_by_id = inc.set_index("ID")[col]
        base_ids = base["ID"]
        base[col] = base[col].where(base[col].notna(), official_by_id.reindex(base_ids).to_numpy())
        inc.drop(columns=col, inplace=True)

    merged = base.merge(inc, on="ID", how="left", validate="one_to_one",
                        suffixes=("", "__official"), indicator="_merge_status",
                        sort=False)
    if len(merged) != len(base) or not merged["_merge_status"].eq("both").all():
        raise ValueError("Not all prepared respondents matched; no output written")
    merged.drop(columns="_merge_status", inplace=True)
    if any(c.endswith("__official") for c in merged.columns):
        raise ValueError("Unexpected duplicate official columns; no output written")
    if merged["ID"].tolist() != base["ID"].tolist():
        raise ValueError("Merge changed respondent order; no output written")

    labels = dict(prepared_labels or {})
    for col, label in (weight_labels or {}).items():
        if col in merged and label and not labels.get(col):
            labels[col] = label
    flag_summary = {}
    for flag in flag_cols:
        values = merged[flag]
        flag_summary[flag] = {
            "nonmissing": int(values.notna().sum()),
            "missing": int(values.isna().sum()),
            "value_counts": {str(k): int(v) for k, v in values.value_counts(dropna=False).items()},
        }
    qa = {
        "wave": "2013", "prepared_rows": len(base),
        "weights_rows": len(inc), "matched_prepared_rows": len(merged),
        "match_rate": 1.0, "prepared_only_rows": 0,
        "official_weights_only_rows": int((~inc["ID"].isin(base["ID"])).sum()),
        "added_or_checked_variables": add_cols,
        "sample_flag_summary": flag_summary,
        "privacy": "aggregate QA only; no participant IDs or row-level values",
    }
    return merged, labels, qa


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weights", required=True, type=Path,
                    help="Official 2013 Weights.dta stored in private local storage")
    ap.add_argument("--prepared", type=Path,
                    default=WAVE_DATA_DIR / "CHARLS_wave2013_person_analytic.dta")
    ap.add_argument("--output", type=Path,
                    default=WAVE_DATA_DIR / "CHARLS_wave2013_person_analytic_with_official_sample_flags.dta")
    ap.add_argument("--qa-output", type=Path,
                    default=QA_OUTPUT_DIR / "charls_2013_official_weights_merge_qa.json")
    ap.add_argument("--replace-prepared", action="store_true",
                    help="After successful checks, atomically replace prepared input (backup retained)")
    args = ap.parse_args()
    for name in ("weights", "prepared", "output", "qa_output"):
        setattr(args, name, require_private_path(getattr(args, name)))
    if args.weights.resolve() == args.prepared.resolve():
        raise ValueError("Weights source and prepared input must be different files")
    if args.replace_prepared:
        args.output = args.prepared.with_name(args.prepared.stem + "_official_flags.tmp.dta")
        backup = args.prepared.with_name(args.prepared.stem + ".pre_official_flags_backup.dta")
        if backup.exists():
            raise FileExistsError(f"Refusing to replace prepared input because backup exists: {backup}")
    if args.output.resolve() == args.prepared.resolve():
        raise ValueError("Output cannot overwrite prepared input; use --replace-prepared")

    source, source_meta = pyreadstat.read_dta(str(args.weights))
    prepared, prepared_meta = pyreadstat.read_dta(str(args.prepared))
    labels, weight_labels = {}, {}
    for col, label in zip(prepared_meta.column_names, prepared_meta.column_labels or []):
        if label:
            labels[col] = label
    for col, label in zip(source_meta.column_names, source_meta.column_labels or []):
        if label:
            weight_labels[col] = label
    merged, labels, qa = merge_official_weights(prepared, source, labels, weight_labels)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_name(args.output.stem + ".write.tmp.dta")
    pyreadstat.write_dta(merged, str(temp), column_labels={k: v for k, v in labels.items() if k in merged},
                         version=15, file_label="CHARLS 2013 prepared respondent table with official weights")
    _, check = pyreadstat.read_dta(str(temp), metadataonly=True)
    if check.number_rows != len(merged) or check.number_columns != len(merged.columns):
        temp.unlink(missing_ok=True)
        raise RuntimeError("Read-back shape check failed; source input left unchanged")
    # Confirm key order and flags survived Stata serialization before publishing output.
    check_data, _ = pyreadstat.read_dta(str(temp), usecols=["ID", *REQUIRED_FLAGS])
    if check_data["ID"].astype("string").tolist() != merged["ID"].astype("string").tolist():
        temp.unlink(missing_ok=True)
        raise RuntimeError("Read-back respondent order check failed")
    os.replace(temp, args.output)
    qa.update({"source_file": args.weights.name, "source_sha256": sha256_file(args.weights),
               "output_file": args.output.name, "output_sha256": sha256_file(args.output),
               "prepared_source_sha256": sha256_file(args.prepared)})
    args.qa_output.parent.mkdir(parents=True, exist_ok=True)
    args.qa_output.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.replace_prepared:
        backup = args.prepared.with_name(args.prepared.stem + ".pre_official_flags_backup.dta")
        if backup.exists():
            raise FileExistsError(f"Refusing to overwrite existing backup: {backup}")
        os.replace(args.prepared, backup)
        os.replace(args.output, args.prepared)
        qa["replaced_prepared"] = True
        qa["backup_file"] = backup.name
        args.qa_output.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in qa.items() if k != "sample_flag_summary"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
