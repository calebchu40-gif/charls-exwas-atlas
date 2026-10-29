#!/usr/bin/env python3
"""Reconcile private historical pilot contrasts with the public metadata register.
Reads only pair/contrast keys; estimates and participant values are never accessed or emitted.
Writes aggregate-only QA to a caller-selected protected path.
"""
import argparse, csv, json
from pathlib import Path

KEYS = ("wave", "exposure_field_candidate", "phenotype_field_candidate", "contrast_id")
FILES = ("pilot_results_private.csv", "environment_extension_results_private.csv")

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def registered_key(row):
    return tuple((row.get(k) or "").strip() for k in KEYS)

def output_key(row):
    term = (row.get("term") or "").strip()
    if term == "water_yes" or (not term and (row.get("exposure_variable") or "").strip() == "i017"):
        contrast_id = "yes_vs_no"
    elif term.startswith("fuel_") and term[5:].isdigit():
        contrast_id = f"code_{term[5:]}_vs_5"
    elif term.startswith("fuel_") and term[5:].isdigit() and int(term[5:]) in {1,2,3,4,6,7}:
        contrast_id = f"code_{term[5:]}_vs_5"
    else:
        return None  # Ignore adjustment coefficients; reconcile exposure contrasts only.
    return ((row.get("wave") or "").strip(), (row.get("exposure_variable") or "").strip(),
            (row.get("phenotype_variable") or "").strip(), contrast_id)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--private-dir", type=Path, required=True)
    ap.add_argument("--private-output", type=Path, required=True)
    a = ap.parse_args()
    reg = read_csv(a.registry)
    if reg and set(KEYS + ("prior_pilot_overlap",)) - set(reg[0]):
        raise ValueError("Registry is missing required scope/contrast fields")
    expected = {registered_key(r) for r in reg
                if (r.get("prior_pilot_overlap") or "").strip().lower() == "yes"}
    water_expected = {k for k in expected if k[1] == "i017"}
    by_file, all_observed = {}, set()
    for name in FILES:
        rows = read_csv(a.private_dir / name)
        observed = {key for r in rows if (key := output_key(r)) is not None}
        all_observed.update(observed)
        target = water_expected if name == "pilot_results_private.csv" else expected
        by_file[name] = {
            "result_rows_not_individually_read": len(rows),
            "unique_registered_contrast_keys": len(observed & target),
            "unique_keys_outside_expected_scope": len(observed - target),
            "expected_keys_not_in_file": len(target - observed),
            "exact_scope_match": observed == target,
            "model_id_cardinality": len({r.get("model_id", "") for r in rows}),
        }
    report = {
        "scope": "private historical output key reconciliation at contrast level only",
        "participant_values_read": False, "estimates_or_p_values_read": False,
        "contrast_or_pair_identifiers_emitted": False,
        "registered_overlap_rows": sum((r.get("prior_pilot_overlap") or "").strip().lower() == "yes" for r in reg),
        "registered_unique_contrast_keys": len(expected),
        "pilot_water_unique_keys_expected": len(water_expected),
        "combined_output_unique_contrast_keys": len(all_observed),
        "combined_exact_scope_match": all_observed == expected,
        "files": by_file,
        "interpretation": "scope reconciliation only; does not assess model validity or approve results",
    }
    a.private_output.parent.mkdir(parents=True, exist_ok=True)
    a.private_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "scope_match" if report["combined_exact_scope_match"] and all(x["exact_scope_match"] for x in by_file.values()) else "review_required",
                      "participant_values_read": False, "estimates_or_p_values_read": False,
                      "contrast_or_pair_identifiers_emitted": False}))

if __name__ == "__main__": main()
