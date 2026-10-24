import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ElectricityBathingReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/food_environment_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / "audit/ep_concept_source_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.index = list(csv.DictReader(f))
        cls.site = json.loads((ROOT / "site-prototype/dist/food_environment_v1.json").read_text(encoding="utf-8"))

    def test_all_mapped_electricity_and_bath_fields_have_wave_specific_labels(self):
        electricity = [r for r in self.rows if r["concept_id"] == "electricity_access"]
        bathing = [r for r in self.rows if r["concept_id"] == "bathing_facility"]
        self.assertEqual({r["wave"] for r in electricity}, {"2011", "2013", "2018", "2020"})
        self.assertEqual({r["wave"] for r in bathing}, {"2011", "2013", "2015", "2018", "2020"})
        self.assertEqual({r["code_value_labels"] for r in electricity}, {"1=Yes; 2=No"})
        self.assertIn("1=Unified hot water supply; 2=Water heater; 3=No", {r["code_value_labels"] for r in bathing})
        for row in electricity + bathing:
            self.assertIn("official", row["mapping_status"].lower())
            self.assertIn("person-household linkage", row["mapping_status"])

    def test_bathing_categories_are_nominal_and_not_a_personal_exposure_measure(self):
        for row in (r for r in self.rows if r["concept_id"] == "bathing_facility"):
            self.assertIn("nominal", row["caveat"].lower())
            self.assertIn("do not infer bathing frequency", row["caveat"].lower())
            self.assertIn("cross-wave equivalence is unapproved", row["caveat"].lower())

    def test_index_and_public_json_match_reviewed_status(self):
        concepts = {"electricity_access", "bathing_facility"}
        source = {(r["wave"], r["code"].lower(), r["concept_id"]): r for r in self.rows if r["concept_id"] in concepts}
        for key, row in source.items():
            idx = next(r for r in self.index if r["Source.File"].endswith("food_environment_crosswalk_v1.csv") and r["Wave"] == key[0] and r["Source.Code"].lower() == key[1] and key[2] in r["Source.Concept.ID"].split(" | "))
            self.assertEqual(idx["Mapping.Status"], row["mapping_status"])
        for concept in self.site:
            if concept.get("concept_id") in concepts:
                for field in concept["source_fields"]:
                    key = (field["wave"], field["code"].lower(), concept["concept_id"])
                    if key in source:
                        self.assertEqual(field["mapping_status"], source[key]["mapping_status"])


if __name__ == "__main__":
    unittest.main()
