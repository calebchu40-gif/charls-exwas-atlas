import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ("2013", "da007_w2_6_2"),
    ("2015", "da007_w2_6_2"),
    ("2018", "da007_w2_6_2"),
    ("2015", "zda065_1"),
}


class ConditionEventAgeMetadataReviewTests(unittest.TestCase):
    def test_reviewed_fields_are_metadata_not_adjustment_recommendations(self):
        with (ROOT / "site-prototype/dist/catalog_c.json").open(encoding="utf-8") as stream:
            catalog = json.load(stream)
        rows = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in catalog}
        self.assertTrue(TARGETS <= rows.keys())
        for key in TARGETS:
            row = rows[key]
            self.assertEqual(row["category"], "measurement metadata")
            self.assertEqual(row["subcategory"], "condition or event timing metadata")
            self.assertIn("not a", row["Harmonization.Status"])
            self.assertIn("not a selected adjustment covariate", row["Review.Flag"])
            self.assertNotIn("not yet reviewed", row["Value.Label.Review"].lower())

    def test_audit_has_official_sources_and_does_not_copy_frequencies(self):
        with (ROOT / "audit/condition_event_age_metadata_review_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual({(r["wave"], r["code"]) for r in rows}, TARGETS)
        for row in rows:
            self.assertIn("Questionnaire_extracted.txt", row["official_sources"])
            self.assertIn("Codebook_extracted.txt", row["official_sources"])
            self.assertIn("sample summaries omitted", row["review_status"])
            self.assertNotIn("Freq.", " ".join(row.values()))
            self.assertNotIn("%", " ".join(row.values()))


if __name__ == "__main__":
    unittest.main()
