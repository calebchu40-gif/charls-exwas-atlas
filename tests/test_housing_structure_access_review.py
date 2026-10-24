import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = "housing_structure_access_review_2026-10-25.md"


class HousingStructureAccessReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/food_environment_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / "audit/ep_concept_source_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.index = list(csv.DictReader(f))
        cls.site = json.loads((ROOT / "site-prototype/dist/food_environment_v1.json").read_text(encoding="utf-8"))

    def test_all_22_source_reviewed_rows_have_wave_specific_labels(self):
        selected = [r for r in self.rows if REVIEW in r["mapping_status"]]
        self.assertEqual(len(selected), 23)
        for row in selected:
            self.assertTrue(row["code_value_labels"])
            self.assertIn("official", row["mapping_status"].lower())
            self.assertIn("Cross-wave equivalence is not established", row["caveat"])
        for row in selected:
            key = (row["wave"], row["code"].lower(), row["concept_id"])
            idx = next(r for r in self.index if r["Source.File"].endswith("food_environment_crosswalk_v1.csv") and r["Wave"] == key[0] and r["Source.Code"].lower() == key[1] and key[2] in r["Source.Concept.ID"].split(" | "))
            self.assertEqual(idx["Mapping.Status"], row["mapping_status"])

    def test_entrance_steps_keep_structural_route_and_elevator_caveat(self):
        rows = [r for r in self.rows if r["concept_id"] == "entrance_steps" and r["wave"] in {"2011", "2013", "2015", "2018"}]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertIn("structural skips as ineligible", row["caveat"])
            self.assertIn("elevator is available", row["caveat"])

    def test_story_fields_remain_separate_and_nominal_structure_is_not_pooled(self):
        structures = [r for r in self.rows if r["concept_id"] == "building_structure"]
        self.assertEqual(len(structures), 5)
        self.assertTrue(all("nominal" in r["caveat"] for r in structures))
        stories = [r for r in self.rows if r["concept_id"] == "building_stories" and REVIEW in r["mapping_status"]]
        self.assertTrue(stories)
        self.assertTrue(all("do not combine them into a numeric floor" in r["caveat"] for r in stories))

    def test_2011_interval_categories_are_under_parent_question_i005(self):
        row = next(r for r in self.rows if r["concept_id"] == "housing_construction_year" and r["wave"] == "2011" and r["code"].lower() == "i005_1")
        self.assertIn(REVIEW, row["mapping_status"])
        self.assertIn("fallback interval", row["caveat"].lower())
        script = (ROOT / "scripts/apply_housing_structure_access_review.py").read_text(encoding="utf-8")
        self.assertIn("fallback intervals are printed under", script)
        questionnaire = (ROOT / "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt").read_text(encoding="utf-8", errors="ignore")
        self.assertIn("If R is unclear about year, choose", questionnaire)


if __name__ == "__main__":
    unittest.main()
