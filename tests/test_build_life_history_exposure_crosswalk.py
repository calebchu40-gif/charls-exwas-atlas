import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_life_history_exposure_crosswalk as builder  # noqa: E402


class LifeHistoryCrosswalkTests(unittest.TestCase):
    def test_codebook_codes_with_spacing_are_normalized(self):
        sample = """\f--- PAGE 2 ---
CHARLSCodeBook 1 RESIDENCE
• t003c_1_s11 : Why Moved out 1st Residence: Intellectual Youth
• t004_1_: Rural or Urban
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "codebook.txt"
            path.write_text(sample, encoding="utf-8")
            with patch.object(builder, "CODEBOOK", path):
                fields = builder.read_codebook_fields()
        self.assertEqual(fields[("RESIDENCE", "t003c_1_s11")], "Why Moved out 1st Residence: Intellectual Youth")
        self.assertIn(("RESIDENCE", "t004_1_"), fields)

    def test_official_mapping_counts_and_repeated_episode_grouping(self):
        rows, groups = builder.build()
        self.assertEqual((len(groups), len(rows)), (18, 471))
        self.assertEqual({role: sum(row["role"] == role for row in rows) for role in ("e", "p")}, {"e": 466, "p": 5})
        by_concept = {}
        for row in rows:
            by_concept.setdefault(row["concept_id"], []).append(row)
        self.assertEqual(len(by_concept["life_history_residential_transition_reasons"]), 325)
        self.assertEqual(len(by_concept["life_history_residential_urbanicity"]), 25)
        self.assertEqual(len(by_concept["life_history_parental_divorce"]), 3)
        self.assertEqual(len({(row["module"], row["code"]) for row in rows}), len(rows))
        self.assertFalse(any("OBS:" in " ".join(row.values()) for row in rows))


if __name__ == "__main__":
    unittest.main()
