#!/usr/bin/env python3
"""Derive the Wave 1 pilot-105 hypothesis manifest from the frozen K=150 register.

The pilot batch is **not** a new inferential family. It is exactly the 105
coefficients nested inside the frozen K=150 household-environment register:
one running-water contrast plus six cooking-fuel-versus-electricity contrasts,
each crossed with the fifteen predeclared blood phenotypes.

This script therefore *filters* the frozen register and labels each row with its
review status; it never invents a hypothesis, never changes a family, and never
touches participant data.

Status rules (from the 2026-10-30 pilot execution design):

* the fasting field ``qc1_va003`` has no authoritative Wave 1 numeric mapping,
  so both the seven glucose and the seven triglyceride coefficients stay
  ``blocked_by_unresolved_measurement_rule`` — no estimate, no p/q value;
* every other coefficient is ``open_pending_independent_review``: a candidate
  only, not a claim of estimability.

Run::

    python scripts/build_wave1_pilot105_manifest.py

and it rewrites ``audit/wave1_pilot105_hypothesis_manifest_draft_2026-10-31.csv``.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "audit" / "wave1_household_environment_hypothesis_register_v0.csv"
OUTPUT = ROOT / "audit" / "wave1_pilot105_hypothesis_manifest_draft_2026-10-31.csv"

PARENT_FAMILY = "wave1_household_environment_K150"
PILOT_EXPOSURES = ("running_water_at_residence", "cooking_fuel_main")
BLOCKED_OUTCOMES = ("blood_glucose", "blood_triglycerides")
BLOCKED_STATUS = "blocked_by_unresolved_measurement_rule"
OPEN_STATUS = "open_pending_independent_review"
BLOCKED_REASON = ("Wave 1 fasting field qc1_va003 has no authoritative numeric mapping; "
                  "no coefficient, p or q value is produced until reviewed codes exist")
EXPECTED_ROWS = 105
EXPECTED_CONTRASTS = 7
EXPECTED_PHENOTYPES = 15

FIELDS = (
    "hypothesis_id", "parent_family_id", "parent_family_size", "family_role", "wave",
    "exposure_concept_id", "contrast_id", "exposure_field_candidate",
    "exposure_label_candidate", "reference_label_candidate",
    "phenotype_concept_id", "phenotype_field_candidate", "phenotype_unit_candidate",
    "primary_model_id", "analysis_status", "status_reason", "notes",
)


class ManifestError(ValueError):
    """The frozen register cannot produce the expected pilot-105 batch."""


def build(register: Path = REGISTER) -> list[dict[str, str]]:
    with register.open(newline="", encoding="utf-8-sig") as handle:
        rows = [row for row in csv.DictReader(handle)
                if row["family_id"] == PARENT_FAMILY
                and row["exposure_concept_id"] in PILOT_EXPOSURES]
    if len(rows) != EXPECTED_ROWS:
        raise ManifestError(f"expected {EXPECTED_ROWS} pilot rows, found {len(rows)}")

    contrasts = {row["contrast_id"] for row in rows}
    phenotypes = {row["phenotype_concept_id"] for row in rows}
    if len(contrasts) != EXPECTED_CONTRASTS:
        raise ManifestError(f"expected {EXPECTED_CONTRASTS} contrasts, found {len(contrasts)}")
    if len(phenotypes) != EXPECTED_PHENOTYPES:
        raise ManifestError(f"expected {EXPECTED_PHENOTYPES} phenotypes, found {len(phenotypes)}")
    pairs = {(row["contrast_id"], row["phenotype_concept_id"]) for row in rows}
    if len(pairs) != EXPECTED_ROWS:
        raise ManifestError("the register does not contain a complete contrast x phenotype grid")

    manifest: list[dict[str, str]] = []
    for row in rows:
        blocked = row["phenotype_concept_id"] in BLOCKED_OUTCOMES
        manifest.append({
            "hypothesis_id": row["hypothesis_id"],
            "parent_family_id": row["family_id"],
            "parent_family_size": row["family_size"],
            "family_role": row["family_role"],
            "wave": row["wave"],
            "exposure_concept_id": row["exposure_concept_id"],
            "contrast_id": row["contrast_id"],
            "exposure_field_candidate": row["exposure_field_candidate"],
            "exposure_label_candidate": row["exposure_label_candidate"],
            "reference_label_candidate": row["reference_label_candidate"],
            "phenotype_concept_id": row["phenotype_concept_id"],
            "phenotype_field_candidate": row["phenotype_field_candidate"],
            "phenotype_unit_candidate": row["phenotype_unit_candidate"],
            "primary_model_id": row["primary_model_id"],
            "analysis_status": BLOCKED_STATUS if blocked else OPEN_STATUS,
            "status_reason": BLOCKED_REASON if blocked else "candidate only; requires independent review",
            "notes": ("nested in the frozen K=150 family; no tranche-level multiplicity adjustment"
                      if not blocked else
                      "nested in the frozen K=150 family; blocked before any model fit"),
        })
    return manifest


def write(rows: list[dict[str, str]], path: Path = OUTPUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def summarise(rows: list[dict[str, str]]) -> dict[str, object]:
    by_status: dict[str, int] = {}
    for row in rows:
        by_status[row["analysis_status"]] = by_status.get(row["analysis_status"], 0) + 1
    return {
        "rows": len(rows),
        "contrasts": len({row["contrast_id"] for row in rows}),
        "phenotypes": len({row["phenotype_concept_id"] for row in rows}),
        "by_status": by_status,
        "parent_family": PARENT_FAMILY,
        "output": str(OUTPUT.relative_to(ROOT)),
    }


def main() -> int:
    rows = build()
    write(rows)
    print(json.dumps(summarise(rows), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
