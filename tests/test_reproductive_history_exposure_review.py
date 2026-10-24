import importlib.util
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apply_reproductive_history_exposure_review.py"
SPEC = importlib.util.spec_from_file_location("reproductive_history_review", SCRIPT)
REVIEW = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(REVIEW)


class ReproductiveHistoryExposureReviewTests(unittest.TestCase):
    def test_crosswalk_has_eight_exact_wave_field_mappings(self):
        mapping = REVIEW.load_mapping()
        self.assertEqual(len(mapping), 8)
        self.assertEqual(set(mapping.concept_id), {"age_at_menarche", "age_at_menopause"})
        self.assertEqual(set(mapping.wave), {"2011", "2013", "2015", "2018"})
        self.assertEqual(set(mapping.code.str.lower()), {"da026_2", "da028_2"})


    def test_transform_promotes_only_age_components_and_preserves_route_caveats(self):
        mapping = REVIEW.load_mapping()
        records = []
        for row in mapping.to_dict(orient="records"):
            records.append({
                "Source.Wave": row["wave"], "Variable.Name": row["code"], "epcf": "c",
                "Concept.ID.Candidates": "", "Concept.Label.Candidates": "",
            })
        updated = REVIEW.transform_records(records, mapping)
        self.assertEqual(len(updated), 8)
        self.assertTrue(all(row["epcf"] == "e" for row in updated))
        self.assertTrue(all(row["Concept.Unit.Candidates"] == "years" for row in updated))
        self.assertTrue(all("*_1 calendar-year component remains separate" in row["Harmonization.Status"] for row in updated))
        self.assertTrue(all("special responses" in row["Review.Flag"] for row in updated if row["Variable.Name"] == "da026_2"))
        self.assertTrue(all("DA027" in row["Review.Flag"] or row["Variable.Name"] == "da026_2" for row in updated))


    def test_mapping_does_not_promote_prior_wave_zda_history_fields(self):
        mapping = REVIEW.load_mapping()
        self.assertFalse(mapping.code.str.lower().str.startswith("zda").any())
        self.assertTrue(mapping.caveat.str.contains("cross-wave equivalence is established|cross-wave equivalence not approved", case=False, regex=True).all())
