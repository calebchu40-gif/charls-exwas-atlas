import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GenderSourceDerivationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/respondent_gender_source_derivation_crosswalk_2011_2018_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.audit = list(csv.DictReader(handle))
        cls.c_rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.ep_rows = [
            row
            for role in ("e", "p")
            for row in json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
        ]

    def test_all_module_qualified_gender_rows_are_audited(self):
        self.assertEqual(len(self.audit), 9)
        keys = {(row["wave"], row["code"], row["module"]) for row in self.audit}
        self.assertIn(("2018", "xrgender", "Demographic_Background"), keys)
        self.assertIn(("2018", "xrgender", "Health_Status_and_Functioning"), keys)
        for row in self.audit:
            for source in row["official_sources"].split("; "):
                self.assertTrue((ROOT / source).is_file(), source)

    def test_respondent_gender_labels_and_route_flag_are_distinguished(self):
        targets = {(row["wave"], row["code"], row["module"]) for row in self.audit}
        by_key = {
            (row["Source.Wave"], row["Variable.Name"].lower(), row["Data.File.Name"]): row
            for row in self.c_rows
        }
        for item in self.audit:
            key = (item["wave"], item["code"], item["module"])
            row = by_key[key]
            self.assertEqual(row["epcf"], "c")
            self.assertNotEqual(row["Value.Label.Review"], "not yet reviewed")
            if item["code"] == "zfrgender":
                self.assertEqual(row["Value.Labels"], "")
                self.assertEqual(row["subcategory"], "prior-wave gender route flag")
            else:
                self.assertEqual(row["Value.Labels"], "1=Male; 2=Female")
                self.assertEqual(row["subcategory"], "respondent gender source and derivation metadata")
        ep_keys = {(row["Source.Wave"], row["Variable.Name"].lower(), row["Data.File.Name"]) for row in self.ep_rows}
        self.assertTrue(targets.isdisjoint(ep_keys))

    def test_catalog_preserves_role_caveats_and_ui_labels(self):
        for item in self.audit:
            row = next(
                row for row in self.c_rows
                if row["Source.Wave"] == item["wave"]
                and row["Variable.Name"].lower() == item["code"]
                and row["Data.File.Name"] == item["module"]
            )
            self.assertIn("adjustment use remains estimand-specific", row["Candidate.Status"])
            self.assertIn("official_sources", item)
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("受访者性别来源与派生元数据", app)
        self.assertIn("前一波次性别信息路由标记", app)


if __name__ == "__main__":
    unittest.main()
