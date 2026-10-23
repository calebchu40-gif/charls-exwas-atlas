import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/build_objective_measurement_crosswalk.py"
spec = importlib.util.spec_from_file_location("objective_measurement_crosswalk", MODULE_PATH)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ObjectiveMeasurementCrosswalkTests(unittest.TestCase):
    def test_wave_sources_are_specific_and_official(self):
        rows = builder.build_rows()
        self.assertEqual(len(rows), 45)
        by_wave = {wave: next(row for row in rows if row["wave"] == wave) for wave in ("2011", "2013", "2015")}
        self.assertIn("Physical_Examination_Questionnaire_official.doc", by_wave["2011"]["source_document"])
        self.assertIn("CHARLS_2013_Biomarker_Questionnaire.pdf", by_wave["2013"]["source_document"])
        self.assertIn("CHARLS_2015_Biomarker_Questionnaire.pdf", by_wave["2015"]["source_document"])

    def test_2011_item_ids_are_not_asserted_as_release_variable_equivalents(self):
        rows = builder.build_rows()
        wave_2011 = [row for row in rows if row["wave"] == "2011"]
        self.assertTrue(all("不能仅凭相似题意视为同一字段" in row["source_status"] for row in wave_2011))
        self.assertTrue(all("不代表LI*与QA*/QB*/QC*代码一一对应" in row["source_caveat"] for row in wave_2011))

    def test_candidate_status_does_not_claim_field_level_validation(self):
        for row in builder.build_rows():
            self.assertIn("候选", row["source_status"])
            self.assertTrue(row["source_document"].startswith("sources_official/"))
            self.assertIn("all listed candidate code tokens found", row["codebook_presence"])
            self.assertIn("does not confirm", row["codebook_presence"])

    def test_wave_specific_codebook_labels_are_preserved_without_summary_statistics(self):
        rows = builder.build_rows()
        bp_2011 = next(r for r in rows if r["concept_id"] == "systolic_bp" and r["wave"] == "2011")
        waist_2013 = next(r for r in rows if r["concept_id"] == "waist_circumference" and r["wave"] == "2013")
        weight_2013 = next(r for r in rows if r["concept_id"] == "body_weight" and r["wave"] == "2013")
        self.assertIn("qa003=Systolic Reading", bp_2011["source_field_labels"])
        self.assertIn("qm002=Waist Circumference", waist_2013["source_field_labels"])
        self.assertIn("ql002=Weight Measuremen [extraction clipped at page boundary]", weight_2013["source_field_labels"])
        for row in rows:
            self.assertNotIn("Mean", row["source_field_labels"])
            self.assertNotIn("OBS", row["source_field_labels"])

    def test_site_explains_wave_scope_and_searchable_source_labels(self):
        html = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn("2018 Wave 4 User’s Guide", html)
        self.assertIn("非血液生物标志物（如人体测量和血压）采集于Wave 1–3", html)
        self.assertIn("2021–2023称为第五轮常规调查", html)
        self.assertIn("尚未取得并核验2021–2023常规调查的发布文件", html)
        self.assertIn("变量名不同也不能单独证明测量不存在", html)
        self.assertIn("官方Codebook字段标签", html)
        self.assertIn("source_field_labels", app)
        self.assertIn("objective_measurements_v1.json?v=2", app)


if __name__ == "__main__":
    unittest.main()
