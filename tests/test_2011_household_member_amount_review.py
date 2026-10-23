import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
def status(wave):
    return (
        f"official {wave} questionnaire identifies Yuan amount period and household-member roster slot; "
        "continuous amount with no discrete response categories; authorized-release storage scale and special values remain unverified"
    )


class HouseholdMemberAmountReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/household_member_income_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.crosswalk = [row for row in csv.DictReader(handle) if row.get("wave") in {"2011", "2013", "2015"} and row.get("value_label_status") == status(row.get("wave"))]
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_2011_roster_amount_units_and_periods_are_explicit(self):
        self.assertEqual({wave: sum(row["wave"] == wave for row in self.crosswalk) for wave in ("2011", "2013", "2015")},
                         {"2011": 80, "2013": 24, "2015": 20})
        for row in self.crosswalk:
            expected = "Yuan/year" if row["concept_id"].endswith("_annual") else "Yuan/month"
            self.assertEqual(row["unit"], expected, row["code"])
            self.assertIn("household-member roster slot", row["value_semantics"])
            self.assertIn("do not sum slots", row["value_semantics"].lower())
            self.assertIn("storage scale and special values remain unverified", row["value_label_status"])

    def test_candidate_site_rows_are_continuous_and_not_given_fabricated_categories(self):
        for row in self.crosswalk:
            site = [item for item in self.catalog
                    if item.get("Source.Wave") == row["wave"]
                    and item.get("Variable.Name", "").lower() == row["code"].lower()]
            self.assertTrue(site, row["code"])
            self.assertTrue(all(item.get("Unit") == row["unit"] for item in site), row["code"])
            self.assertTrue(all(item.get("Value.Label.Review") == status(row["wave"]) for item in site), row["code"])
            self.assertTrue(all(not item.get("Value.Labels") for item in site), row["code"])
            self.assertTrue(all("roster slot" in item.get("Harmonization.Status", "") for item in site), row["code"])


if __name__ == "__main__":
    unittest.main()
