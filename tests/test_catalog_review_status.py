import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CatalogReviewStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
        cls.work = json.loads((ROOT / "site-prototype/dist/work_exposures_v1.json").read_text(encoding="utf-8"))

    def test_2011_fb010_codebook_values_and_conflict_reach_main_catalog(self):
        rows = [
            row for row in self.catalog
            if row.get("Variable.Name", "").lower() == "fb010" and "2011" in row.get("waves", "").split(",")
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertIn("4=School", row.get("value_labels", ""))
        self.assertIn("6=Other", row.get("value_labels", ""))
        self.assertIn("DO NOT ANALYZE", row.get("value_label_review", ""))
        self.assertIn("questionnaire:", row.get("value_label_review", ""))
        self.assertIn("released-data coding unresolved", row.get("value_label_review", ""))

    def test_2011_fb010_specialty_catalog_links_correct_baseline_source(self):
        fields = [
            field
            for concept in self.work
            for field in concept.get("source_fields", [])
            if field.get("code", "").lower() == "fb010" and field.get("wave") == "2011"
        ]
        self.assertEqual(len(fields), 1)
        self.assertIn("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", fields[0].get("value_label_source", ""))
        self.assertIn("DO NOT ANALYZE", fields[0].get("value_label_status", ""))

    def test_2011_fl020_option_labels_are_questionnaire_meanings_not_codes(self):
        meanings = [
            "Business closed", "Quit", "I was laid off", "I was fired",
            "I went to school", "I went abroad", "Stopped working for health reasons",
            "Stopped working for family reasons", "Transferred to another job",
            "Sent down to the countryside for manual labor", "Started working off-farm locally",
            "Went to work away from home", "Better job in the local area",
            "Better job in another location", "Retired", "Other",
        ]
        for index, meaning in enumerate(meanings, start=1):
            code = f"fl020s{index}"
            fields = [
                field for concept in self.work for field in concept.get("source_fields", [])
                if field.get("code", "").lower() == code and field.get("wave") == "2011"
            ]
            self.assertEqual(len(fields), 1, code)
            field = fields[0]
            self.assertIn(meaning, field.get("value_labels", ""), code)
            self.assertIn("not an answer-value code", field.get("value_labels", ""), code)
            self.assertIn("DO NOT ANALYZE", field.get("value_label_status", ""), code)
            self.assertIn("selected/unselected/missing value coding not verified", field.get("value_label_status", ""), code)
            self.assertIn("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", field.get("value_label_source", ""), code)
            rows = [row for row in self.catalog if row.get("Variable.Name", "").lower() == code and "2011" in row.get("waves", "").split(",")]
            self.assertEqual(len(rows), 1, code)
            self.assertIn("DO NOT ANALYZE", rows[0].get("value_label_review", ""), code)
    def test_2011_fn024_is_current_enrollment_separate_from_2013_history(self):
        wave1 = [row for row in self.catalog if row.get("Variable.Name", "").lower() == "fn024" and "2011" in row.get("waves", "").split(",")]
        self.assertEqual(len(wave1), 1)
        row = wave1[0]
        self.assertIn("pension_current_basic_plan_enrollment_among_nonretired_2011", row.get("candidate_concept_ids", ""))
        self.assertNotIn("pension_past_basic_plan_participation_when_not_currently_enrolled", row.get("candidate_concept_ids", ""))
        self.assertIn("3=No", row.get("value_labels", ""))
        self.assertNotIn("DO NOT ANALYZE", row.get("value_label_review", ""))
        wave2 = [row for row in self.catalog if row.get("Variable.Name", "").lower() == "fn022_w2" and "2013" in row.get("waves", "").split(",")]
        self.assertEqual(len(wave2), 1)
        self.assertIn("pension_past_basic_plan_participation_when_not_currently_enrolled", wave2[0].get("candidate_concept_ids", ""))

    def test_2011_fn011_amount_components_have_verified_wave_route_and_period(self):
        import csv
        codes = {f"fn011_{i}" for i in range(1, 7)}
        with (ROOT / "audit/pension_exposure_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            mapped = list(csv.DictReader(handle))
        rows = [row for row in mapped if row.get("wave") == "2011" and row.get("code", "").lower() in codes]
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertIn("route, amount period, and unit reviewed", row.get("mapping_status", ""))
            self.assertIn("FN002=3/4/5", row.get("caveat", ""))
            self.assertIn("FN009=Yes", row.get("caveat", ""))
            self.assertIn("FN011 Codebook form selector", row.get("caveat", ""))
            self.assertIn("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", row.get("value_label_source", ""))

    def test_2011_social_care_fields_keep_verified_routes_and_codebook_limits(self):
        import csv
        expected = {
            "db022s38": "Codebook reports no observations",
            "db023_38_": "Codebook summary reports one observation",
            "db031s37": "future-helper route and category reviewed",
        }
        with (ROOT / "audit/social_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            mappings = list(csv.DictReader(handle))
        for code, status_fragment in expected.items():
            rows = [row for row in mappings if row.get("wave") == "2011" and row.get("code", "").lower() == code]
            self.assertEqual(len(rows), 1, code)
            self.assertIn(status_fragment, rows[0].get("mapping_status", ""), code)
            self.assertIn("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", rows[0].get("questionnaire_source", ""), code)
            self.assertIn("CHARLS_2011_Codebook_extracted.txt", rows[0].get("value_label_source", ""), code)

    def test_2013_and_2015_fn028_date_identity_conflict_is_locked(self):
        import csv
        with (ROOT / "audit/pension_exposure_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            mapped = list(csv.DictReader(handle))
        rows = [row for row in mapped if row.get("code", "").lower() in {"fn028_w2_1", "fn028_w2_2"} and row.get("wave") in {"2013", "2015"}]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(row.get("concept_id"), "pension_basic_plan_fn028_timing_questionnaire_codebook_conflicted")
            self.assertIn("DO NOT ANALYZE", row.get("mapping_status", ""))
            self.assertIn("says start participating", row.get("mapping_status", ""))
            self.assertIn("says stop participating", row.get("mapping_status", ""))

    def test_main_search_renderer_surfaces_locked_source_conflict(self):
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("问卷与Codebook编码冲突，已锁定不可分析", app)
        self.assertIn("DO NOT ANALYZE; questionnaire:", app)

    def test_c_catalog_uses_chinese_categories_and_explains_review_status(self):
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        page = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        self.assertIn("协变量候选", app)
        self.assertIn("测量/设计元数据", app)
        self.assertIn("连续变量可能没有离散类别标签", app)
        self.assertIn("不等于建议自动调整", page)

    def test_pages_workflow_deploys_site_changes_automatically(self):
        workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
        self.assertIn("push:", workflow)
        self.assertIn("site-prototype/dist/**", workflow)
        self.assertIn("workflow_dispatch:", workflow)

    def test_active_do_not_analyze_inventory_matches_catalog_and_triage_count(self):
        catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
        active = {
            (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
            for row in catalog
            if "DO NOT ANALYZE" in str(row.get("Review.Flag", ""))
        }
        triage = (ROOT / "audit/do_not_analyze_triage_2026-10-22.md").read_text(encoding="utf-8")
        self.assertEqual(len(active), 33)
        self.assertIn(f"当前主目录有{len(active)}条唯一波次—字段分析锁定项", triage)
        self.assertNotIn(("2011", "fm033"), active)


if __name__ == "__main__":
    unittest.main()
