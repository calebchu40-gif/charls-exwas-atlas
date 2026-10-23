import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HouseholdExpenditureMetadataReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.fields = list(csv.DictReader(handle))
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_56_wave_fields_have_period_and_source_review(self):
        reviewed = [r for r in self.fields if r.get("Candidate.Status") == "household-level expenditure/resource candidate; preserve item period and wave wording"]
        self.assertEqual(len(reviewed), 56)
        for row in reviewed:
            self.assertIn("CHARLS_", row["Value.Label.Source"])
            self.assertIn("Codebook", row["Value.Label.Source"])
            expected_note = "household-level indicator" if row["Variable.Name"].lower() in {"ge006_w2", "gf007"} else "wave-specific item list"
            self.assertIn(expected_note, row["Harmonization.Status"])

    def test_household_self_production_has_only_explicit_yes_no_labels(self):
        indicators = [r for r in self.catalog if r["Value.Label.Review"] == "official Codebook response categories reviewed; frequencies and percentages omitted" and r["Variable.Name"].lower() in {"ge006_w2", "gf007"}]
        self.assertEqual(len(indicators), 4)
        for row in indicators:
            self.assertEqual(row["Value.Labels"], "1=Yes; 2=No")

    def test_continuous_amounts_have_units_without_codebook_extrema(self):
        rows = [r for r in self.catalog if r["Candidate.Status"] == "household-level expenditure/resource candidate; preserve item period and wave wording" and r["Variable.Name"].lower() not in {"ge006_w2", "gf007"}]
        self.assertEqual(len(rows), 52)
        allowed = {"Yuan/week", "Yuan/month", "Yuan/year", "Yuan (past month)"}
        for row in rows:
            self.assertIn(row["Unit"], allowed, row["Variable.Name"])
            self.assertEqual(row["Value.Labels"], "", row["Variable.Name"])


if __name__ == "__main__":
    unittest.main()
