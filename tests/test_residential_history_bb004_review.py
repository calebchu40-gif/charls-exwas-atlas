import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResidentialHistoryBB004ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_wave = {r["Source.Wave"]: r for r in rows if r["Variable.Name"].lower() == "bb004"}

    def test_2011_conflict_withholds_labels_and_locks_field(self):
        row = self.by_wave["2011"]
        self.assertEqual(row["Value.Labels"], "")
        self.assertIn("identity conflict", row["Value.Label.Review"])
        self.assertIn("HOLD FOR SOURCE VALIDATION", row["Review.Flag"])
        self.assertIn("same county/city", row["Harmonization.Status"])
        self.assertNotIn("DO NOT ANALYZE", row["Harmonization.Status"])

    def test_later_wave_labels_are_wave_specific_and_routed(self):
        for wave in ("2013", "2015", "2018"):
            row = self.by_wave[wave]
            self.assertEqual(row["Value.Labels"], "1=Yes; 2=No")
            self.assertIn("conditional", row["Harmonization.Status"])
            self.assertIn("not current neighborhood quality", row["Harmonization.Status"])
            self.assertNotIn("Freq.", row["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
