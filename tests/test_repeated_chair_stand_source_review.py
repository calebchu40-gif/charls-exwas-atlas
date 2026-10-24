import importlib.util
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/apply_repeated_chair_stand_source_review.py"
spec = importlib.util.spec_from_file_location("repeated_chair_stand_source_review", MODULE_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class RepeatedChairStandSourceReviewTests(unittest.TestCase):
    def test_official_questionnaire_and_guide_anchors_exist(self):
        self.assertEqual(set(review.verify_sources()), {"2011", "2013", "2015"})

    def test_route_specific_durations_and_preamble_conflict_are_preserved(self):
        semantics, caveat, _ = review.source_note("2015")
        self.assertIn("fastest pace", semantics)
        self.assertIn("usual pace", semantics)
        self.assertIn("different completion routes", caveat)
        self.assertIn("993", caveat)
        self.assertIn("999", caveat)
        self.assertIn("chair height", caveat)

    def test_2011_field_identity_is_not_asserted(self):
        self.assertIn("LI003–LI008", review.source_note("2011")[1])
        self.assertIn("unverified", review.source_note("2011")[1])

    def test_all_three_rows_and_public_json_are_reviewed(self):
        with (ROOT / "audit/objective_measurement_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        target = [r for r in rows if r["concept_id"] == "repeated_chair_stand"]
        self.assertEqual(len(target), 3)
        self.assertTrue(all("candidate phenotype only" in r["source_status"] for r in target))
        public_rows = json.loads((ROOT / "site-prototype/dist/objective_measurements_v1.json").read_text(encoding="utf-8"))
        public_target = [r for r in public_rows if r["concept_id"] == "repeated_chair_stand"]
        self.assertEqual(len(public_target), 3)
        self.assertTrue(all("fastest pace" in r["value_semantics"] for r in public_target))


if __name__ == "__main__":
    unittest.main()
