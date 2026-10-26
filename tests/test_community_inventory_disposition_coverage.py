import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityInventoryDispositionCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):
            with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
                return list(csv.DictReader(stream))

        cls.inventory = read("audit/community_field_inventory_2011_v1.csv")
        cls.crosswalk = read("audit/community_exposure_crosswalk_v1.csv")
        cls.value_labels = read("audit/community_exposure_value_labels_v1.csv")
        cls.overrides = read("audit/catalog_role_override_review_v1.csv")
        cls.catalog = read("audit/charls_atlas_candidate_fields_v0.csv")

    def test_all_2011_community_inventory_fields_have_a_documented_disposition(self):
        source_codes = {row["variable"].casefold() for row in self.inventory}
        mapped = {row["code"].casefold() for row in self.crosswalk if row["wave"] == "2011"}
        metadata_overrides = {
            row["code"].casefold()
            for row in self.overrides
            if row["wave"] == "2011" and row["keep_role"].casefold() == "c"
        }
        catalog_c = {
            row["Variable.Name"].casefold()
            for row in self.catalog
            if row["Source.Wave"] == "2011"
            and row["Data.File.Name"].casefold() == "community"
            and row["epcf"].casefold() == "c"
        }
        documented_linkage_keys = {"communityid", "sub_commuid"}
        self.assertEqual(len(source_codes), 719)
        self.assertEqual(source_codes - mapped - metadata_overrides - catalog_c, documented_linkage_keys)
        self.assertTrue(source_codes <= mapped | metadata_overrides | catalog_c | documented_linkage_keys)

    def test_new_health_facility_location_fields_are_separate_candidate_metadata(self):
        fields = {row["code"].casefold() for row in self.crosswalk}
        expected = {f"jf003_{level}_{facility}_" for facility in range(1, 9) for level in range(1, 5)}
        self.assertEqual(len(expected), 32)
        self.assertTrue(expected <= fields)
        concepts = {row["code"].casefold(): row["concept_id"] for row in self.crosswalk}
        self.assertEqual({concepts[code] for code in expected}, {"community_health_facility_geographic_scope"})
        labels = {row["code"].casefold(): row for row in self.value_labels}
        self.assertEqual(labels["jf003_1_1_"]["value_labels"], "1=This province; 2=Other province")
        self.assertEqual(labels["jf003_2_1_"]["value_labels"], "1=This county / city; 2=Other county / city")
        for code in expected:
            self.assertEqual(labels[code]["value_label_status"], "official codebook response labels; frequencies omitted")
            self.assertNotIn("Freq.", labels[code]["value_labels"])

    def test_informant_and_codebook_only_fields_remain_metadata(self):
        overrides = {
            row["code"].casefold(): row
            for row in self.overrides
            if row["wave"] == "2011" and row["keep_role"].casefold() == "c"
        }
        expected_types = {
            "jh001_1": "community_part_h_informant_metadata",
            "jh002_1_1_": "community_part_h_informant_metadata",
            "jh031": "community_part_h_open_text",
            "jj034": "community_part_j_informant_role",
            "jj036": "community_part_j_codebook_only_unresolved",
            "jj037s1": "community_part_j_codebook_only_unresolved",
            "jj038_1": "community_part_j_codebook_only_unresolved",
            "jj038s1": "community_part_j_codebook_only_unresolved",
            "jk007": "community_part_k_interviewer_observation",
        }
        for code, metadata_type in expected_types.items():
            with self.subTest(code=code):
                self.assertEqual(overrides[code]["metadata_type"], metadata_type)


if __name__ == "__main__":
    unittest.main()
