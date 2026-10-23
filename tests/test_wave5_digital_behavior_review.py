import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import apply_wave5_digital_behavior_review as review


class Wave5DigitalBehaviorReviewTests(unittest.TestCase):
    def test_crosswalk_covers_screen_device_activity_and_digital_use_fields(self):
        mapping = review.read_mapping(review.BEHAVIOR_MAP)
        expected = {
            "da040", "da041_s1", "da041_s2", "da041_s3", "da041_s4", "da041_s5",
            "da042_s1", "da042_s2", "da042_s3", "da042_s4", "da042_s5", "da042_s6",
            "da043", "da044", "da045",
        }
        self.assertTrue(expected.issubset(mapping))
        self.assertEqual(len(expected), 15)
        self.assertTrue(all("frequencies omitted" in mapping[c]["value_label_status"] for c in expected))

    def test_exact_auto_covariate_duplicate_is_removed_and_source_route_preserved(self):
        rows = [
            {"Variable.Name": "da042_s5", "Source.Wave": "2020", "epcf": "c"},
            {"Variable.Name": "da042_s5", "Source.Wave": "2020", "epcf": "e"},
            {"Variable.Name": "da042_s5", "Source.Wave": "2018", "epcf": "c"},
            {"Variable.Name": "da029", "Source.Wave": "2020", "epcf": "p"},
        ]
        kept, reviewed, removed = review.update_rows(rows)
        self.assertEqual((reviewed, removed), (2, 1))
        self.assertEqual([(r["Variable.Name"], r["Source.Wave"], r["epcf"]) for r in kept], [
            ("da042_s5", "2020", "e"), ("da042_s5", "2018", "c"), ("da029", "2020", "p")
        ])
        digital = kept[0]
        self.assertEqual(digital["subcategory"], "internet and digital technology use")
        self.assertIn("skipped", digital["Harmonization.Status"])
        self.assertIn("997=don’t know", kept[-1]["Value.Labels"].lower())
        self.assertIn("XFAgePossibility", kept[-1]["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
