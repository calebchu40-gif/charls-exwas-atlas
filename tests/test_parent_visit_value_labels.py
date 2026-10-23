import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ParentVisitValueLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/social_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.rows = [row for row in csv.DictReader(handle) if row.get("concept_id") == "parent_visits"]
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.catalog_rows = list(csv.DictReader(handle))
        cls.site_rows = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        topics = json.loads((ROOT / "site-prototype/dist/social_exposures_v1.json").read_text(encoding="utf-8"))
        cls.topic = next(item for item in topics if item.get("concept_id") == "parent_visits")

    def test_official_field_specific_category_coverage_is_preserved(self):
        self.assertEqual(len(self.rows), 33)
        self.assertEqual({wave: sum(row["wave"] == wave for row in self.rows) for wave in ("2011", "2013", "2015", "2018")},
                         {"2011": 9, "2013": 4, "2015": 12, "2018": 8})
        full = [row for row in self.rows if "complete listed 1-10 set" in row["value_label_status"]]
        partial = [row for row in self.rows if "partial Codebook category set" in row["value_label_status"]]
        self.assertEqual((len(full), len(partial)), (27, 6))
        for row in self.rows:
            codes = [int(item.split("=", 1)[0]) for item in row["value_labels"].split("; ")]
            self.assertTrue(codes)
            self.assertEqual(codes, sorted(set(codes)))
            self.assertTrue(all(1 <= code <= 10 for code in codes))
            if row in partial:
                self.assertIn("unlisted categories not inferred", row["value_label_status"])
            self.assertNotRegex(row["value_labels"], r"\b(?:N|Freq|Percent|%)\b")

    def test_candidate_and_site_catalog_carry_wave_specific_labels_and_review(self):
        for row in self.rows:
            key = (row["wave"], row["code"].lower())
            candidate = [item for item in self.catalog_rows
                         if (item["Source.Wave"], item["Variable.Name"].lower()) == key]
            site = [item for item in self.site_rows
                    if (item["Source.Wave"], item["Variable.Name"].lower()) == key]
            self.assertTrue(candidate, key)
            self.assertTrue(site, key)
            self.assertTrue(all(item["Value.Labels"] == row["value_labels"] for item in candidate), key)
            self.assertTrue(all(item["Value.Label.Review"] == row["value_label_status"] for item in candidate), key)
            self.assertTrue(all(item["Value.Labels"] == row["value_labels"] for item in site), key)
            self.assertTrue(all(item["Value.Label.Review"] == row["value_label_status"] for item in site), key)

    def test_focused_topic_has_labels_without_frequency_counts(self):
        fields = self.topic["source_fields"]
        self.assertEqual(len(fields), 33)
        for item in fields:
            self.assertIn("=", item.get("value_labels", ""))
            self.assertIn("sources_official/CHARLS_", item.get("value_label_source", ""))
            self.assertNotRegex(item["value_labels"], r"\b(?:N|Freq|Percent|%)\b")


if __name__ == "__main__":
    unittest.main()
