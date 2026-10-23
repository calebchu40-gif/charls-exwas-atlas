import unittest

from scripts.validate_prepared_wave_tables import missing_required_sample_flags


class PreparedWaveValidationTests(unittest.TestCase):
    def test_2013_requires_cross_section_and_longitudinal_flags(self):
        self.assertEqual(
            missing_required_sample_flags("2013", ["ID", "crosssection"]),
            ["longitudinal"],
        )
        self.assertEqual(
            missing_required_sample_flags("2013", ["ID", "CROSSSECTION", "Longitudinal"]),
            [],
        )

    def test_other_waves_do_not_reuse_2013_sample_flag_rule(self):
        self.assertEqual(missing_required_sample_flags("2020", ["ID"]), [])


if __name__ == "__main__":
    unittest.main()
