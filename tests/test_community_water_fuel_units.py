import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommunityWaterFuelUnitTests(unittest.TestCase):
    def test_water_and_fuel_counts_are_household_counts_with_limits(self):
        with (ROOT / "audit" / "community_exposure_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as f:
            rows = list(csv.DictReader(f))
        by_code = {row["code"].lower(): row for row in rows}
        for prefix, last in (("jb006_", 8), ("jb007_", 6)):
            for number in range(1, last + 1):
                code = f"{prefix}{number}"
                with self.subTest(code=code):
                    self.assertEqual(by_code[code]["unit"], "households")
                    self.assertIn("may overlap", by_code[code]["caveat"])
                    self.assertIn("no total-household denominator", by_code[code]["caveat"])

    def test_source_questionnaire_defines_reference_period_and_household_unit(self):
        questionnaire = (
            ROOT / "sources_official" / "CHARLS_2011_Community_Questionnaire_official_extracted.txt"
        ).read_text(encoding="utf-8")
        questionnaire = re.sub(r"\s+", " ", questionnaire).lower()
        self.assertIn("at the end of the last calendar year (2010)", questionnaire)
        self.assertIn("(households)户", questionnaire)
        self.assertIn("how many households in your village use fuel", questionnaire)

    def test_site_metadata_displays_count_unit_and_denominator_caveat(self):
        import json

        items = json.loads(
            (ROOT / "site-prototype" / "dist" / "community_exposures_v1.json").read_text(
                encoding="utf-8"
            )
        )
        by_id = {item["concept_id"]: item for item in items}
        for concept_id in ("community_water_sources", "community_cooking_fuel_profile"):
            with self.subTest(concept_id=concept_id):
                item = by_id[concept_id]
                self.assertIn("no total-household denominator", item["caveat"])
                self.assertTrue(all(field["unit"] == "households" for field in item["source_fields"]))


if __name__ == "__main__":
    unittest.main()
