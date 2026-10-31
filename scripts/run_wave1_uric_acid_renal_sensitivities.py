#!/usr/bin/env python3
"""Fit private Wave 1 uric-acid renal-adjustment sensitivity models.

The primary K150/K90 results remain unchanged. This companion run refits only
the 16 registered exposure-to-uric-acid pairs with creatinine and/or the
official self-reported kidney-disease indicator added to the primary model.
It does not authorize public release or replace the primary-family correction.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_paths import PRIVATE_ROOT, require_private_path
import run_2011_household_environment_scaleup as runner
from require_verified_wave1_frame import (
    analysis_plan_fingerprint,
    require_user_authorized_internal_analysis,
    require_verified_wave1_frame,
)


PRIVATE = runner.PRIVATE
PLAN_KEY = runner.PLAN_KEY
CONFIG_PATH = PRIVATE / "analysis_review" / "wave1_household_environment_scaleup_model_config.json"
AUTH_PATH = PRIVATE / "analysis_review" / f"{runner.ANALYSIS_PLANS[PLAN_KEY]['plan_id']}_user_internal_authorization.json"
KIDNEY_FIELD = "da007_9_"
CREATININE_FIELD = "newcrea"
VARIANTS = {
    "creatinine": {"creatinine": True, "kidney_disease": False},
    "kidney_disease": {"creatinine": False, "kidney_disease": True},
    "creatinine_and_kidney_disease": {"creatinine": True, "kidney_disease": True},
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if PRIVATE.resolve() != PRIVATE_ROOT.resolve():
        raise RuntimeError("CHARLS private root does not match the configured protected root")
    original_config_bytes = CONFIG_PATH.read_bytes()
    original_auth_bytes = AUTH_PATH.read_bytes()
    base_config = json.loads(original_config_bytes)
    base_auth = json.loads(original_auth_bytes)
    analytes = runner.read_analytes()
    uric_acid = next(row for row in analytes if row["concept_id"] == "blood_uric_acid")
    registry = runner._load_registry()
    ua_registry = [row for row in registry if row["phenotype_concept_id"] == "blood_uric_acid"]
    if len(ua_registry) != 16 or len({row["hypothesis_id"] for row in ua_registry}) != 16:
        raise RuntimeError("Expected the 16 registered Wave 1 uric-acid hypotheses")

    provenance = require_verified_wave1_frame(PRIVATE, runner.DATA, age_path=runner.AGE)
    output_root = require_private_path(PRIVATE / "results" / "wave1_uric_acid_renal_sensitivities_20261031")
    output_root.mkdir(parents=True, exist_ok=False)
    output_root.chmod(0o700)
    manifest_variants: list[dict[str, Any]] = []

    import numpy as np
    import polars as pl
    import pyreadstat
    import svy

    if svy.__version__ != runner.EXPECTED_SVY:
        raise RuntimeError(f"Expected svy {runner.EXPECTED_SVY}, found {svy.__version__}")

    try:
        for name, flags in VARIANTS.items():
            config = json.loads(json.dumps(base_config))
            config["analysis_plan_sha256"] = analysis_plan_fingerprint(PLAN_KEY)
            config["model"]["primary_model_id"] = f"M1_UA_renal_{name}"
            if flags["creatinine"]:
                config["model"]["continuous_covariates"].append({
                    "field": CREATININE_FIELD,
                    "transform": "identity",
                    "center": None,
                })
            if flags["kidney_disease"]:
                config["model"]["binary_covariates"].append({
                    "field": KIDNEY_FIELD,
                    "positive_value": 1,
                    "reference_value": 2,
                })

            config_path = PRIVATE / "analysis_review" / f"wave1_uric_acid_renal_{name}_config_private.json"
            config_bytes = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            config_path.write_bytes(config_bytes)
            config_path.chmod(0o600)

            auth = dict(base_auth)
            auth.update({
                "analysis_plan_sha256": config["analysis_plan_sha256"],
                "model_configuration_sha256": sha256(config_bytes),
                "sensitivity_variant": name,
                "scope": "User-authorized internal sensitivity run of the 16 pre-registered Wave 1 exposure-to-uric-acid pairs; private output only.",
            })
            AUTH_PATH.write_text(json.dumps(auth, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            AUTH_PATH.chmod(0o600)
            auth_archive = PRIVATE / "analysis_review" / f"wave1_uric_acid_renal_{name}_authorization_private.json"
            auth_archive.write_text(json.dumps(auth, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            auth_archive.chmod(0o600)

            readiness = require_user_authorized_internal_analysis(
                PRIVATE, provenance, PLAN_KEY, config_path
            )
            runner._validate_configuration(
                config, analytes, ua_registry, user_authorized_internal=True
            )
            data, term_map = runner._read_protected_frame(
                config, analytes, ua_registry, pyreadstat, pl
            )
            outcome_scale = runner._reference_outcome_scale(data, config, uric_acid, pl, np)
            results: list[dict[str, Any]] = []
            for family_id in ("wave1_household_environment_K150", "wave1_heating_route_K90"):
                family = [row for row in ua_registry if row["family_id"] == family_id]
                groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
                for row in family:
                    groups[(row["exposure_concept_id"], row["exposure_field_candidate"])].append(row)
                for (concept, field_candidate), exposure_rows in groups.items():
                    contrast_rows = list({row["contrast_id"]: row for row in exposure_rows}.values())
                    terms = [runner._term_for(row) for row in contrast_rows]
                    estimates, _qa = runner._fit_exposure_group(
                        data, config, uric_acid, contrast_rows, family_id, terms,
                        term_map, outcome_scale, pl, np, svy,
                    )
                    for row in exposure_rows:
                        estimate = estimates.get(row["contrast_id"])
                        if estimate is None:
                            raise RuntimeError(f"Missing fitted contrast {row['hypothesis_id']}")
                        results.append({
                            "hypothesis_id": row["hypothesis_id"],
                            "family_id": family_id,
                            "exposure_concept_id": concept,
                            "contrast_id": row["contrast_id"],
                            "phenotype_concept_id": "blood_uric_acid",
                            "model_id": config["model"]["primary_model_id"],
                            **estimate,
                            "release_status": "not_approved",
                        })
            if len(results) != 16 or any(row["fit_status"] != "success" for row in results):
                raise RuntimeError(f"{name}: expected 16 successful fits, found {len(results)}")

            from adjust_exwas_pvalues import adjust_pvalues
            adjusted = adjust_pvalues([float(row["p_value"]) for row in results])
            for row, q, bonf in zip(results, adjusted["q_value_by"], adjusted["p_bonferroni"], strict=True):
                row["q_value_by_ua_sensitivity16"] = q
                row["p_bonferroni_ua_sensitivity16"] = bonf
                row["multiplicity_scope"] = "diagnostic within targeted UA sensitivity set only; primary inference remains the full registered K150/K90 family"

            result_path = output_root / f"wave1_ua_renal_{name}_results_private.csv"
            with result_path.open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.DictWriter(stream, fieldnames=sorted({key for row in results for key in row}))
                writer.writeheader()
                writer.writerows(results)
            result_path.chmod(0o600)
            manifest_variants.append({
                "variant": name,
                "added_covariates": [field for field, included in ((CREATININE_FIELD, flags["creatinine"]), (KIDNEY_FIELD, flags["kidney_disease"])) if included],
                "model_configuration_sha256": readiness["model_configuration_sha256"],
                "result_sha256": sha256(result_path.read_bytes()),
                "rows": len(results),
                "fit_status": "16_success",
                "result_file": result_path.name,
            })
    finally:
        CONFIG_PATH.write_bytes(original_config_bytes)
        CONFIG_PATH.chmod(0o600)
        AUTH_PATH.write_bytes(original_auth_bytes)
        AUTH_PATH.chmod(0o600)

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "analysis": "Wave 1 registered exposure-to-uric-acid renal-adjustment sensitivities",
        "source_manifest_id": provenance["source_manifest_id"],
        "prepared_frame_sha256": provenance["prepared_output_sha256"],
        "age_candidate_sha256": provenance["age_candidate_sha256"],
        "analysis_plan_sha256": analysis_plan_fingerprint(PLAN_KEY),
        "code_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=runner.ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "variants": manifest_variants,
        "data_release": False,
        "public_release_status": "not_approved",
        "independent_methods_review": "not_claimed",
    }
    manifest_path = output_root / "wave1_ua_renal_sensitivity_manifest_private.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path.chmod(0o600)
    print(json.dumps({"run": "complete", "variants": len(manifest_variants), "result_rows": sum(v["rows"] for v in manifest_variants), "outputs_private": True}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
