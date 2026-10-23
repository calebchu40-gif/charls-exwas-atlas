import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = "housing_context_source_review_2026-10-24.md"


class HousingContextSourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit" / "food_environment_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.site = json.loads(
            (ROOT / "site-prototype" / "dist" / "food_environment_v1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_all_heating_and_gas_wave_fields_are_source_reviewed(self):
        expected = {
            (wave, concept, code)
            for wave, concept, code in (
                (w, "piped_gas_access", "i019" if w != "2020" else "i018")
                for w in ("2011", "2013", "2015", "2018", "2020")
            )
        } | {
            (wave, "residential_heating", "i020" if wave != "2020" else "i019")
            for wave in ("2011", "2013", "2015", "2018", "2020")
        }
        actual = {
            (r["wave"], r["concept_id"], r["code"].lower())
            for r in self.rows
            if REVIEW in r["mapping_status"]
        }
        self.assertEqual(actual, expected | {
            ("2020", "tap_water_access", "i016"),
            ("2020", "waterworks_treatment", "i029"),
            ("2020", "air_cleaner_home", "i024"),
            ("2015", "air_cleaner_home", "i027_w3"),
            ("2018", "air_cleaner_home", "i027_w3"),
            ("2020", "floor_condition", "i027"),
        } | {
            (wave, concept, code)
            for wave in ("2011", "2013", "2015", "2018", "2020")
            for concept, code in (("indoor_cleanliness", "i025"), ("indoor_temperature", "i026"))
        })

    def test_2020_heating_label_conflict_is_explicit_and_preserved(self):
        row = next(
            r for r in self.rows
            if r["wave"] == "2020" and r["concept_id"] == "residential_heating"
        )
        self.assertEqual(row["source_label"], "Centralized Heating")
        self.assertIn("questionnaire asks whether XFinancialResp's house has heating", row["caveat"])
        item = next(c for c in self.site if c["concept_id"] == "residential_heating")
        field = next(f for f in item["source_fields"] if f["wave"] == "2020")
        self.assertIn("wording discrepancy", field["note"])

    def test_water_air_items_have_household_and_interpretation_limits(self):
        by_code = {
            r["code"].lower(): r for r in self.rows
            if r["wave"] == "2020" and r["concept_id"] in {
                "tap_water_access", "waterworks_treatment", "air_cleaner_home"
            }
        }
        self.assertIn("XFinancialResp's house", by_code["i016"]["caveat"])
        self.assertIn("not a direct", by_code["i016"]["caveat"])
        self.assertIn("Do not know", by_code["i029"]["caveat"])
        self.assertIn("filter condition", by_code["i024"]["caveat"])
        site_by_id = {item["concept_id"]: item for item in self.site}
        self.assertIn("otherwise asking the respondent", site_by_id["air_cleaner_home"]["caveat"])

    def test_review_script_confirms_official_source_and_no_frequency_use(self):
        script = (ROOT / "scripts" / "apply_housing_context_source_review.py").read_text(
            encoding="utf-8"
        )
        questionnaire = (
            ROOT / "sources_official" / "CHARLS_2020_Questionnaire_English_extracted.txt"
        ).read_text(encoding="utf-8", errors="ignore")
        codebook = (
            ROOT / "sources_official" / "CHARLS_2020_Codebook_extracted.txt"
        ).read_text(encoding="utf-8", errors="ignore")
        self.assertIn("I024 Does [XFinancialResp]’s house have an air cleaner?", questionnaire)
        self.assertIn("IWER: Record if interviewer is in R's housing", questionnaire)
        self.assertIn("i019: Centralized Heating", codebook)
        self.assertIn("no respondent data or Codebook frequencies used", script)

    def test_air_cleaner_concept_has_reviewed_2015_2018_2020_fields(self):
        item = next(c for c in self.site if c["concept_id"] == "air_cleaner_home")
        fields = {str(f["wave"]): f for f in item["source_fields"]}
        self.assertEqual(set(fields), {"2015", "2018", "2020"})
        for wave in ("2015", "2018"):
            self.assertEqual(fields[wave]["code"].lower(), "i027_w3")
            self.assertEqual(fields[wave]["value_labels"], "1=Yes; 2=No")
            self.assertIn("questionnaire/Codebook reviewed", fields[wave]["note"])
        self.assertIn("wave-specific household referents", item["caveat"])

    def test_indoor_observer_measures_preserve_wave_labels_and_2011_source_discrepancy(self):
        expected_codes = {"indoor_cleanliness": "i025", "indoor_temperature": "i026"}
        for concept_id, code in expected_codes.items():
            concept = next(c for c in self.site if c["concept_id"] == concept_id)
            self.assertEqual({f["wave"] for f in concept["source_fields"]}, {"2011", "2013", "2015", "2018", "2020"})
            self.assertIn("interviewer-recorded", concept["caveat"])
            self.assertIn("not", concept["caveat"])
            row_2011 = next(r for r in self.rows if r["wave"] == "2011" and r["code"].lower() == code)
            row_2013 = next(r for r in self.rows if r["wave"] == "2013" and r["code"].lower() == code)
            self.assertIn("2011 source-version discrepancy", row_2011["caveat"])
            self.assertIn("interviewer-recorded", row_2013["caveat"])
        review = (ROOT / "audit" / REVIEW).read_text(encoding="utf-8")
        self.assertIn("I025 and I026", review)
        self.assertIn("baseline questionnaire lists 6=Not applicable", review)

    def test_2020_floor_condition_is_nominal_and_household_level(self):
        row = next(
            r for r in self.rows
            if r["wave"] == "2020" and r["concept_id"] == "floor_condition"
        )
        self.assertEqual(row["code"].lower(), "i027")
        self.assertEqual(row["code_value_labels"], "1=Flat covered; 2=Flat concrete; 3=Uneven")
        self.assertIn("nominal categories", row["caveat"])
        concept = next(c for c in self.site if c["concept_id"] == "floor_condition")
        self.assertIn("not a mobility or fall-risk test", concept["caveat"])
        script = (ROOT / "scripts" / "apply_housing_context_source_review.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("2020 floor-condition interviewer instruction not found", script)


if __name__ == "__main__":
    unittest.main()
