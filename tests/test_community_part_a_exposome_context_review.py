import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class CommunityPartAExposomeContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = read_csv("audit/community_field_inventory_2011_v1.csv")
        cls.crosswalk = read_csv("audit/community_exposure_crosswalk_v1.csv")
        cls.overrides = read_csv("audit/catalog_role_override_review_v1.csv")
        cls.labels = read_csv("audit/community_exposure_value_labels_v1.csv")
        cls.site_c = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.site_e = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        cls.questionnaire = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.codebook = (ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8")
        cls.audit = (ROOT / "audit/community_part_a_exposome_context_review_2026-10-26.md").read_text(encoding="utf-8")

    def test_all_2011_ja_inventory_fields_have_candidate_or_explicit_metadata_disposition(self):
        inventory = {r["variable"].lower() for r in self.inventory if r["wave"] == "2011" and r["module"] == "community" and r["variable"].lower().startswith("ja")}
        mapped = {r["code"].lower() for r in self.crosswalk if r["wave"] == "2011" and r["code"].lower().startswith("ja")}
        c_only = {r["code"].lower() for r in self.overrides if r["wave"] == "2011" and r["keep_role"].lower() == "c" and r["code"].lower().startswith("ja")}
        self.assertEqual(len(inventory), 80)
        self.assertEqual(len(mapped & inventory), 69)
        self.assertEqual(len(c_only & inventory), 11)
        self.assertEqual(inventory, (mapped | c_only) & inventory)
        self.assertIn("ja012", c_only)

    def test_new_concepts_keep_routes_aggregates_and_field_specific_units(self):
        by_code = {r["code"].lower(): r for r in self.crosswalk if r["wave"] == "2011" and r["code"].lower().startswith("ja")}
        expected = {
            "ja002": "community_office_establishment_year",
            "ja004": "community_boundary_change_history",
            "ja007": "community_urban_transition_history",
            "ja009": "community_urban_transition_history",
            "ja015": "community_land_rights_certification",
            "ja023": "community_land_rights_certification",
            "ja027": "community_land_development_history",
            "ja030": "community_land_development_history",
            "ja035": "community_land_expropriation_history",
            "ja037": "community_land_expropriation_history",
            "ja051s1": "community_homestead_allocation_policy",
            "ja051s6": "community_homestead_allocation_policy",
            "ja052": "community_homestead_allocation_policy",
            "ja053": "community_homestead_allocation_policy",
            "ja043": "community_surname_concentration_context",
            "ja046_3": "community_surname_concentration_context",
        }
        for code, concept in expected.items():
            self.assertEqual(by_code[code]["concept_id"], concept)
        self.assertEqual(by_code["ja005"]["unit"], "year")
        self.assertEqual(by_code["ja006_1"]["unit"], "km²")
        self.assertEqual(by_code["ja006_2"]["unit"], "mu")
        self.assertEqual(by_code["ja037"]["unit"], "Yuan/mu")
        for code in ("ja007", "ja008", "ja009", "ja010", "ja015", "ja016", "ja023", "ja024", "ja027", "ja028", "ja030", "ja031", "ja035", "ja036", "ja053", "ja054"):
            self.assertIn("conditional", by_code[code]["caveat"].lower())

    def test_unit_selectors_and_open_text_do_not_become_candidate_exposures(self):
        c_only = {r["code"].lower() for r in self.overrides if r["wave"] == "2011" and r["keep_role"].lower() == "c"}
        for code in ("ja001", "ja003", "ja006", "ja045_1", "ja045_2", "ja045_3", "ja048", "ja052_1", "ja042_2_5_", "ja042_3_5_"):
            self.assertIn(code, c_only)
        mapped = {r["code"].lower() for r in self.crosswalk}
        for code in ("ja045_1", "ja045_2", "ja045_3", "ja052_1"):
            self.assertNotIn(code, mapped)

    def test_ja012_questionnaire_codebook_conflict_remains_unresolved(self):
        self.assertIn("among arable land, how many is irrigatable", self.codebook.lower())
        self.assertIn("among arable land, how many is paddy field", self.questionnaire.lower())
        labels = {r["code"].lower(): r for r in self.labels}
        self.assertNotIn("ja012", labels)
        self.assertIn("ja012", {r["code"].lower() for r in self.overrides if r["keep_role"].lower() == "c"})
        self.assertIn("not interchangeable", self.audit.lower())
        self.assertIn("no meaning or numeric unit is guessed", self.audit.lower())
        row = next(r for r in self.site_c if r["Variable.Name"].lower() == "ja012" and r["Source.Wave"] == "2011")
        self.assertIn("paddy-field area", row["Value.Label.Review"].lower())
        self.assertIn("excluded from e/p association matrix", row["Review.Flag"].lower())
        self.assertFalse(any(r["Variable.Name"].lower() == "ja012" and r["Source.Wave"] == "2011" for r in self.site_e))

    def test_field_name_checks_do_not_import_codebook_frequencies(self):
        for row in self.crosswalk:
            if row["code"].lower().startswith("ja") and row["mapping_status"].startswith("official questionnaire"):
                self.assertNotIn("OBS", row["source_evidence"])
                self.assertNotIn("frequency", row["source_evidence"].lower())
        self.assertIn("descriptive codebook counts/frequencies were not copied", self.audit.lower())


if __name__ == "__main__":
    unittest.main()
