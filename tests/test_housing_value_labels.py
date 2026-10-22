import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class HousingValueLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels = read_csv(AUDIT / "housing_value_label_review_v1.csv")
        cls.catalog = read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv")
        cls.crosswalk = read_csv(AUDIT / "ep_concept_source_crosswalk_v1.csv")
        with (ROOT / "site-prototype" / "dist" / "housing_catalog_v1.json").open(encoding="utf-8") as stream:
            cls.housing_site = json.load(stream)

    def test_structure_categories_are_wave_specific_and_omit_codebook_frequencies(self):
        labels = {(row["wave"], row["code"]): row["value_labels"] for row in self.labels}
        self.assertIn("8=Tent", labels[("2011", "i004")])
        self.assertNotIn("8=", labels[("2013", "i004")])
        self.assertIn("7=Other", labels[("2020", "i001")])
        for row in self.labels:
            self.assertNotRegex(row["value_labels"], r"\b\d{1,3},\d{3}\b|\b\d{2,}\.\d{1,2}\b|%")

    def test_2018_accessibility_keeps_do_not_need_and_2020_steps_are_continuous(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        self.assertIn("3=Do not need", lookup[("2018", "i010_w4")]["value_labels"])
        self.assertIn("3=Do not need", lookup[("2020", "i009")]["value_labels"])
        self.assertNotIn(("2020", "i010"), lookup)
        catalog_row = next(row for row in self.catalog if row["Source.Wave"] == "2020" and row["Variable.Name"].lower() == "i010")
        self.assertEqual(catalog_row["Value.Labels"], "")
        self.assertEqual(catalog_row["Harmonization.Status"], "Number/category of steps to entrance; may be top-coded or grouped and is not an individual stair-climbing performance test.")

    def test_household_connectivity_and_air_cleaner_keep_wave_specific_codes(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for key in (("2011", "i023"), ("2013", "i023"), ("2015", "i023"), ("2018", "i023"), ("2020", "i022"),
                    ("2011", "i024"), ("2013", "i024"), ("2015", "i024"), ("2018", "i024"), ("2020", "i023"),
                    ("2015", "i027_w3"), ("2018", "i027_w3"), ("2020", "i024")):
            self.assertEqual(lookup[key]["value_labels"], "1=Yes; 2=No", key)
        self.assertEqual(lookup[("2020", "i027")]["value_labels"], "1=Flat covered; 2=Flat concrete; 3=Uneven")

    def test_residence_use_and_single_wave_housing_categories_are_labeled(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for wave in ("2011", "2013", "2015", "2018"):
            self.assertEqual(lookup[(wave, "i003")]["value_labels"], "1=Yes; 2=No")
        self.assertIn("4=Special zone", lookup[("2018", "i000_w4_2")]["value_labels"])
        self.assertIn("8=Other", lookup[("2018", "i000_w4_3")]["value_labels"])
        self.assertEqual(lookup[("2020", "i027")]["value_labels"], "1=Flat covered; 2=Flat concrete; 3=Uneven")

    def test_interviewer_observed_home_conditions_preserve_not_applicable_and_water_dk(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        self.assertNotIn("6=Not applicable", lookup[("2011", "i025")]["value_labels"])
        self.assertIn("6=Not applicable", lookup[("2013", "i025")]["value_labels"])
        self.assertIn("6=Not applicable", lookup[("2013", "i026")]["value_labels"])
        self.assertIn("5=Very cold", lookup[("2011", "i026")]["value_labels"])
        self.assertEqual(lookup[("2020", "i016")]["value_labels"], "1=Yes; 2=No")
        self.assertEqual(lookup[("2020", "i029")]["value_labels"], "1=Yes; 2=No; 997=Do not know")

    def test_heating_fuels_remain_nominal_and_preserve_no_heating_codes(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for key in (("2011", "i021"), ("2013", "i021"), ("2015", "i021")):
            self.assertIn("7=Other", lookup[key]["value_labels"])
            self.assertNotIn("8=", lookup[key]["value_labels"])
        self.assertIn("8=Heating provided", lookup[("2018", "i021_w4")]["value_labels"])
        self.assertIn("8=Do not heating", lookup[("2020", "i020")]["value_labels"])
        for key in (("2011", "i020"), ("2013", "i020"), ("2015", "i020"), ("2018", "i020"), ("2020", "i019")):
            self.assertEqual(lookup[key]["value_labels"], "1=Yes; 2=No")

    def test_basic_sanitation_energy_and_shower_fields_keep_wave_code_shifts(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for key in (("2011", "i016"), ("2013", "i016"), ("2018", "i016"), ("2020", "i015"),
                    ("2011", "i019"), ("2013", "i019"), ("2015", "i019"), ("2018", "i019"), ("2020", "i018"),
                    ("2011", "i015"), ("2013", "i015"), ("2015", "i015"), ("2018", "i015"), ("2020", "i014")):
            self.assertEqual(lookup[key]["value_labels"], "1=Yes; 2=No", key)
        for wave in ("2011", "2013", "2015", "2018"):
            self.assertEqual(lookup[(wave, "i018")]["value_labels"], "1=Hot water provided; 2=Water heater installed by the household; 3=No")
        self.assertEqual(lookup[("2020", "i017")]["value_labels"], "1=Unified hot water supply; 2=Water heater; 3=No")
        self.assertEqual(lookup[("2020", "i016")]["value_labels"], "1=Yes; 2=No")

    def test_reviewed_labels_reach_field_catalog_concept_crosswalk_and_housing_page(self):
        key = ("2018", "i010_w4")
        field = next(row for row in self.catalog if (row["Source.Wave"], row["Variable.Name"].lower()) == (key[0], key[1]))
        self.assertEqual(field["Value.Label.Review"], "Official Codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding")
        self.assertEqual(field["Value.Label.Source"], "sources_official/CHARLS_2018_Codebook_extracted.txt")
        mapped = [row for row in self.crosswalk if row["Wave"] == key[0] and row["Source.Code"].lower() == key[1]]
        self.assertTrue(mapped)
        self.assertTrue(all("3=Do not need" in row["Value.Labels"] for row in mapped))
        site = [row for row in self.housing_site if row["wave"] == key[0] and row["code"].lower() == key[1]]
        self.assertTrue(site)
        self.assertTrue(all("3=Do not need" in row["value_labels"] for row in site))


if __name__ == "__main__":
    unittest.main()
