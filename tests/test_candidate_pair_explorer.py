from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CandidatePairExplorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))
        with (ROOT / "audit/ep_candidate_pair_wave_coverage_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.coverage = {r["wave"]: r for r in csv.DictReader(f)}

    def test_wave_counts_match_the_metadata_pair_coverage_audit(self):
        for wave, data in self.data["waves"].items():
            self.assertEqual(data["candidate_pair_count"], int(self.coverage[wave]["distinct_concept_pairs_with_both_roles"]))

    def test_wave_role_lists_are_unique_and_self_pairs_are_removed(self):
        for wave, data in self.data["waves"].items():
            exposures = {x["concept_id"] for x in data["exposures"]}
            phenotypes = {x["concept_id"] for x in data["phenotypes"]}
            self.assertEqual(len(exposures), len(data["exposures"]))
            self.assertEqual(len(phenotypes), len(data["phenotypes"]))
            self.assertEqual(data["candidate_pair_count"], len(exposures) * len(phenotypes) - len(exposures & phenotypes))
            self.assertTrue(all("e" in x["roles"] for x in data["exposures"]))
            self.assertTrue(all("p" in x["roles"] for x in data["phenotypes"]))

    def test_payload_is_explicitly_metadata_only_and_has_no_estimates(self):
        self.assertEqual(self.data["status"], "metadata_candidate_pairs_only")
        self.assertTrue(any("not people" in note or "not eligible samples" in note for note in self.data["limitations"]))
        self.assertNotIn("association_results", self.data)
        self.assertNotIn("effect_estimates", self.data)

    def test_baseline_community_candidates_are_separate_from_same_wave_pairs(self):
        longitudinal = self.data["baseline_community_to_followup"]
        baseline_exposures = self.data["baseline_community_exposures"]
        self.assertEqual(set(longitudinal), {"2013", "2015", "2018", "2020"})
        baseline_ids = None
        for wave, entry in longitudinal.items():
            self.assertEqual(entry["baseline_wave"], "2011")
            self.assertEqual(entry["followup_wave"], wave)
            self.assertEqual(entry["linkage_status"], "metadata_candidate_only_no_records_joined")
            self.assertEqual(entry["candidate_pair_count"], entry["exposure_count"] * entry["phenotype_count"])
            ids = {item["concept_id"] for item in baseline_exposures}
            self.assertEqual(len(ids), entry["exposure_count"])
            if baseline_ids is None:
                baseline_ids = ids
            self.assertEqual(ids, baseline_ids)
            self.assertTrue(all(
                field["module"].strip().lower() == "community"
                for item in baseline_exposures for field in item["source_fields"]
            ))
            followup_ids = {item["concept_id"] for item in self.data["waves"][wave]["phenotypes"]}
            self.assertTrue(set(entry["phenotype_concept_ids"]).issubset(followup_ids))
        self.assertEqual(len(baseline_ids), 186)
        self.assertTrue(any("not matched participants" in note for note in self.data["limitations"]))

    def test_page_explains_cross_wave_linkage_limits(self):
        html = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn('id="candidatePairDesign"', html)
        self.assertIn('id="candidatePairLongitudinalNote"', html)
        self.assertIn("未连接个人迁移史", html)
        self.assertIn("会尽量追访迁居者", html)
        self.assertIn("https://charls.pku.edu.cn/en/data/Release2013.pdf", html)
        self.assertIn("https://charls.pku.edu.cn/en/data/User2018.pdf", html)
        self.assertIn("data.baseline_community_to_followup", app)

    def test_page_exposes_candidate_pair_view_without_claiming_results(self):
        html = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        app = (ROOT / "site-prototype/dist/app.js").read_text(encoding="utf-8")
        self.assertIn('id="candidatePairExplorer"', html)
        self.assertIn("目录候选组合", app)
        self.assertIn("目前没有已计算的 CHARLS 暴露—表型关联结果", html)


if __name__ == "__main__":
    unittest.main()
