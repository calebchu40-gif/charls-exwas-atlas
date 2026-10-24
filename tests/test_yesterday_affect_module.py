import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "wb05": "affect_frustrated_yesterday",
    "wb06": "affect_sad_yesterday",
    "wb07": "affect_enthusiastic_yesterday",
    "wb08": "affect_lonely_yesterday",
    "wb09": "affect_content_yesterday",
    "wb10": "affect_worried_yesterday",
    "wb11": "affect_bored_yesterday",
    "wb12": "affect_happy_yesterday",
    "wb13": "affect_angry_yesterday",
    "wb14": "affect_tired_yesterday",
    "wb15": "affect_stressed_yesterday",
}


class YesterdayAffectModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/health_symptom_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.affect = {r["code"].lower(): r for r in cls.rows if r["code"].lower() in EXPECTED}
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        cls.health_json = json.loads((ROOT / "site-prototype/dist/health_symptoms_v1.json").read_text(encoding="utf-8"))

    def test_all_eleven_official_yesterday_feelings_are_individual_outcomes(self):
        self.assertEqual(set(self.affect), set(EXPECTED))
        for code, concept in EXPECTED.items():
            row = self.affect[code]
            self.assertEqual(row["concept_id"], concept)
            self.assertEqual(row["wave"], "2013")
            self.assertEqual(row["value_labels"], "1=Not at all; 2=A little; 3=Somewhat; 4=Quite a bit; 5=Very")
            self.assertIn("no composite mood score", row["value_label_status"])
            self.assertIn("昨天", row["note"])

    def test_public_phenotype_catalog_includes_all_items_without_frequency_data(self):
        by_code = {r["Variable.Name"].lower(): r for r in self.catalog if r["Variable.Name"].lower() in EXPECTED}
        self.assertEqual(set(by_code), set(EXPECTED))
        for code in EXPECTED:
            self.assertEqual(by_code[code]["Value.Labels"], self.affect[code]["value_labels"])
            self.assertNotRegex(by_code[code]["Value.Labels"], r"\b\d[,.]\d{3}\b")
            self.assertIn("no composite mood score", by_code[code]["Harmonization.Status"])
            self.assertIn("routed denominator requires authorized-release review", by_code[code]["Harmonization.Status"])

    def test_health_symptom_browser_keeps_the_items_separate(self):
        concepts = {x["concept_id"]: x for x in self.health_json}
        for code, concept_id in EXPECTED.items():
            self.assertIn(concept_id, concepts)
            concept = concepts[concept_id]
            self.assertEqual([f["code"].lower() for f in concept["source_fields"]], [code])
            self.assertIn("合成", concept["caveat"])


if __name__ == "__main__":
    unittest.main()
