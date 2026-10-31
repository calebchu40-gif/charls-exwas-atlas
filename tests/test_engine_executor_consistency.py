"""Consistency between the generic engine and the frozen scale-up executor.

The K=150/K=90 executor (``run_2011_household_environment_scaleup.py``) accepts
only a frozen configuration that names the weight, PSU, strata, with-replacement
flag, variance method *and* its limitation. The generic engine must be able to
express the same design facts, and its per-row design note must never describe
an approximation as if it were a full design-based variance.

These tests read the public configuration template only; they never touch
participant data.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

SURVEY_STACK = all(importlib.util.find_spec(name) for name in ("numpy", "polars", "svy"))
SKIP_REASON = "survey analysis stack (svy/polars/numpy) is not installed in this job"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

if SURVEY_STACK:
    import exwas_engine as engine  # noqa: E402

TEMPLATE = ROOT / "audit" / "templates" / "wave1_household_environment_scaleup_model_config.template.json"


@unittest.skipUnless(SURVEY_STACK, SKIP_REASON)
@unittest.skipUnless(TEMPLATE.is_file(), "scale-up configuration template is not present")
class ExecutorTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_design_block_has_the_required_keys(self):
        design = self.template["design"]
        for key in ("weight_field", "psu_field", "stratum_fields", "replicate_weight_fields",
                    "with_replacement", "variance_method", "variance_limitations"):
            self.assertIn(key, design, f"executor template lost design.{key}")

    def test_template_starts_unfrozen(self):
        self.assertEqual(self.template["status"], "not_frozen")
        self.assertEqual(self.template["design"]["replicate_weight_fields"], [])
        self.assertIsNone(self.template["design"]["with_replacement"])

    def test_every_required_design_field_has_an_engine_counterpart(self):
        design = self.template["design"]
        self.assertTrue(hasattr(engine.DesignSpec, "__dataclass_fields__"))
        fields = engine.DesignSpec.__dataclass_fields__
        # weight / PSU / strata / with-replacement / variance limitation are expressible.
        for name in ("weight", "psu", "strata", "variance_limitations"):
            self.assertIn(name, fields)
        # The executor's replicate-weight slot has no engine counterpart by design:
        # the engine never accepts replicate weights and must fail closed instead.
        self.assertNotIn("replicate_weight_fields", fields)
        self.assertNotIn("rep_wgts", fields)


@unittest.skipUnless(SURVEY_STACK, SKIP_REASON)
class DesignNoteTests(unittest.TestCase):
    def test_unstratified_note_carries_a_limitation_label(self):
        design = engine.DesignSpec(weight="bloodweight", psu="communityID")
        note = design.note()
        self.assertIn("unstratified with-replacement Taylor approximation", note)
        self.assertIn("not full design variance", note)
        self.assertIn("limitation:", note)
        self.assertIn(engine.DEFAULT_VARIANCE_LIMITATION, note)

    def test_custom_limitation_text_is_used_verbatim(self):
        design = engine.DesignSpec(weight="bloodweight", psu="communityID",
                                   variance_limitations="county-prefix cluster candidate, not official")
        self.assertIn("limitation: county-prefix cluster candidate, not official", design.note())

    def test_stratified_note_names_the_stratum_column(self):
        design = engine.DesignSpec(weight="bloodweight", psu="communityID", strata="province")
        note = design.note()
        self.assertIn("official stratum province", note)
        self.assertNotIn("limitation:", note)

    def test_design_json_round_trips_limitations(self):
        import tempfile
        payload = {
            "weight": "bloodweight", "psu": "communityID", "strata": None,
            "variance_limitations": "county-prefix candidate; not CHARLS-endorsed",
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(payload, handle)
            path = Path(handle.name)
        design = engine.load_design(path)
        self.assertEqual(design.variance_limitations, "county-prefix candidate; not CHARLS-endorsed")
        self.assertIn("limitation: county-prefix candidate", design.note())

    def test_result_rows_carry_the_note(self):
        import run_exwas_scan as cli
        frame = cli.synthetic_frame(n=300, seed=2)
        design = engine.DesignSpec(weight="ind_weight", psu="psu", age_field="age", age_min=45,
                                   covariate_sets={"M0": []}, scale_outcome=False)
        rows = engine.scan(frame, cli.synthetic_registry(), design, wave="SYNTH", models=["M0"])
        self.assertTrue(rows)
        self.assertTrue(all("limitation:" in row["design_note"] for row in rows))


if __name__ == "__main__":
    unittest.main()
