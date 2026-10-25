import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_CONCEPTS = {
    "community_population_hukou_profile": {
        "jc001", "jc002", "jc003", "jc003_1", "jc004", "jc004_1", "jc005", "jc005_1", "jc007", "jc008"
    },
    "community_short_term_migrant_population": {"jc006"},
    "community_age_sex_structure": {"jc009", "jc009_1", "jc010", "jc010_1", "jc011", "jc011_1"},
    "community_never_married_over40_population": {"jc012", "jc012_1"},
    "community_ethnic_minority_household_profile": {"jc013", "jc013_1", "jc015", "jc017", "jc018"},
}


class CommunityPopulationSourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):
            with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
                return list(csv.DictReader(stream))
        cls.raw = read("audit/raw_variable_catalog_v1.csv")
        cls.crosswalk = read("audit/community_exposure_crosswalk_v1.csv")
        cls.overrides = read("audit/catalog_role_override_review_v1.csv")
        cls.fields = read("audit/charls_atlas_candidate_fields_v0.csv")
        cls.site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))
        cls.audit = (ROOT / "audit/community_part_c_population_source_coverage_review_2026-10-26.md").read_text(encoding="utf-8")

    def test_every_part_c_source_field_has_a_disposition(self):
        inventory = {
            row["variable"].lower() for row in self.raw
            if row.get("wave") == "2011" and row.get("module", "").lower() == "community"
            and row.get("variable", "").lower().startswith("jc")
        }
        mapped = {row["code"].lower() for row in self.crosswalk if row.get("wave") == "2011" and row.get("code", "").lower().startswith("jc")}
        excluded = {row["code"].lower() for row in self.overrides if row.get("wave") == "2011" and row.get("keep_role", "").lower() == "c" and row.get("code", "").lower().startswith("jc")}
        self.assertEqual(len(inventory), 39)
        self.assertEqual(len(mapped), 36)
        self.assertEqual(mapped & excluded, set())
        self.assertEqual(inventory - mapped, {"jc014", "jc016", "jc026"})
        self.assertEqual(inventory, mapped | (inventory - mapped))
        self.assertIn("JC013=No routes to JC019", self.audit)

    def test_new_concept_maps_and_units_preserve_aggregate_definitions(self):
        rows = {row["code"].lower(): row for row in self.crosswalk if row.get("wave") == "2011"}
        site = {item["concept_id"]: item for item in self.site}
        for concept, expected in NEW_CONCEPTS.items():
            actual = {code for code, row in rows.items() if row["concept_id"] == concept}
            source_fields = {field["code"].lower(): field for field in site[concept]["source_fields"]}
            self.assertEqual(actual, expected)
            self.assertEqual(set(source_fields), expected)
            self.assertIn("community-informant", site[concept]["caveat"].lower())
            for code in expected:
                self.assertIn("official questionnaire slot/route", rows[code]["mapping_status"])
                self.assertTrue(rows[code]["source_evidence"].startswith("CHARLS 2011 Community Questionnaire, Part C"))
                self.assertEqual(source_fields[code]["wave"], "2011")

    def test_open_text_names_and_informant_role_are_c_metadata_only(self):
        c_rows = {
            row["Variable.Name"].lower(): row for row in self.fields
            if row.get("Source.Wave") == "2011" and row.get("epcf", "").lower() == "c"
        }
        for code in ("jc014", "jc016"):
            self.assertIn(code, c_rows)
            self.assertIn("do not expose respondent text", c_rows[code]["Review.Flag"].lower())
            self.assertEqual(c_rows[code]["Value.Labels"], "")
        self.assertIn("jc026", c_rows)
        self.assertIn("never use a community-informant role", c_rows["jc026"]["Review.Flag"].lower())
        self.assertNotIn("jc014", {code for fields in (item["source_fields"] for item in self.site) for code in [f["code"].lower() for f in fields]})


if __name__ == "__main__":
    unittest.main()
