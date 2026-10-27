"""Synthetic tests for the generic ExWAS scan engine.

Every fixture here is fabricated. No CHARLS microdata is read, and the tests
only assert that the engine recovers *known* effects from a fake frame and
fail-closes on malformed registries/designs.

The engine depends on the pinned survey stack (``svy`` / ``polars`` / ``numpy``).
The default CI unit-test job installs only ``requirements-test.txt``, so this
module skips cleanly there and runs for real in the ``synthetic-survey-engine``
job, which installs ``requirements-survey-audit.txt``.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SURVEY_STACK = all(importlib.util.find_spec(name) for name in ("numpy", "polars", "svy"))
SKIP_REASON = "survey analysis stack (svy/polars/numpy) is not installed in this job"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

if SURVEY_STACK:
    import exwas_engine as engine  # noqa: E402
    import run_exwas_scan as cli  # noqa: E402


def _rows(rows, exposure, phenotype, model_id="M0"):
    return [r for r in rows
            if r["exposure_concept_id"] == exposure
            and r["phenotype_concept_id"] == phenotype
            and r["model_id"] == model_id]


@unittest.skipUnless(SURVEY_STACK, SKIP_REASON)
class RegistryValidationTests(unittest.TestCase):
    def _write(self, content: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        handle.write(content)
        handle.close()
        return Path(handle.name)

    def test_missing_required_field_is_rejected(self):
        path = self._write("concept_id,role,wave,variable\nx,E,SYNTH,a\n")
        with self.assertRaises(engine.RegistryError):
            engine.load_registry(path)

    def test_unknown_role_is_rejected(self):
        path = self._write("concept_id,role,wave,variable,kind\nx,Z,SYNTH,a,continuous\n")
        with self.assertRaises(engine.RegistryError):
            engine.load_registry(path)

    def test_categorical_reference_must_be_a_level(self):
        path = self._write(
            "concept_id,role,wave,variable,kind,levels,reference\n"
            "x,E,SYNTH,a,categorical,1|2,9\n")
        with self.assertRaises(engine.RegistryError):
            engine.load_registry(path)

    def test_valid_registry_roundtrips(self):
        path = self._write(
            "concept_id,role,wave,variable,kind,label\n"
            "e1,E,SYNTH,exposure_cont,continuous,Exposure\n"
            "p1,P,SYNTH,pheno_cont,continuous,Phenotype\n")
        specs = engine.load_registry(path)
        self.assertEqual(len(specs), 2)
        self.assertEqual({s.role for s in specs}, {"E", "P"})


@unittest.skipUnless(SURVEY_STACK, SKIP_REASON)
class DesignValidationTests(unittest.TestCase):
    def test_design_requires_weight_and_psu(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump({"weight": "w"}, handle)
            path = Path(handle.name)
        with self.assertRaises(engine.DesignError):
            engine.load_design(path)

    def test_missing_frame_column_is_rejected(self):
        frame = cli.synthetic_frame(n=50)
        design = cli.synthetic_design()
        broken = frame.drop("psu")
        with self.assertRaises(engine.DesignError):
            engine.prepare_frame(broken, design, cli.synthetic_registry())


@unittest.skipUnless(SURVEY_STACK, SKIP_REASON)
class SyntheticScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = cli.synthetic_frame(n=6000, seed=11)
        cls.registry = cli.synthetic_registry()
        cls.design = cli.synthetic_design()
        cls.rows = engine.scan(cls.frame, cls.registry, cls.design, wave="SYNTH", models=["M0"])

    def test_continuous_exposure_effect_is_recovered(self):
        row = _rows(self.rows, "synth_cont", "synth_pheno_cont")[0]
        self.assertEqual(row["fit_status"], "success")
        self.assertAlmostEqual(float(row["estimate"]), 0.60, delta=0.10)

    def test_binary_exposure_effect_is_recovered(self):
        row = _rows(self.rows, "synth_bin", "synth_pheno_cont")[0]
        self.assertAlmostEqual(float(row["estimate"]), 1.20, delta=0.18)

    def test_binomial_phenotype_reports_odds_ratio(self):
        row = _rows(self.rows, "synth_bin", "synth_pheno_bin")[0]
        self.assertEqual(row["estimate_type"], "odds_ratio")
        self.assertGreater(float(row["estimate"]), 1.2)
        self.assertLess(float(row["estimate"]), 2.3)

    def test_categorical_exposure_yields_one_row_per_non_reference_level(self):
        rows = _rows(self.rows, "synth_site", "synth_pheno_cont")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["fit_status"] == "success" for row in rows))

    def test_family_assignment_covers_every_row(self):
        family = self.rows[0]["multiple_testing_family"]
        self.assertTrue(family.endswith(f"K={len(self.rows)}"))
        self.assertTrue(all(row["multiple_testing_family"] == family for row in self.rows))
        self.assertTrue(all(row["q_value_by"] != "" for row in self.rows))
        self.assertTrue(all(row["p_bonferroni"] != "" for row in self.rows))

    def test_engine_never_pairs_a_concept_with_itself(self):
        pairs = engine.enumerate_pairs(self.registry, "SYNTH")
        self.assertTrue(all(e.concept_id != p.concept_id for e, p in pairs))
        self.assertEqual(len(pairs), 3 * 2)


@unittest.skipUnless(SURVEY_STACK, SKIP_REASON)
class FailClosedTests(unittest.TestCase):
    def test_empty_domain_is_reported_not_fitted(self):
        frame = cli.synthetic_frame(n=400)
        design = cli.synthetic_design()
        design.age_min = 999
        rows = engine.scan(frame, cli.synthetic_registry(), design, wave="SYNTH", models=["M0"])
        self.assertTrue(rows)
        self.assertTrue(all(row["fit_status"] == "no_eligible_records" for row in rows))
        self.assertTrue(all(row["estimate"] == "" for row in rows))

    def test_z_transform_scales_the_exposure(self):
        frame = cli.synthetic_frame(n=4000, seed=3)
        design = cli.synthetic_design()
        registry = [
            engine.VariableSpec("z_cont", "E", "z exposure", "SYNTH", "exposure_cont",
                                "continuous", transform="z"),
            engine.VariableSpec("p", "P", "pheno", "SYNTH", "pheno_cont", "continuous"),
        ]
        rows = engine.scan(frame, registry, design, wave="SYNTH", models=["M0"])
        self.assertEqual(rows[0]["exposure_scale"], "weighted_z")
        # outcome is unscaled in the synthetic design, exposure sd ~1 -> ~0.6
        self.assertAlmostEqual(float(rows[0]["estimate"]), 0.60, delta=0.12)


if __name__ == "__main__":
    unittest.main()
