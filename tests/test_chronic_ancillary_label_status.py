import importlib.util
import csv
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "apply_chronic_ancillary_label_status",
    ROOT / "scripts/apply_chronic_ancillary_label_status.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ChronicAncillaryLabelStatusTests(unittest.TestCase):
    def test_only_rows_with_explicit_reviewed_response_labels_advance(self):
        mapping = pd.read_csv(ROOT / "audit/chronic_disease_ancillary_variable_mapping_v1.csv", dtype=str).fillna("")
        updated, count = MODULE.apply_status(mapping)
        self.assertEqual(count, 83)
        changed = updated.mapping_status.eq(MODULE.REVIEWED_STATUS)
        self.assertEqual(int(changed.sum()), 83)
        self.assertTrue(updated.loc[changed, "value_labels"].ne("").all())
        self.assertTrue(updated.loc[changed, "value_label_status"].str.contains("frequencies excluded|frequencies omitted", case=False).all())
        self.assertTrue(updated.loc[changed, "mapping_status"].str.contains("routed denominator and analysis eligibility require QA").all())
        self.assertEqual(int(updated.mapping_status.str.contains("DO NOT ANALYZE").sum()), int(mapping.mapping_status.str.contains("DO NOT ANALYZE").sum()))

    def test_status_application_is_idempotent(self):
        mapping = pd.read_csv(ROOT / "audit/chronic_disease_ancillary_variable_mapping_v1.csv", dtype=str).fillna("")
        once, _ = MODULE.apply_status(mapping)
        twice, _ = MODULE.apply_status(once)
        self.assertTrue(once.equals(twice))

    def test_reported_diagnosis_age_c_metadata_is_source_reviewed(self):
        with (ROOT / "audit/chronic_disease_ancillary_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            mapping = list(csv.DictReader(f))
        targets = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in mapping
                   if r["construct"] == "reported diagnosis/knowledge time" and r["subtype"] == "age"}
        self.assertEqual(len(targets), 56)
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        matched = [r for r in catalog if r["epcf"].lower() == "c" and
                   (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in targets]
        self.assertEqual(len(matched), 56)
        self.assertTrue(all(r["category"] == "source-reviewed chronic-disease timing metadata" for r in matched))
        self.assertTrue(all(r["subcategory"] == "reported diagnosis/knowledge age metadata" for r in matched))
        self.assertTrue(all("not biological onset or a default adjustment" in r["Candidate.Status"] for r in matched))
        self.assertTrue(all(r["Unit"] == "age in years" for r in matched))


if __name__ == "__main__":
    unittest.main()
