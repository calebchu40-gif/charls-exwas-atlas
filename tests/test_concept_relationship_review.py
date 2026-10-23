import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


class ConceptRelationshipReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (AUDIT / "ep_concept_link_relationship_review_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.relationships = list(csv.DictReader(stream))
        with (AUDIT / "concept_alias_canonicalization_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.aliases = list(csv.DictReader(stream))
        with (AUDIT / "ep_concept_link_collision_review_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.collisions = list(csv.DictReader(stream))

    def test_unclassified_overlaps_are_zero_and_parent_records_are_stratified(self):
        self.assertFalse(any(row["Review.Status"] == "needs manual audit before analysis" for row in self.relationships))
        ca009 = [row for row in self.relationships if row["Source.Code"] == "ca009"]
        self.assertEqual({row["Wave"] for row in ca009}, {"2013", "2015"})
        self.assertTrue(all(row["Relationship.Type"] == "relationship_stratified_parent_record_measure" for row in ca009))

    def test_physical_activity_umbrella_is_not_an_independent_measure(self):
        rows = [row for row in self.relationships if row["Relationship.Type"] == "umbrella_group_not_independent_measure"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all("not a separate overall activity response" in row["Interpretation"] for row in rows))

    def test_past_year_alcohol_binary_is_a_recode_of_frequency(self):
        rows = [row for row in self.relationships if row["Source.Code"] in {"da067", "da051"}]
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["Relationship.Type"] == "binary_derived_from_frequency_categories" for row in rows))
        self.assertTrue(all("1/2" in row["Interpretation"] and "3" in row["Interpretation"] for row in rows))

    def test_smoking_routes_preserve_wave_reference_time(self):
        with (AUDIT / "ep_concept_source_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        retrospective = [row for row in source_rows if row["Wave"] == "2015" and row["Source.Code"] == "da061_w3"]
        self.assertTrue(retrospective)
        self.assertTrue(all("not current 2015 status" in row["Caveat"] for row in retrospective))
        smoking_links = [row for row in self.relationships if row["Relationship.Type"] == "component_of_composite_status" and ("smoke_ever" in row["Candidate.Concept.IDs"] or "still_smoking_among_ever_smokers" in row["Candidate.Concept.IDs"])]
        self.assertTrue(smoking_links)
        self.assertTrue(all("missing ever-smoking response is not No" in row["Interpretation"] or "missing DA059 is therefore not equivalent to never smoking" in row["Interpretation"] for row in smoking_links))
        with (ROOT / "site-prototype" / "dist" / "catalog.json").open(encoding="utf-8") as stream:
            site_catalog = json.load(stream)
        site_w3 = [row for row in site_catalog if row["Variable.Name"].lower() == "da061_w3"]
        self.assertEqual(len(site_w3), 1)
        self.assertIn("not current 2015 status", site_w3[0].get("Concept.Mapping.Caveat", site_w3[0].get("concept_mapping_caveats", "")))

    def test_2013_life_insurance_frequency_uses_questionnaire_label_with_partial_codebook_caveat(self):
        with (AUDIT / "charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as stream:
            catalog = list(csv.DictReader(stream))
        rows = [row for row in catalog if row["Source.Wave"] == "2013" and row["Variable.Name"].lower() == "fn056_w2_5"]
        self.assertEqual(len(rows), 1)
        self.assertIn("2=Quarterly", rows[0]["Value.Labels"])
        self.assertNotEqual(rows[0]["Value.Label.Review"], "conflict")
        self.assertNotIn("DO NOT ANALYZE", rows[0]["Review.Flag"])
        self.assertIn("response-category table", rows[0]["Concept.Mapping.Caveat"])
        with (AUDIT / "pension_label_conflict_adjudication_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            decisions = list(csv.DictReader(stream))
        decision = [row for row in decisions if row["wave"] == "2013" and row["code"] == "fn056_w2_5"]
        self.assertEqual(decision[0]["decision_status"], "resolved_questionnaire_authority_codebook_category_table_partial")
        app_js = (ROOT / "site-prototype" / "dist" / "app.js").read_text(encoding="utf-8")
        self.assertIn("official questionnaire response menu reviewed; CodeBook response-category table omits questionnaire option 2", app_js)

    def test_2011_unfolding_bracket_labels_survive_pipeline_and_locks_remain_visible(self):
        with (AUDIT / "charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as stream:
            catalog = list(csv.DictReader(stream))
        rows = [row for row in catalog if row["Source.Wave"] == "2011" and row["Variable.Name"].lower() in {f"fn064_{i}" for i in range(1, 5)} | {f"fn070_{i}" for i in range(1, 5)}]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["Value.Labels"] for row in rows))
        self.assertTrue(all(row["Value.Label.Review"].startswith("official 2011 questionnaire/Codebook threshold categories transcribed") for row in rows))
        self.assertTrue(all("DO NOT ANALYZE as an amount" in row["Review.Flag"] for row in rows))
        with (AUDIT / "pension_value_label_review_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            label_review = list(csv.DictReader(stream))
        review_rows = [row for row in label_review if row["wave"] == "2011" and row["code"].lower() in {item["Variable.Name"].lower() for item in rows}]
        self.assertEqual(len(review_rows), 8)
        self.assertTrue(all("unlisted categories not inferred" in row["value_label_status"] for row in review_rows))
        app_js = (ROOT / "site-prototype" / "dist" / "app.js").read_text(encoding="utf-8")
        self.assertIn("includes('DO NOT ANALYZE')", app_js)
        self.assertIn("official 2011 questionnaire/Codebook threshold categories transcribed; no response frequencies shown", app_js)
        self.assertIn("DO NOT ANALYZE", app_js)

    def test_duplicate_2018_workforce_concept_is_an_explicit_alias(self):
        alias = [row for row in self.aliases if row["alias_concept_id"] == "last_job_business_workforce_size_2018"]
        self.assertEqual(len(alias), 1)
        self.assertEqual(alias[0]["canonical_concept_id"], "last_self_employed_business_employee_count_2018")
        self.assertFalse(any(row["Wave"] == "2018" and row["Source.Code"] == "fl012_w4" for row in self.collisions))


if __name__ == "__main__":
    unittest.main()

