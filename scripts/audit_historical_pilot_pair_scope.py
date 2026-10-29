#!/usr/bin/env python3
"""Reconcile private historical pilot pair keys to the public metadata register.
Only pair keys are read; estimates and participant values are never accessed or emitted.
"""
import argparse, csv, json
from pathlib import Path

KEYS = ("wave", "exposure_concept_id", "phenotype_concept_id")
FILES = ("pilot_results_private.csv", "environment_extension_results_private.csv")

def pairs(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if set(KEYS) - set(reader.fieldnames or ()):
            raise ValueError(f"Required pair-key fields missing in {path.name}")
        return {tuple((row.get(k) or "").strip() for k in KEYS) for row in reader}

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--private-dir", type=Path, required=True)
    ap.add_argument("--private-output", type=Path, required=True)
    a = ap.parse_args()
    with a.registry.open(encoding="utf-8-sig", newline="") as f:
        reg = list(csv.DictReader(f))
    if reg and "prior_pilot_overlap" not in reg[0]:
        raise ValueError("Registry missing prior_pilot_overlap")
    expected = {tuple((r.get(k) or "").strip() for k in KEYS) for r in reg
                if (r.get("prior_pilot_overlap") or "").strip().lower() == "yes"}
    combined, by_file = set(), {}
    for name in FILES:
        path = a.private_dir / name
        observed = pairs(path)
        combined.update(observed)
        by_file[name] = {"result_rows": rows(path), "unique_pair_count": len(observed),
                         "registered_overlap_pair_count": len(observed & expected),
                         "outside_registered_overlap_pair_count": len(observed - expected)}
    report = {"scope": "historical private output pair-key reconciliation only",
              "participant_values_read": False, "estimates_or_p_values_read": False,
              "pair_identifiers_emitted": False,
              "register_overlap_row_count": sum((r.get("prior_pilot_overlap") or "").strip().lower() == "yes" for r in reg),
              "registered_unique_pair_count": len(expected), "combined_unique_output_pair_count": len(combined),
              "combined_exact_set_match": combined == expected, "files": by_file,
              "scientific_validity_or_analysis_approval": "not assessed; historical pilot remains exploratory"}
    a.private_output.parent.mkdir(parents=True, exist_ok=True)
    a.private_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "scope_match" if combined == expected else "scope_mismatch_review_required",
                      "participant_values_read": False, "estimates_or_p_values_read": False,
                      "pair_identifiers_emitted": False}))

if __name__ == "__main__": main()
