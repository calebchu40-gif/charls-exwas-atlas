import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReproductiveHistoryPreloadMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/reproductive_history_preload_metadata_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.audit = list(csv.DictReader(handle))
        cls.c_rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.ep_rows = [
            row
            for role in ("e", "p")
            for row in json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
        ]

    def test_audit_uses_official_questionnaire_and_codebook(self):
        self.assertEqual({row["code"] for row in self.audit}, {"zda026_2", "zda028_2"})
        for row in self.audit:
            self.assertIn("CHARLS_2013_Questionnaire_extracted.txt", row["official_sources"])
            self.assertIn("CHARLS_2013_Codebook_extracted.txt", row["official_sources"])
            self.assertTrue((ROOT / "sources_official/CHARLS_2013_Questionnaire_extracted.txt").exists())
            self.assertTrue((ROOT / "sources_official/CHARLS_2013_Codebook_extracted.txt").exists())

    def test_preloads_remain_c_metadata_and_are_excluded_from_ep(self):
        targets = {("2013", row["code"]) for row in self.audit}
        catalog = {(row["Source.Wave"], row["Variable.Name"].lower()): row for row in self.c_rows}
        for key in targets:
            row = catalog[key]
            self.assertEqual(row["category"], "measurement metadata")
            self.assertEqual(row["subcategory"], "prior-wave reproductive-history preload values")
            self.assertEqual(row["Value.Labels"], "")
            self.assertNotEqual(row["Value.Label.Review"], "not yet reviewed")
            self.assertIn("not a newly measured 2013 exposure or phenotype", row["Harmonization.Status"])
        ep_keys = {(row["Source.Wave"], row["Variable.Name"].lower()) for row in self.ep_rows}
        self.assertTrue(targets.isdisjoint(ep_keys))

    def test_site_explains_historical_role_in_chinese(self):
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("前一波次生殖史预载年龄值（非当前波暴露/结局）", app)
        self.assertIn("前波生殖史预载元数据", app)


if __name__ == "__main__":
    unittest.main()
