import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SanitizedCommunityInventoryTests(unittest.TestCase):
    def test_inventory_contains_only_field_metadata_not_row_counts_or_values(self):
        path = ROOT / "audit/community_field_inventory_2011_v1.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            self.assertEqual(reader.fieldnames, ["wave", "module", "variable", "variable_label"])
        self.assertEqual(len(rows), 719)
        self.assertEqual(len({row["variable"].lower() for row in rows}), 719)
        self.assertTrue(all(row["wave"] == "2011" and row["module"] == "community" for row in rows))
        self.assertTrue(all(row["variable"] for row in rows))
        self.assertEqual([row["variable"] for row in rows if not row["variable_label"]], ["jh026_1"])
        text = path.read_text(encoding="utf-8-sig").lower()
        self.assertNotIn("module_rows", text)
        self.assertNotIn("frequenc", text)
        self.assertNotIn("respondent_id", text)


if __name__ == "__main__":
    unittest.main()
