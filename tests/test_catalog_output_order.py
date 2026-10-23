import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_charls_atlas_catalog import preserve_existing_catalog_order


class CatalogOutputOrderTests(unittest.TestCase):
    def test_existing_rows_keep_order_and_new_rows_append(self):
        fields = ["Source.Wave", "Variable.Name", "epcf", "Data.File.Name", "category", "subcategory"]
        prior = pd.DataFrame([
            ["2020", "b", "p", "health", "physical", "function"],
            ["2020", "a", "e", "health", "behavior", "other"],
        ], columns=fields)
        generated = pd.DataFrame([
            ["2020", "new", "e", "health", "behavior", "digital"],
            ["2020", "a", "e", "health", "behavior", "other"],
            ["2020", "b", "p", "health", "physical", "function"],
        ], columns=fields)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prior.csv"
            prior.to_csv(path, index=False, encoding="utf-8-sig")
            ordered = preserve_existing_catalog_order(generated, path)
        self.assertEqual(ordered["Variable.Name"].tolist(), ["b", "a", "new"])

    def test_reclassified_row_uses_wave_code_role_fallback(self):
        fields = ["Source.Wave", "Variable.Name", "epcf", "Data.File.Name", "category", "subcategory"]
        prior = pd.DataFrame([["2020", "dc030", "c", "health", "keyword", "pending"]], columns=fields)
        generated = pd.DataFrame([["2020", "dc030", "c", "health", "measurement", "interview language"]], columns=fields)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prior.csv"
            prior.to_csv(path, index=False, encoding="utf-8-sig")
            ordered = preserve_existing_catalog_order(generated, path)
        self.assertEqual(ordered.iloc[0]["category"], "measurement")

    def test_recreated_metadata_rows_return_to_their_prior_position(self):
        fields = ["Source.Wave", "Variable.Name", "epcf", "Data.File.Name", "category", "subcategory"]
        prior = pd.DataFrame([
            ["2020", "a", "e", "health", "behavior", "other"],
            ["2011", "old-meta", "c", "health", "measurement", "history"],
            ["2020", "b", "p", "health", "physical", "function"],
        ], columns=fields)
        generated = pd.DataFrame([
            prior.iloc[0].tolist(),
            prior.iloc[2].tolist(),
            prior.iloc[1].tolist(),
        ], columns=fields)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prior.csv"
            prior.to_csv(path, index=False, encoding="utf-8-sig")
            ordered = preserve_existing_catalog_order(generated, path)
        self.assertEqual(ordered["Variable.Name"].tolist(), ["a", "old-meta", "b"])


if __name__ == "__main__":
    unittest.main()
