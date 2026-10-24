import importlib.util
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/apply_objective_measurement_source_review.py"
spec = importlib.util.spec_from_file_location("objective_measurement_source_review", MODULE_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ObjectiveMeasurementSourceReviewTests(unittest.TestCase):
    def test_official_questionnaire_and_guide_anchors_exist(self):
        self.assertEqual(set(review.verify_sources()), {"2011", "2013", "2015"})

    def test_units_are_only_recorded_when_explicit(self):
        for wave in review.WAVES:
            self.assertEqual(review.source_note(wave, "systolic_bp")[1], "mmHg")
            self.assertEqual(review.source_note(wave, "diastolic_bp")[1], "mmHg")
            self.assertEqual(review.source_note(wave, "grip_strength")[1], "kg")
            self.assertEqual(review.source_note(wave, "pulse_rate")[1], "")
            self.assertEqual(review.source_note(wave, "peak_flow")[1], "")

    def test_wave_identity_and_status_codes_remain_caveated(self):
        self.assertIn("LI-to-QA one-to-one field identity remains unverified", review.source_note("2011", "systolic_bp")[2])
        for concept in ("grip_strength", "peak_flow"):
            self.assertIn("unresolved", review.source_note("2011", concept)[2])
        self.assertIn("age-related protocol marker", review.source_note("2015", "peak_flow")[0])
        self.assertIn("993", review.source_note("2013", "grip_strength")[0])
        self.assertIn("890", review.source_note("2013", "peak_flow")[0])

    def test_applied_crosswalk_has_fifteen_concept_wave_rows(self):
        with (ROOT / "audit/objective_measurement_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        target = [r for r in rows if r.get("concept_id") in review.CONCEPTS]
        self.assertEqual(len(target), 15)
        self.assertTrue(all(r["unit"] == "mmHg" for r in target if r["concept_id"] in {"systolic_bp", "diastolic_bp"}))
        self.assertTrue(all(r["unit"] == "kg" for r in target if r["concept_id"] == "grip_strength"))
        self.assertTrue(all(r["unit"] == "" for r in target if r["concept_id"] in {"pulse_rate", "peak_flow"}))
        self.assertTrue(all("candidate phenotype only" in r["source_status"] for r in target))

    def test_public_shard_has_audited_mapping_and_keeps_special_codes(self):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        codes = {code for values in review.CONCEPTS.values() for code in values["codes"]}
        target = [r for r in rows if r.get("Variable.Name", "").lower() in codes
                  and r.get("Source.Wave") in review.WAVES
                  and r.get("Concept.Mapping.Source") == "audit/objective_measurement_crosswalk_v1.csv"]
        self.assertEqual(len(target), 75)
        for row in target:
            self.assertIn("candidate phenotype only", row["Concept.Mapping.Status"])
            if row["Variable.Name"].lower() in review.CONCEPTS["grip_strength"]["codes"]:
                self.assertIn("=kg", row.get("Concept.Unit.Candidates", ""))
            elif row["Variable.Name"].lower() in review.CONCEPTS["peak_flow"]["codes"]:
                self.assertEqual(row.get("Concept.Unit.Candidates", ""), "")
                self.assertIn("890", row["Concept.Mapping.Caveat"])


if __name__ == "__main__":
    unittest.main()
