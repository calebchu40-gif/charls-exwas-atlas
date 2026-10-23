import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommunityPollutionLabelOverrideTests(unittest.TestCase):
    def test_questionnaire_anchors_override_misleading_codebook_gloss(self):
        with (ROOT / "audit" / "community_questionnaire_label_overrides_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as f:
            rows = list(csv.DictReader(f))
        by_code = {row["code"]: row for row in rows}
        expected = (
            "1=Very severe (very serious pollution); 2=Some pollution; "
            "3=Almost none; 4=Completely absent"
        )
        for code in ("jb018", "jb019"):
            with self.subTest(code=code):
                self.assertEqual(by_code[code]["value_labels"], expected)
                self.assertIn("questionnaire semantics reconciled", by_code[code]["value_label_status"])
                self.assertIn("higher codes indicate less reported pollution", by_code[code]["rationale"])

    def test_override_is_supported_by_official_questionnaire_text(self):
        questionnaire = (
            ROOT / "sources_official" / "CHARLS_2011_Community_Questionnaire_official_extracted.txt"
        ).read_text(encoding="utf-8")
        for anchor in ("JB018", "JB019", "很严重", "有一些", "基本没有", "完全没有"):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, questionnaire)

    def test_nearest_industrial_site_is_a_village_level_kilometre_measure(self):
        with (ROOT / "audit" / "community_exposure_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as f:
            rows = list(csv.DictReader(f))
        by_code = {row["code"].lower(): row for row in rows}
        nearby = by_code["jb019"]
        distance = by_code["jb027"]
        self.assertIn("village-only CAPI", nearby["source_evidence"])
        self.assertIn("km", distance["unit"])
        self.assertIn("village-only CAPI", distance["source_evidence"])
        self.assertIn("0 when the site is in the village", distance["caveat"])
        self.assertIn("not an individual's home-to-source distance", distance["caveat"])

    def test_distance_unit_and_zero_rule_are_from_official_questionnaire(self):
        questionnaire = (
            ROOT / "sources_official" / "CHARLS_2011_Community_Questionnaire_official_extracted.txt"
        ).read_text(encoding="utf-8")
        normalized = " ".join(questionnaire.split()).lower()
        self.assertIn("how far is the closest industrial pollution site", normalized)
        self.assertIn("answer 0 if located in the village", normalized)
        self.assertIn("km公里", normalized)


    def test_weather_units_and_referent_follow_2011_questionnaire(self):
        with (ROOT / "audit" / "community_exposure_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as f:
            rows = list(csv.DictReader(f))
        by_code = {row["code"].lower(): row for row in rows}
        self.assertEqual(by_code["ja039_1"]["unit"], "degrees Celsius (°C)")
        self.assertEqual(by_code["ja039_2"]["unit"], "degrees Celsius (°C)")
        self.assertEqual(by_code["ja040"]["unit"], "days")
        self.assertEqual(by_code["ja041"]["unit"], "days")
        self.assertIn("calendar year 2010", by_code["ja039_1"]["caveat"])
        questionnaire = (ROOT / "sources_official" / "CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        normalized = " ".join(questionnaire.split()).lower()
        self.assertIn("highest and lowest temperature for the last calendar year (2010)", normalized)
        self.assertIn("centigrade", normalized)
        self.assertIn("how many days are rainy days", normalized)
        self.assertIn("how many days are snowy days", normalized)
        self.assertIn("not linked to a weather station", by_code["ja040"]["caveat"].lower())
        items = json.loads((ROOT / "site-prototype" / "dist" / "community_exposures_v1.json").read_text(encoding="utf-8"))
        weather = next(item for item in items if item["concept_id"] == "community_weather")
        fields = {field["code"].lower(): field for field in weather["source_fields"]}
        self.assertEqual(fields["ja041"]["unit"], "days")
        self.assertIn("not linked to a weather station", fields["ja041"]["caveat"].lower())

    def test_public_community_table_carries_field_specific_pollution_caveats(self):
        items = json.loads((ROOT / "site-prototype" / "dist" / "community_exposures_v1.json").read_text(encoding="utf-8"))
        concept = next(item for item in items if item["concept_id"] == "community_industrial_pollution")
        nearby = next(field for field in concept["source_fields"] if field["code"].lower() == "jb019")
        distance = next(field for field in concept["source_fields"] if field["code"].lower() == "jb027")
        self.assertIn("Village-only route", nearby["caveat"])
        self.assertEqual(distance["unit"], "km")
        self.assertIn("not an individual's home-to-source distance", distance["caveat"])
        self.assertIn("field.caveat", (ROOT / "site-prototype" / "dist" / "app.js").read_text(encoding="utf-8"))
        self.assertIn("community_exposures_v1.json?v=4", (ROOT / "site-prototype" / "dist" / "app.js").read_text(encoding="utf-8"))
        html = (ROOT / "site-prototype" / "dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn("104个候选概念、198条字段映射", html)
        self.assertIn("JB018本村污染等级、JB019邻近村镇污染等级", html)
        self.assertIn("JB027村庄至污染源距离（公里", html)


if __name__ == "__main__":
    unittest.main()
