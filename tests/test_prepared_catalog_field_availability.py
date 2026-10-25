import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.audit_prepared_catalog_field_availability import inspect_catalog, missing_reason


class PreparedCatalogAvailabilityTests(unittest.TestCase):
    def test_known_structural_absences_are_described_without_inference(self):
        self.assertIn("communityID", missing_reason("2011", "community"))
        self.assertIn("roster remains separate", missing_reason("2013", "Child"))
        self.assertIn("independent 2015 Blood Data", missing_reason("2015", "Blood_Data_2015_Independent_Release"))
        self.assertIn("inspect module merge", missing_reason("2018", "Health_Status"))

    def test_header_only_comparison_counts_names_and_2013_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            data.mkdir()
            for wave in ("2011", "2013", "2015", "2018", "2020"):
                columns = {"ID": [1, 2]}
                if wave == "2013":
                    columns["age"] = [50, 60]
                    columns["indv_weight"] = [1.0, 1.0]
                pd.DataFrame(columns).to_stata(data / f"CHARLS_wave{wave}_person_analytic.dta", write_index=False)

            catalog = root / "catalog.csv"
            pd.DataFrame([
                {"Source.Wave": "2011", "Data.File.Name": "community", "Variable.Name": "cc001", "epcf": "e"},
                {"Source.Wave": "2013", "Data.File.Name": "Demographic_Background", "Variable.Name": "age", "epcf": "p"},
                {"Source.Wave": "2013", "Data.File.Name": "Child", "Variable.Name": "child_id", "epcf": "c"},
            ]).to_csv(catalog, index=False, encoding="utf-8-sig")

            summaries, absent, modules, report = inspect_catalog(catalog, data)
            lookup = {(r["wave"], r["role"]): r for r in summaries}
            self.assertEqual(lookup[("2013", "P")]["source_codes_present_by_name"], 1)
            self.assertEqual(lookup[("2011", "E")]["source_codes_absent_by_name"], 1)
            self.assertEqual(report["waves"]["2013"]["required_2013_sample_flags_missing"],
                             ["crosssection", "longitudinal"])
            self.assertEqual(len(absent), 2)
            self.assertIn("row counts read", lookup[("2013", "P")]["status"])
            module_lookup = {(r["wave"], r["role"], r["module"]): r for r in modules}
            self.assertEqual(module_lookup[("2013", "P", "Demographic_Background")]
                             ["source_codes_present_by_name"], 1)
            self.assertEqual(module_lookup[("2013", "C", "Child")]
                             ["source_codes_absent_by_name"], 1)
            self.assertIn("header-name screening only", module_lookup[("2013", "C", "Child")]["status"])


if __name__ == "__main__":
    unittest.main()
