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
            self.assertNotRegex(row["value_labels"], r"\b\d[,.]?\d{2,}\b|%")

    def test_2018_accessibility_keeps_do_not_need_and_2020_steps_are_continuous(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        self.assertIn("3=Do not need", lookup[("2018", "i010_w4")]["value_labels"])
        self.assertIn("3=Do not need", lookup[("2020", "i009")]["value_labels"])
        self.assertNotIn(("2020", "i010"), lookup)
        catalog_row = next(row for row in self.catalog if row["Source.Wave"] == "2020" and row["Variable.Name"].lower() == "i010")
        self.assertEqual(catalog_row["Value.Labels"], "")
        self.assertEqual(catalog_row["Harmonization.Status"], "Number/category of steps to entrance; may be top-coded or grouped and is not an individual stair-climbing performance test.")

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
