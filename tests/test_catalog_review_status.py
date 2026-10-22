import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CatalogReviewStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
        cls.work = json.loads((ROOT / "site-prototype/dist/work_exposures_v1.json").read_text(encoding="utf-8"))

    def test_2011_fb010_codebook_values_and_conflict_reach_main_catalog(self):
        rows = [
            row for row in self.catalog
            if row.get("Variable.Name", "").lower() == "fb010" and "2011" in row.get("waves", "").split(",")
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertIn("4=School", row.get("value_labels", ""))
        self.assertIn("6=Other", row.get("value_labels", ""))
        self.assertIn("DO NOT ANALYZE", row.get("value_label_review", ""))
        self.assertIn("questionnaire:", row.get("value_label_review", ""))
        self.assertIn("released-data coding unresolved", row.get("value_label_review", ""))

    def test_2011_fb010_specialty_catalog_links_correct_baseline_source(self):
        fields = [
            field
            for concept in self.work
            for field in concept.get("source_fields", [])
            if field.get("code", "").lower() == "fb010" and field.get("wave") == "2011"
        ]
        self.assertEqual(len(fields), 1)
        self.assertIn("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", fields[0].get("value_label_source", ""))
        self.assertIn("DO NOT ANALYZE", fields[0].get("value_label_status", ""))

    def test_2011_fl020_option_labels_are_questionnaire_meanings_not_codes(self):
        meanings = [
            "Business closed", "Quit", "I was laid off", "I was fired",
            "I went to school", "I went abroad", "Stopped working for health reasons",
            "Stopped working for family reasons", "Transferred to another job",
            "Sent down to the countryside for manual labor", "Started working off-farm locally",
            "Went to work away from home", "Better job in the local area",
            "Better job in another location", "Retired", "Other",
        ]
        for index, meaning in enumerate(meanings, start=1):
            code = f"fl020s{index}"
            fields = [
                field for concept in self.work for field in concept.get("source_fields", [])
                if field.get("code", "").lower() == code and field.get("wave") == "2011"
            ]
            self.assertEqual(len(fields), 1, code)
            field = fields[0]
            self.assertIn(meaning, field.get("value_labels", ""), code)
            self.assertIn("not an answer-value code", field.get("value_labels", ""), code)
            self.assertIn("DO NOT ANALYZE", field.get("value_label_status", ""), code)
            self.assertIn("selected/unselected/missing value coding not verified", field.get("value_label_status", ""), code)
            self.assertIn("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", field.get("value_label_source", ""), code)
            rows = [row for row in self.catalog if row.get("Variable.Name", "").lower() == code and "2011" in row.get("waves", "").split(",")]
            self.assertEqual(len(rows), 1, code)
            self.assertIn("DO NOT ANALYZE", rows[0].get("value_label_review", ""), code)
    def test_main_search_renderer_surfaces_locked_source_conflict(self):
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("问卷与Codebook编码冲突，已锁定不可分析", app)
        self.assertIn("DO NOT ANALYZE; questionnaire:", app)


if __name__ == "__main__":
    unittest.main()
