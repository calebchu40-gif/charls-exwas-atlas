import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PriorWaveDiagnosisAgePreloadReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/prior_wave_diagnosis_age_preload_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.audit = list(csv.DictReader(handle))
        cls.rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_key = {(row["Source.Wave"], row["Variable.Name"].lower()): row for row in cls.rows}

    def test_source_review_covers_expected_fields_and_sources(self):
        self.assertEqual(len(self.audit), 33)
        self.assertEqual(sum(row["wave"] == "2013" for row in self.audit), 19)
        self.assertEqual(sum(row["wave"] == "2015" for row in self.audit), 14)
        for item in self.audit:
            self.assertIn("Questionnaire_extracted.txt", item["official_sources"])
            self.assertIn("Codebook_extracted.txt", item["official_sources"])
            for source in item["official_sources"].split("; "):
                self.assertTrue((ROOT / source).exists())

    def test_preload_values_are_c_metadata_and_not_same_wave_ep_candidates(self):
        ep_rows = []
        for role in ("e", "p"):
            ep_rows.extend(json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8")))
        ep_keys = {(row["Source.Wave"], row["Variable.Name"].lower()) for row in ep_rows}
        for item in self.audit:
            key = (item["wave"], item["code"].lower())
            row = self.by_key[key]
            self.assertEqual(row["category"], "measurement metadata")
            self.assertEqual(row["subcategory"], "prior-wave diagnosis-time preload values")
            self.assertEqual(row["Value.Labels"], "")
            self.assertNotEqual(row["Value.Label.Review"], "not yet reviewed")
            self.assertIn("not a current-wave phenotype", row["Harmonization.Status"])
            self.assertNotIn(key, ep_keys)

    def test_ui_names_the_metadata_role_and_caveat_in_chinese(self):
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("前一波次诊断时间预载年龄值（非当前波协变量）", app)
        self.assertIn("不是当前波结局或通用调整变量", app)


if __name__ == "__main__":
    unittest.main()
