import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_core_concept_coverage.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("build_core_concept_coverage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SampleFrameGateTests(unittest.TestCase):
    def test_2013_missing_official_flags_fails_closed(self):
        status, mask = MODULE.sample_frame_gate("2013", ["ID", "wave"], pd.DataFrame({"ID": [1, 2]}))
        self.assertEqual(status, "sample_flags_missing:crosssection;longitudinal")
        self.assertIsNone(mask)

    def test_2013_requires_both_flags_but_filters_by_crosssection(self):
        data = pd.DataFrame({"crosssection": [1, 0, 1], "longitudinal": [1, 1, 0]})
        status, mask = MODULE.sample_frame_gate("2013", data.columns, data)
        self.assertEqual(status, "crosssection_flag_applied")
        self.assertEqual(mask.tolist(), [True, False, True])

    def test_later_wave_requires_crosssection_flag(self):
        data = pd.DataFrame({"crosssection": [1, 0, 1]})
        status, mask = MODULE.sample_frame_gate("2020", data.columns, data)
        self.assertEqual(status, "crosssection_flag_applied")
        self.assertEqual(mask.tolist(), [True, False, True])

    def test_baseline_is_explicitly_marked_without_a_separate_flag(self):
        data = pd.DataFrame({"ID": [1, 2]})
        status, mask = MODULE.sample_frame_gate("2011", data.columns, data)
        self.assertEqual(status, "baseline_frame_flag_not_available")
        self.assertEqual(mask.tolist(), [True, True])

    def test_pair_count_is_suppressed_when_frame_gate_is_unavailable(self):
        exposure = pd.Series([True, True, False])
        phenotype = pd.Series([True, False, True])
        self.assertIsNone(MODULE.pair_availability_count(exposure, phenotype, None))

    def test_pair_count_applies_the_wave_specific_frame_mask(self):
        exposure = pd.Series([True, True, False])
        phenotype = pd.Series([True, True, True])
        frame = pd.Series([True, False, True])
        self.assertEqual(MODULE.pair_availability_count(exposure, phenotype, frame), 1)


if __name__ == "__main__":
    unittest.main()
