import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResidentialHistoryMobilityDurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.rows = {(r["Variable.Name"].lower(), r["Source.Wave"]): r for r in rows}

    def test_all_branch_fields_are_present_in_both_waves(self):
        names = ("bb007", "bb008_1", "bb008_2", "bb009", "bb010_1", "bb010_2")
        for wave in ("2011", "2013"):
            for name in names:
                self.assertIn((name, wave), self.rows)

    def test_yes_no_gates_keep_labels_and_branch_routes(self):
        for wave in ("2011", "2013"):
            self.assertEqual(self.rows[("bb007", wave)]["Value.Labels"], "1=Yes; 2=No")
            self.assertEqual(self.rows[("bb009", wave)]["Value.Labels"], "1=Yes; 2=No")
            self.assertIn("alternate", self.rows[("bb009", wave)]["Harmonization.Status"].lower())
            self.assertIn("BB008", self.rows[("bb007", wave)]["Harmonization.Status"])
            self.assertIn("BB010", self.rows[("bb009", wave)]["Harmonization.Status"])

    def test_duration_components_are_not_given_fabricated_categories(self):
        for wave in ("2011", "2013"):
            for name in ("bb008_1", "bb008_2", "bb010_1", "bb010_2"):
                row = self.rows[(name, wave)]
                self.assertEqual(row["Value.Labels"], "")
                self.assertIn("do not treat routed absence as zero", row["Harmonization.Status"])

    def test_2011_codebook_wording_difference_is_retained(self):
        note = self.rows[("bb007", "2011")]["Harmonization.Status"]
        self.assertIn("Codebook says ‘present county/city’", note)
        self.assertIn("permanent county/city/district", note)


if __name__ == "__main__":
    unittest.main()
