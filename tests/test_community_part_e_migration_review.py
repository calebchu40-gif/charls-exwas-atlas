import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class CommunityPartEMigrationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = read_csv(Path("audit/raw_variable_catalog_v1.csv"))
        cls.crosswalk = read_csv(Path("audit/community_exposure_crosswalk_v1.csv"))
        cls.labels = read_csv(Path("audit/community_exposure_value_labels_v1.csv"))
        cls.overrides = read_csv(Path("audit/catalog_role_override_review_v1.csv"))
        cls.questionnaire = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.codebook = (ROOT / "audit/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8")
        cls.audit = (ROOT / "audit/community_part_e_migration_source_review_2026-10-26.md").read_text(encoding="utf-8")

    def test_every_inventory_field_has_a_candidate_or_explicit_c_only_disposition(self):
        inventory = {row["variable"].lower() for row in self.raw if row["wave"] == "2011" and row["module"] == "community" and row["variable"].lower().startswith("je")}
        mapped = {row["code"].lower() for row in self.crosswalk if row["wave"] == "2011" and row["code"].lower().startswith("je")}
        c_only = {row["code"].lower() for row in self.overrides if row["wave"] == "2011" and row["keep_role"].lower() == "c" and row["code"].lower().startswith("je")}
        self.assertEqual(len(inventory), 46)
        self.assertEqual(len(mapped), 44)
        self.assertEqual(inventory, mapped | {"je014", "je016"})
        self.assertEqual(c_only & inventory, {"je014", "je016"})
        self.assertNotIn("je013", inventory)
        self.assertNotIn("je015", inventory)

    def test_migration_constructs_keep_units_levels_routes_and_source_limits(self):
        rows = {row["code"].lower(): row for row in self.crosswalk if row["wave"] == "2011" and row["code"].lower().startswith("je")}
        self.assertEqual(rows["je001"]["unit"], "persons")
        self.assertEqual(rows["je002"]["unit"], "percent")
        self.assertEqual(rows["je009"]["unit"], "Yuan/month")
        self.assertEqual(rows["je011"]["unit"], "Yuan/month")
        self.assertEqual(rows["je012"]["unit"], "households")
        self.assertEqual(sum(code.startswith("je007s") for code in rows), 33)
        for row in rows.values():
            self.assertIn("Part E", row["source_evidence"])
            self.assertTrue("individual" in row["caveat"].lower() or "participant" in row["caveat"].lower())

    def test_response_labels_omit_frequencies_and_codebook_only_je016_stays_unresolved(self):
        labels = {row["code"].lower(): row for row in self.labels if row["code"].lower().startswith("je")}
        for code in ("je003", "je004", "je005", "je006"):
            self.assertIn("1=0–20%", labels[code]["value_labels"])
            self.assertIn("frequencies omitted", labels[code]["value_label_status"])
        self.assertIn("Anhui", labels["je007s1"]["value_labels"])
        self.assertIn("No Observations", labels["je007s33"]["value_label_status"])
        role = {row["code"].lower(): row for row in self.overrides if row["wave"] == "2011"}
        self.assertIn("no matching je016 item", role["je016"]["rationale"].lower())
        self.assertIn("Respondent name", self.questionnaire)
        self.assertIn("Phone number for the respondent of Part E", self.questionnaire)
        self.assertIn("je016", self.codebook.lower())
        self.assertIn("je016", self.audit.lower())


if __name__ == "__main__":
    unittest.main()
