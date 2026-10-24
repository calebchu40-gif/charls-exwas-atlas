import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit/residential_location_metadata_review_v1.csv"


class ResidentialLocationMetadataReviewTests(unittest.TestCase):
    def test_exact_reviewed_fields_are_context_metadata(self):
        with AUDIT.open(encoding="utf-8-sig", newline="") as stream:
            audit = list(csv.DictReader(stream))
        self.assertEqual(len(audit), 13)
        with (ROOT / "site-prototype/dist/catalog_c.json").open(encoding="utf-8") as stream:
            catalog = json.load(stream)
        by_key = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in catalog}
        for item in audit:
            row = by_key[(item["wave"], item["code"].lower())]
            self.assertEqual(row["category"], "measurement metadata")
            self.assertEqual(row["subcategory"], "residential geography and migration metadata")
            self.assertIn("not a measured environmental exposure", row["Harmonization.Status"])
            self.assertIn("selected adjustment covariate", row["Review.Flag"])
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("Questionnaire", item["official_sources"])
            self.assertIn("Codebook_extracted.txt", item["official_sources"])

    def test_generated_c_shard_has_no_reproduced_geographic_code_labels(self):
        with (ROOT / "site-prototype/dist/catalog_c.json").open(encoding="utf-8") as stream:
            catalog = json.load(stream)
        for row in catalog:
            if row.get("subcategory") == "residential geography and migration metadata":
                self.assertEqual(row.get("Value.Labels"), "")
                self.assertNotIn("Freq.", row.get("Value.Label.Review", ""))


if __name__ == "__main__":
    unittest.main()
