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


if __name__ == "__main__":
    unittest.main()
