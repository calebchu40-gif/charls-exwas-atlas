"""Tests for the engine -> schema-v3 mapper.

The mapper must fail closed: it may only emit a ``success`` row when the
frozen provenance states a verified source, weight and PSU, a documented
stratum status, a reviewed estimability decision, and a code commit.
"""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import engine_to_schema_v3 as mapper  # noqa: E402
import exwas_engine as engine  # noqa: E402
import run_exwas_scan as cli  # noqa: E402
import validate_exwas_result_table as contract  # noqa: E402

PROVENANCE = {
    "data_release": "SYNTHETIC test release",
    "source_identity_status": "verified_official_source",
    "source_hash_status": "private_local_sha256_recorded",
    "source_manifest_id": "synthetic-manifest-001",
    "target_population": "synthetic frame",
    "eligibility_rule": "weight > 0 and complete cases",
    "weight_id": "ind_weight",
    "weight_status": "verified_used",
    "weight_source": "synthetic fixture",
    "psu_id": "psu",
    "psu_status": "verified_used",
    "stratum_id": "stratum",
    "stratum_status": "verified_used",
    "variance_design": "Taylor linearisation with synthetic strata",
    "exposure_transform": "none",
    "phenotype_transform": "none",
    "missingness_rule": "complete case",
    "comparability_grade": "synthetic",
    "estimability_review_status": "reviewed_pass",
    "estimability_review_id": "synthetic-review-001",
    "software_versions": "python 3.12; svy 0.35.0; commit: 0e39927",
}


def _engine_rows(**scan_kwargs):
    frame = cli.synthetic_frame(n=600, seed=5)
    registry = cli.synthetic_registry()
    design = cli.synthetic_design()
    for key, value in scan_kwargs.items():
        setattr(design, key, value)
    rows = engine.scan(frame, registry, design, wave="SYNTH", models=["M0"])
    return [{k: ("" if v is None else str(v)) for k, v in row.items()} for row in rows]


def _write_provenance(tmp: Path, payload: dict) -> Path:
    path = tmp / "provenance.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class ProvenanceTests(unittest.TestCase):
    def test_missing_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = dict(PROVENANCE)
            payload.pop("source_manifest_id")
            path = _write_provenance(Path(tmp), payload)
            with self.assertRaises(mapper.MappingError):
                mapper.load_provenance(path)

    def test_bad_enum_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = dict(PROVENANCE, source_identity_status="looks_fine")
            path = _write_provenance(Path(tmp), payload)
            with self.assertRaises(mapper.MappingError):
                mapper.load_provenance(path)

    def test_missing_code_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = dict(PROVENANCE, software_versions="python 3.12; svy 0.35.0")
            path = _write_provenance(Path(tmp), payload)
            with self.assertRaises(mapper.MappingError):
                mapper.load_provenance(path)

    def test_reviewed_pass_requires_review_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = dict(PROVENANCE, estimability_review_id="")
            path = _write_provenance(Path(tmp), payload)
            with self.assertRaises(mapper.MappingError):
                mapper.load_provenance(path)


class MappingTests(unittest.TestCase):
    def test_engine_rows_round_trip_through_the_contract(self):
        engine_rows = _engine_rows()
        rows = mapper.build(engine_rows, PROVENANCE)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "results_v3.csv"
            mapper.write_rows(rows, out)
            errors = contract.validate_csv(out)
            self.assertEqual(errors, [], msg="\n".join(errors[:10]))
            with out.open(newline="", encoding="utf-8") as handle:
                written = list(csv.DictReader(handle))
        self.assertEqual(len(written), len(engine_rows))
        self.assertTrue(all(row["fit_status"] == "success" for row in written))
        self.assertTrue(all(row["psu_id"] == "psu" for row in written))
        self.assertTrue(all("commit: 0e39927" in row["software_versions"] for row in written))

    def test_blocked_scan_produces_no_estimates(self):
        engine_rows = _engine_rows(age_min=999)
        rows = mapper.build(engine_rows, PROVENANCE)
        self.assertTrue(rows)
        for row in rows:
            self.assertNotEqual(row["fit_status"], "success")
            for field in ("estimate", "standard_error", "ci_lower", "ci_upper",
                          "p_value", "q_value_by", "p_bonferroni", "n_model"):
                self.assertEqual(row[field], "")
            self.assertEqual(row["estimability_review_id"], "")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "blocked.csv"
            mapper.write_rows(rows, out)
            self.assertEqual(contract.validate_csv(out), [])

    def test_unknown_engine_status_is_rejected(self):
        engine_rows = _engine_rows()
        engine_rows[0]["fit_status"] = "mystery"
        with self.assertRaises(mapper.MappingError):
            mapper.build(engine_rows, PROVENANCE)

    def test_duplicate_analysis_ids_are_rejected(self):
        engine_rows = _engine_rows()
        engine_rows[1]["analysis_id"] = engine_rows[0]["analysis_id"]
        with self.assertRaises(mapper.MappingError):
            mapper.build(engine_rows, PROVENANCE)

    def test_success_without_estimate_is_rejected(self):
        engine_rows = _engine_rows()
        for row in engine_rows:
            if row["fit_status"] == "success":
                row["estimate"] = ""
                break
        with self.assertRaises(mapper.MappingError):
            mapper.build(engine_rows, PROVENANCE)

    def test_status_map_covers_every_engine_status(self):
        produced = {"success", "no_eligible_records", "numerically_unavailable",
                    "zero_outcome_variance", "zero_exposure_variance",
                    "nonpositive_weight_total", "invalid_binary_outcome", "engine_omitted_term"}
        self.assertTrue(produced.issubset(set(mapper.FIT_STATUS_MAP)))
        self.assertTrue(set(mapper.FIT_STATUS_MAP.values()).issubset(contract.FIT_STATUSES))


if __name__ == "__main__":
    unittest.main()
