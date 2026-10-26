import unittest

from scripts.validate_prepared_wave_tables import missing_required_sample_flags, source_record_status


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

    def test_source_manifest_absence_is_explicit(self):
        self.assertEqual(source_record_status("2015", None), "source_record_missing")

    def test_wave1_requires_separate_official_release_records(self):
        digest = "a" * 64
        archive = {"filename": "wave1.zip", "bytes": 100, "sha256": digest}
        record = {"source_archive": archive, "source_inputs": {"all_data_archive": archive}}
        self.assertEqual(source_record_status("2011", record), "missing_psu_source_record")

    def test_local_hashes_do_not_claim_official_source_identity(self):
        digest = "b" * 64
        archive = {"filename": "wave3.zip", "bytes": 100, "sha256": digest}
        record = {"source_archive": archive, "source_inputs": {"all_data_archive": archive}}
        self.assertEqual(
            source_record_status("2015", record),
            "local_source_hashes_recorded_official_identity_unverified",
        )

    def test_invalid_hash_is_not_counted_as_source_evidence(self):
        archive = {"filename": "wave3.zip", "bytes": 100, "sha256": "not-a-hash"}
        record = {"source_archive": archive, "source_inputs": {"all_data_archive": archive}}
        self.assertEqual(source_record_status("2015", record), "invalid_all_data_archive_source_record")


if __name__ == "__main__":
    unittest.main()
