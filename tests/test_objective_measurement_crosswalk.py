import importlib.util
import csv
import json
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

    def test_concept_labels_are_not_overwritten_by_last_codebook_field_label(self):
        labels = {concept: label for concept, label, _domain, _codes, _note in builder.FIELDS}
        rows = builder.build_rows()
        self.assertEqual({r["concept_id"]: r["concept_label"] for r in rows}, labels)
        self.assertEqual(labels["walking_speed"], "计时步行表现（2.5米，两次计时）")

    def test_walking_trials_are_timed_seconds_with_preserved_status_codes(self):
        rows = [r for r in builder.build_rows() if r["concept_id"] == "walking_speed"]
        self.assertEqual({r["wave"] for r in rows}, {"2011", "2013", "2015"})
        for row in rows:
            self.assertIn("2.5米", row["value_semantics"])
            self.assertIn("秒", row["value_semantics"])
            self.assertIn("993", row["value_semantics"])
            self.assertIn("999", row["value_semantics"])
            self.assertIn("2.5米", row["source_status"])
            self.assertIn("not elapsed seconds", row["source_caveat"])
        self.assertIn("LI与QG字段逐项等同", next(r for r in rows if r["wave"] == "2011")["source_caveat"])

    def test_final_catalog_maps_timed_walk_to_phenotype_only(self):
        p_rows = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        e_rows = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        targets = [
            r for r in p_rows
            if r.get("Source.Wave") in {"2011", "2013", "2015"}
            and r.get("Variable.Name", "").lower() in {"qg002", "qg003"}
            and r.get("category", "").lower() == "physical function"
        ]
        self.assertEqual({(r["Source.Wave"], r["Variable.Name"].lower()) for r in targets}, {
            (wave, code) for wave in ("2011", "2013", "2015") for code in ("qg002", "qg003")
        })
        self.assertTrue(all(r["Unit"] == "seconds" for r in targets))
        self.assertTrue(all(r["Concept.ID.Candidates"] == "walking_speed" for r in targets))
        self.assertTrue(all("not yet reviewed" not in r["Value.Label.Review"].lower() for r in targets))
        self.assertFalse(any(
            r.get("Source.Wave") in {"2011", "2013", "2015"}
            and r.get("Variable.Name", "").lower() in {"qg002", "qg003"}
            for r in e_rows
        ))

    def test_objective_p_concepts_attach_outside_physical_function_category(self):
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as handle:
            catalog = list(csv.DictReader(handle))
        target_codes = {"qa003", "qa004", "qa005", "qa007", "qa008", "qa009", "qa011", "qa012", "qa013", "qk002"}
        targets = [row for row in catalog if row.get("Source.Wave") in {"2011", "2013", "2015"}
                   and row.get("Variable.Name", "").lower() in target_codes
                   and row.get("category", "").lower() in {"blood pressure", "anthropometric"}]
        expected = {(wave, code) for wave in ("2011", "2013", "2015") for code in target_codes}
        by_key = {(row["Source.Wave"], row["Variable.Name"].lower()): row for row in targets}
        self.assertEqual(set(by_key), expected)
        for (wave, code), row in by_key.items():
            concept = ("knee_height" if code == "qk002" else
                       "systolic_bp" if code in {"qa003", "qa007", "qa011"} else
                       "diastolic_bp" if code in {"qa004", "qa008", "qa012"} else "pulse_rate")
            self.assertEqual(row["Concept.ID.Candidates"], concept, (wave, code))

    def test_reviewed_objective_fields_do_not_revert_to_automated_discovery(self):
        with (ROOT / "audit/objective_measurement_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            crosswalk = list(csv.DictReader(handle))
        fields = {(row["wave"], code.strip().lower()) for row in crosswalk for code in row["variables"].split(";") if code.strip()}
        p_rows = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        relevant = [row for row in p_rows
                    if (row.get("Source.Wave"), row.get("Variable.Name", "").lower()) in fields
                    and row.get("category") in {"blood pressure", "anthropometric", "physical function"}]
        self.assertTrue(relevant)
        for row in relevant:
            self.assertFalse(row.get("Candidate.Status", "").lower().startswith("automated discovery"), row)
            self.assertFalse(row.get("Candidate.Status", "").lower().startswith("automated keyword discovery"), row)
            self.assertNotEqual(row.get("Review.Flag"), "role/category is a search aid, not analytic inclusion", row)

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
        self.assertIn("2021–2023常规调查尚未在该目录列为可下载发布包", html)
        self.assertIn("CHARLS公开数据目录仍列出2020年全国追访作为最新可申请发布", html)
        self.assertIn("regular_wave5_2021_2023_release_status_2026-10-24.md", html)
        self.assertIn("变量名不同也不能单独证明测量不存在", html)
        self.assertIn("官方Codebook字段标签", html)
        self.assertIn("source_field_labels", app)
        self.assertIn("objective_measurements_v1.json?v=4", app)


if __name__ == "__main__":
    unittest.main()
