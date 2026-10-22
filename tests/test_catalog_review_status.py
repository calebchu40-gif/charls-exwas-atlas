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

    def test_main_search_renderer_surfaces_locked_source_conflict(self):
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("问卷与Codebook编码冲突，已锁定不可分析", app)
        self.assertIn("DO NOT ANALYZE; questionnaire:", app)


if __name__ == "__main__":
    unittest.main()
