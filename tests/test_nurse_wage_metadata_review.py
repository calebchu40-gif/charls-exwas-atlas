import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NurseWageMetadataReviewTests(unittest.TestCase):
    def test_nurse_wage_is_conditional_context_not_exposure(self):
        with (ROOT / "audit/nurse_wage_metadata_review_2015_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            audit = list(csv.DictReader(stream))
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["unit"], "Yuan/month (reported wage last month)")
        self.assertIn("DB035_W3_1", audit[0]["route"])
        with (ROOT / "site-prototype/dist/catalog_c.json").open(encoding="utf-8") as stream:
            catalog = json.load(stream)
        rows = [r for r in catalog if r.get("Source.Wave") == "2015" and r.get("Variable.Name", "").lower() == "db035_w3_2"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["category"], "measurement metadata")
        self.assertEqual(row["subcategory"], "conditional nurse-care wage metadata")
        self.assertEqual(row["Unit"], audit[0]["unit"])
        self.assertIn("not an environmental exposure", row["Harmonization.Status"])
        self.assertIn("not an exposure", row["Review.Flag"])
        self.assertNotIn("not yet reviewed", row["Value.Label.Review"].lower())


if __name__ == "__main__":
    unittest.main()
