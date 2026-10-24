import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ActivityAssignmentMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/catalog_role_override_review_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.overrides = list(csv.DictReader(stream))
        cls.rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))

    def test_random_assignment_fields_are_c_only_unresolved_metadata(self):
        reviewed = [
            row for row in self.overrides
            if row["metadata_type"] == "activity_random_subsample_marker_unresolved"
        ]
        self.assertEqual({(row["wave"], row["code"].lower()) for row in reviewed}, {
            ("2013", "da051_random"), ("2015", "da051_random")
        })
        for item in reviewed:
            self.assertEqual(item["keep_role"].lower(), "c")
            self.assertIn("unresolved", item["review_status"])
            for source in item["source_crosswalks"].split("; "):
                self.assertTrue((ROOT / source).is_file())
                text = (ROOT / source).read_text(encoding="utf-8", errors="replace").lower()
                if source.endswith("Questionnaire_extracted.txt"):
                    self.assertIn("random subsample", text)
                else:
                    self.assertIn("da051_random", text)

        by_key = {(row["Source.Wave"], row["Variable.Name"].lower()): row for row in self.rows}
        for wave in ("2013", "2015"):
            row = by_key[(wave, "da051_random")]
            self.assertEqual(row["epcf"], "c")
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("unverified", row["Harmonization.Status"])
            self.assertIn("do not infer", row["Review.Flag"].lower())
            self.assertIn("exclude from E/P association matrix", row["Review.Flag"])


if __name__ == "__main__":
    unittest.main()
