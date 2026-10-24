import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RelationshipSatisfactionCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit" / "relationship_satisfaction_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.crosswalk = list(csv.DictReader(stream))
        with (ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.catalog = list(csv.DictReader(stream))

    def test_reviewed_marriage_satisfaction_is_a_wave_specific_phenotype_candidate(self):
        rows = [r for r in self.crosswalk if r["concept_id"] == "marital_relationship_satisfaction"]
        self.assertEqual({r["wave"] for r in rows}, {"2015", "2018"})
        self.assertTrue(all(r["code"] == "dc043_w3" for r in rows))
        catalog_rows = [
            r for r in self.catalog
            if r["Variable.Name"].lower() == "dc043_w3"
            and r["Source.Wave"] in {"2015", "2018"}
            and r["epcf"] == "p"
        ]
        self.assertEqual({r["Source.Wave"] for r in catalog_rows}, {"2015", "2018"})
        self.assertTrue(all(r["category"] == "social wellbeing" for r in catalog_rows))
        self.assertTrue(all("BE001=1 或 2" in r["Concept.Mapping.Caveat"] for r in catalog_rows))

    def test_no_spouse_response_remains_outside_the_ordinal_scale(self):
        for row in self.crosswalk:
            if row["concept_id"] != "marital_relationship_satisfaction":
                continue
            self.assertIn("6=No spouse now", row["value_labels"])
            self.assertIn("separate non-ordinal status", row["value_labels"])
            self.assertIn("frequencies omitted", row["value_label_status"])
            self.assertNotIn("Codebook frequencies", row["value_labels"])

    def test_both_official_questionnaires_document_the_route(self):
        for wave in ("2015", "2018"):
            source = ROOT / "sources_official" / f"CHARLS_{wave}_Questionnaire_extracted.txt"
            text = source.read_text(encoding="utf-8", errors="replace")
            self.assertIn("If BE001 = 1", text)
            self.assertIn("DC043_W3", text)

    def test_site_uses_chinese_labels_for_the_new_phenotype_domain(self):
        app = (ROOT / "site-prototype" / "dist" / "app.js").read_text(encoding="utf-8")
        index = (ROOT / "site-prototype" / "dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn("'social wellbeing':'社会关系与主观幸福感'", app)
        self.assertIn("'marital relationship satisfaction':'婚姻关系满意度'", app)
        self.assertIn("'life satisfaction':'总体生活满意度'", app)
        self.assertIn("'health satisfaction':'健康满意度'", app)
        self.assertIn("'relationship with children satisfaction':'与子女关系满意度'", app)
        self.assertIn("'subjective life expectancy':'主观预期寿命可能性'", app)
        self.assertIn("app.js?v=68", index)


if __name__ == "__main__":
    unittest.main()
