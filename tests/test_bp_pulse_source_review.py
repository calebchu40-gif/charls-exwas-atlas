import importlib.util
import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/apply_bp_pulse_source_review.py"
spec = importlib.util.spec_from_file_location("bp_pulse_source_review", MODULE_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class BloodPressurePulseSourceReviewTests(unittest.TestCase):
    def test_official_questionnaire_anchors_exist_for_all_waves(self):
        self.assertEqual(set(review.verify_sources()), {"2011", "2013", "2015"})

    def test_bp_units_are_explicit_and_pulse_unit_stays_unresolved(self):
        for wave in review.WAVES:
            self.assertEqual(review.source_note(wave, "systolic_bp")[1], "mmHg")
            self.assertEqual(review.source_note(wave, "diastolic_bp")[1], "mmHg")
            semantics, unit, note, _ = review.source_note(wave, "pulse_rate")
            self.assertEqual(unit, "")
            self.assertIn("unit only as ‘P’", semantics)
            self.assertIn("unit remains blank", note)

    def test_2011_identity_is_held_while_2013_2015_are_questionnaire_verified(self):
        self.assertIn("LI-to-QA one-to-one field identity remains unverified", review.source_note("2011", "systolic_bp")[2])
        self.assertIn("exact QA* fields", review.source_note("2013", "systolic_bp")[2])
        self.assertIn("exact QA* fields", review.source_note("2015", "systolic_bp")[2])

    def test_applied_crosswalk_contains_9_concept_wave_rows_and_preserves_units(self):
        with (ROOT / "audit/objective_measurement_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        target = [r for r in rows if r.get("concept_id") in review.CONCEPTS]
        self.assertEqual(len(target), 9)
        pulse = [r for r in target if r["concept_id"] == "pulse_rate"]
        self.assertEqual(len(pulse), 3)
        self.assertTrue(all(r["unit"] == "" for r in pulse))
        self.assertTrue(all(r["unit"] == "mmHg" for r in target if r["concept_id"] in {"systolic_bp", "diastolic_bp"}))
        self.assertTrue(all("993" in r["source_caveat"] and "999" in r["source_caveat"] for r in target))

    def test_public_phenotype_shard_receives_units_and_source_review(self):
        import json
        rows = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        codes = {code for values in review.CONCEPTS.values() for code in values["codes"]}
        target = [r for r in rows if r.get("Variable.Name", "").lower() in codes
                  and r.get("Source.Wave") in review.WAVES
                  and r.get("Concept.Mapping.Source") == "audit/objective_measurement_crosswalk_v1.csv"]
        self.assertEqual(len(target), 54)  # two release-module spellings retain the same audited mapping
        for row in target:
            code = row["Variable.Name"].lower()
            if code in review.CONCEPTS["pulse_rate"]["codes"]:
                self.assertEqual(row.get("Concept.Unit.Candidates", ""), "")
            else:
                expected_unit = f"{row['Concept.ID.Candidates']}=mmHg"
                self.assertIn(expected_unit, row.get("Concept.Unit.Candidates", ""))
            self.assertIn("candidate phenotype only", row["Concept.Mapping.Status"])
            self.assertIn("993", row["Concept.Mapping.Caveat"])
            self.assertIn("999", row["Concept.Mapping.Caveat"])


if __name__ == "__main__":
    unittest.main()
