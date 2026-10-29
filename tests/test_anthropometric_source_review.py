import importlib.util
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/apply_anthropometric_source_review.py"
spec = importlib.util.spec_from_file_location("anthropometric_source_review", MODULE_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class AnthropometricSourceReviewTests(unittest.TestCase):
    def test_official_questionnaire_anchors_exist_for_all_waves(self):
        self.assertEqual(set(review.verify_sources()), {"2011", "2013", "2013_release_note", "2015"})

    def test_explicit_units_and_context_fields_are_preserved(self):
        for wave in review.WAVES:
            self.assertEqual(review.source_note(wave, "standing_height")[3], "cm")
            self.assertEqual(review.source_note(wave, "arm_length")[3], "cm")
            self.assertEqual(review.source_note(wave, "knee_height")[3], "cm")
            self.assertEqual(review.source_note(wave, "body_weight")[3], "kg")
            self.assertEqual(review.source_note(wave, "waist_circumference")[3], "cm")
        self.assertIn("150 kg threshold", review.source_note("2015", "body_weight")[0])
        self.assertIn("QJ003", review.source_note("2013", "arm_length")[0])
        self.assertIn("QK003", review.source_note("2013", "knee_height")[0])

    def test_2011_release_field_identity_is_caveated(self):
        for concept in review.CONCEPTS:
            self.assertIn("one-to-one release-field identity remains unresolved", review.source_note("2011", concept)[1].lower())

    def test_all_fifteen_wave_rows_and_public_json_are_updated(self):
        with (ROOT / "audit/objective_measurement_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        target = [r for r in rows if r["concept_id"] in review.CONCEPTS]
        self.assertEqual(len(target), 15)
        self.assertTrue(all(
            "candidate phenotype only" in r["source_status"]
            or "analysis approval remain unverified" in r["source_status"]
            for r in target
        ))
        public_rows = json.loads((ROOT / "site-prototype/dist/objective_measurements_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(len([r for r in public_rows if r["concept_id"] in review.CONCEPTS]), 15)


if __name__ == "__main__":
    unittest.main()
