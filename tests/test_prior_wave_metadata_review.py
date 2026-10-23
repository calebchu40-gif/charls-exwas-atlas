import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PriorWaveMetadataReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/prior_wave_metadata_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.audit = list(csv.DictReader(f))
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_key = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in cls.catalog}

    def test_exact_source_checked_family_counts(self):
        self.assertEqual(len(self.audit), 55)
        self.assertEqual(sum(r["metadata_family"] == "prior-interview response-history routing flags" for r in self.audit), 41)
        self.assertEqual(sum(r["metadata_family"] == "prior-wave diagnosis-time answer-history flags" for r in self.audit), 14)
        for item in self.audit:
            self.assertTrue((ROOT / item["official_source"]).exists())
            self.assertIn("official wave Codebook field located", item["review_status"])

    def test_routing_metadata_stays_c_only_and_has_no_inferred_categories(self):
        for item in self.audit:
            row = self.by_key[(item["wave"], item["code"].lower())]
            self.assertEqual(row["epcf"], "c")
            self.assertEqual(row["Value.Labels"], "")
            if item["metadata_family"] == "prior-wave diagnosis-time answer-history flags":
                self.assertIn("not diagnosis status or diagnosis time", row["Harmonization.Status"])
            else:
                self.assertIn("not a respondent behavior measure", row["Harmonization.Status"])
            self.assertNotEqual(row["Value.Label.Review"], "not yet reviewed")


if __name__ == "__main__":
    unittest.main()
