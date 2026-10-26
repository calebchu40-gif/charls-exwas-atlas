import sys
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_charls_wave_tables import (  # noqa: E402
    split_weights, validate_wave1_source_review,
)
from audit_2011_pilot_intake_metadata import ROLE_DOCUMENTS, ROLE_URLS  # noqa: E402
from project_paths import PRIVATE_ROOT  # noqa: E402
from validate_prepared_wave_tables import get_match_rate_0_to_1  # noqa: E402


class SplitWeightsTests(unittest.TestCase):
    def test_merge_match_rate_is_a_zero_to_one_proportion_and_reads_legacy_name(self):
        self.assertEqual(get_match_rate_0_to_1({"match_rate_0_to_1": 0.789269}), 0.789269)
        self.assertEqual(get_match_rate_0_to_1({"match_pct_of_base_nonmissing": 0.990907}), 0.990907)
        self.assertIsNone(get_match_rate_0_to_1({"match_rate_0_to_1": None}))

    def test_wave2_sample_flags_follow_person_weights(self):
        frame = pd.DataFrame(
            {
                "ID": ["001", "002"],
                "householdID": ["h1", "h2"],
                "INDV_weight": [1.2, 1.3],
                "Blood_weight": [0.8, 0.9],
                "crosssection": [1, 0],
                "longitudinal": [0, 1],
                "HH_weight_ad1": [2.1, 2.2],
            }
        )

        qa = []
        parts = split_weights(frame, "2013", qa)
        person = next(item for item in parts if item[0] == "Weights_person")
        household = next(item for item in parts if item[0] == "Weights_household")

        self.assertEqual(
            list(person[2].columns),
            ["ID", "INDV_weight", "Blood_weight", "crosssection", "longitudinal"],
        )
        self.assertEqual(person[2]["crosssection"].tolist(), [1, 0])
        self.assertEqual(person[2]["longitudinal"].tolist(), [0, 1])
        self.assertEqual(list(household[2].columns), ["householdID", "HH_weight_ad1"])

    def test_conflicting_sample_flags_block_person_weight_table(self):
        frame = pd.DataFrame(
            {
                "ID": ["001", "001", "002"],
                "householdID": ["h1", "h1", "h2"],
                "INDV_weight": [1.2, 1.2, 1.3],
                "crosssection": [1, 0, 1],
                "longitudinal": [0, 1, 0],
                "HH_weight": [2.1, 2.1, 2.2],
            }
        )

        qa = []
        parts = split_weights(frame, "2013", qa)

        self.assertNotIn("Weights_person", [item[0] for item in parts])
        self.assertIn("Weights_household", [item[0] for item in parts])
        person_qa = next(item for item in qa if item["module"] == "Weights_person")
        self.assertIn('"crosssection": 1', person_qa["other_id_mismatch_counts"])

    def test_wave2_without_official_sample_flags_fails_closed(self):
        frame = pd.DataFrame(
            {"ID": ["001"], "INDV_weight": [1.2], "HH_weight": [2.1]}
        )

        with self.assertRaisesRegex(ValueError, "must include crosssection and longitudinal"):
            split_weights(frame, "2013", [])

    def test_identical_duplicate_rows_collapse_without_losing_flag(self):
        frame = pd.DataFrame(
            {
                "ID": ["001", "001", "002"],
                "INDV_weight": [1.2, 1.2, 1.3],
                "crosssection": [1, 1, 0],
                "longitudinal": [0, 0, 1],
            }
        )

        parts = split_weights(frame, "2013", [])
        person = next(item[2] for item in parts if item[0] == "Weights_person")

        self.assertEqual(person["ID"].tolist(), ["001", "002"])
        self.assertEqual(person["crosssection"].tolist(), [1, 0])


class Wave1SourceGateTests(unittest.TestCase):
    def test_wave1_source_table_requires_reviewed_manifest_and_all_four_files(self):
        PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="wave1_gate_test_", dir=PRIVATE_ROOT) as temp:
            manifest_path = Path(temp) / "intake_manifest.json"
            manifest_path.write_text("{}", encoding="utf-8")
            source_inputs = {
                "all_data_archive": {"filename": "all_data.zip", "sha256": "a" * 64},
                "psu": {"filename": "PSU.dta", "sha256": "b" * 64},
                "weight": {"filename": "Weight.dta", "sha256": "c" * 64},
            }
            with self.assertRaisesRegex(ValueError, "missing blood"):
                validate_wave1_source_review(source_inputs, manifest_path)

    def test_wave1_source_gate_rejects_unreviewed_or_hash_mismatched_files(self):
        PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="wave1_gate_test_", dir=PRIVATE_ROOT) as temp:
            manifest_path = Path(temp) / "intake_manifest.json"
            roles = list(ROLE_URLS)
            source_inputs = {}
            required_files = []
            for i, role in enumerate(roles):
                filename = "all_data.zip" if role == "wave1_all_data" else f"{role}.dta"
                digest = str(i + 1) * 64
                source_inputs["all_data_archive" if role == "wave1_all_data" else role] = {
                    "filename": filename, "sha256": digest,
                }
                required_files.append({
                    "role": role,
                    "official_document": ROLE_DOCUMENTS[role],
                    "source_page": ROLE_URLS[role],
                    "original_filename": filename,
                    "official_title": f"Synthetic {role}",
                    "downloaded_at": "2026-10-27",
                    "identity_review_status": "verified_official_source",
                    "reviewed_local_sha256": digest,
                })
            manifest_path.write_text(json.dumps({
                "source_manifest_id": "charls2011-synthetic-test",
                "source_identity_review": {
                    "status": "unresolved", "reviewed_at": None, "reviewer_note": None,
                },
                "required_files": required_files,
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source review gate not passed"):
                validate_wave1_source_review(source_inputs, manifest_path)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["source_identity_review"] = {
                "status": "verified_official_source",
                "reviewed_at": "2026-10-27",
                "reviewer_note": "Synthetic test fixture only.",
            }
            manifest["required_files"][0]["reviewed_local_sha256"] = "f" * 64
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 does not match"):
                validate_wave1_source_review(source_inputs, manifest_path)


if __name__ == "__main__":
    unittest.main()
