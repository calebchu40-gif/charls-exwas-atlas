import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS


class FinalizationBalanceGateTests(unittest.TestCase):
    def test_finalize_only_rebuilds_symptoms_labels_and_balance_gate_before_catalog(self):
        charls_builds = [i for i, name in enumerate(FINALIZATION_PIPELINE_SCRIPTS) if name == "build_charls_atlas_catalog.py"]
        symptom = FINALIZATION_PIPELINE_SCRIPTS.index("build_health_symptom_crosswalk.py")
        labels = FINALIZATION_PIPELINE_SCRIPTS.index("enrich_outcome_value_labels.py")
        gate = FINALIZATION_PIPELINE_SCRIPTS.index("build_balance_assessment_crosswalk.py")
        self.assertGreaterEqual(len(charls_builds), 2)
        self.assertLess(charls_builds[0], symptom)
        self.assertLess(symptom, labels)
        self.assertLess(labels, gate)
        self.assertLess(gate, charls_builds[1])


if __name__ == "__main__":
    unittest.main()
