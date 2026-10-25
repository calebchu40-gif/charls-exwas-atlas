import importlib.util
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_pension_codebook_value_labels",
    ROOT / "scripts/build_pension_codebook_value_labels.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PensionCodebookStatusPropagationTests(unittest.TestCase):
    def test_all_field_location_dispositions_propagate_even_without_categories(self):
        fields = pd.read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv", dtype=str).fillna("")
        reviewed = pd.read_csv(ROOT / "audit/pension_codebook_value_labels_v1.csv", dtype=str).fillna("")
        result = MODULE.apply_codebook_review_status(fields, reviewed)
        self.assertEqual(len(result), 1159)
        self.assertEqual(int(result.value_label_status.eq("official codebook field located; continuous/count or no categorical labels").sum()), 1050)
        self.assertEqual(int(result.value_label_status.str.contains("questionnaire/Codebook field and item identity reviewed|DO NOT ANALYZE", regex=True).sum()), 36)
        self.assertEqual(int(result.value_label_status.eq("official response label not located or title match insufficient").sum()), 0)
        self.assertEqual(int(result.value_label_status.eq("official codebook response labels reviewed; frequencies omitted").sum()), 19)
        self.assertEqual(int(result.value_label_status.str.contains("checkbox slot", case=False).sum()), 17)
        self.assertTrue(result.loc[result.value_labels.eq("") & result.value_label_status.str.startswith("official codebook field located;"), "value_label_source"].ne("").all())

    def test_2011_pdf_space_rendered_subfields_are_exactly_located(self):
        reviewed = pd.read_csv(ROOT / "audit/pension_codebook_value_labels_v1.csv", dtype=str).fillna("")
        fields = reviewed[reviewed.wave.eq("2011") & reviewed.code.isin(["fn003_1", "fn003_2", "fn061_2", "fn036_2"])]
        self.assertEqual(len(fields), 4)
        self.assertTrue(fields.value_labels.eq("").all())
        self.assertTrue(fields.value_label_status.str.startswith("official codebook field located;").all())
        self.assertTrue(fields.value_label_source.str.contains("CHARLS_2011_Codebook_extracted.txt").all())

    def test_status_propagation_preserves_mapping_status_caveat_and_label_text(self):
        fields = pd.DataFrame([{
            "wave": "2011", "code": "fn001", "value_labels": "",
            "value_label_status": "official response label not located; review required",
            "value_label_source": "", "mapping_status": "route still pending", "caveat": "Keep route.",
        }])
        reviewed = pd.DataFrame([{
            "wave": "2011", "code": "fn001", "value_labels": "",
            "value_label_status": "official codebook field located; continuous/count or no categorical labels",
            "value_label_source": "sources_official/CHARLS_2011_Codebook_extracted.txt",
        }])
        result = MODULE.apply_codebook_review_status(fields, reviewed)
        self.assertEqual(result.loc[0, "value_label_status"], reviewed.loc[0, "value_label_status"])
        self.assertEqual(result.loc[0, "value_label_source"], reviewed.loc[0, "value_label_source"])
        self.assertEqual(result.loc[0, "mapping_status"], "route still pending")
        self.assertEqual(result.loc[0, "caveat"], "Keep route.")
        self.assertEqual(result.loc[0, "value_labels"], "")


if __name__ == "__main__":
    unittest.main()
