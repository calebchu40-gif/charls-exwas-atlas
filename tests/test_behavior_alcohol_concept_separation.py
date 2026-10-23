import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BehaviorAlcoholConceptSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit" / "behavior_exposure_variable_mapping_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.alcohol = [row for row in cls.rows if row["concept_id"].startswith("alcohol_")]

    def test_frequency_and_last_drink_quantity_are_separate_concepts(self):
        frequency = [row for row in self.alcohol if row["concept_id"] == "alcohol_frequency"]
        quantity = [row for row in self.alcohol if row["concept_id"] == "alcohol_quantity_last_drink"]
        self.assertEqual({row["code"] for row in frequency if row["wave"] == "2020"}, {"da052"})
        self.assertTrue(all(row["code"] in {"da072", "da074", "da076", "da052"} for row in frequency))
        self.assertTrue(all(row["code"] in {"da073", "da075_1", "da075_2", "da077"} for row in quantity))
        self.assertFalse(set(row["code"] for row in frequency) & set(row["code"] for row in quantity))

    def test_beer_unit_selector_is_not_listed_as_an_exposure(self):
        self.assertFalse(any(row["code"] == "da075" for row in self.alcohol))
        with (ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            catalog = list(csv.DictReader(stream))
        selectors = [row for row in catalog if row["Variable.Name"].lower() == "da075"]
        self.assertEqual({row["Source.Wave"] for row in selectors}, {"2011", "2013", "2015", "2018"})
        self.assertTrue(all(row["epcf"] == "c" and row["category"] == "measurement metadata" for row in selectors))
        self.assertTrue(all(row["Value.Labels"] == "1=Bottles; 2=Mugs" for row in selectors))

    def test_site_payload_preserves_separation_and_quantity_caveat(self):
        concepts = json.loads((ROOT / "site-prototype" / "dist" / "behavior_exposures_v1.json").read_text(encoding="utf-8"))
        by_id = {item["concept_id"]: item for item in concepts}
        self.assertIn("alcohol_frequency", by_id)
        self.assertIn("alcohol_quantity_last_drink", by_id)
        quantity_fields = by_id["alcohol_quantity_last_drink"]["source_fields"]
        self.assertTrue(all("no grams of ethanol derived" in item["value_semantics"] for item in quantity_fields))


if __name__ == "__main__":
    unittest.main()
