import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site-prototype" / "dist" / "index.html"
sys.path.insert(0, str(ROOT / "scripts"))

from audit_2011_community_subcommunity_linkage import summarize_linkage  # noqa: E402


class CommunitySubcommunityLinkageTests(unittest.TestCase):
    def test_public_community_catalog_explains_the_subcommunity_link_hold(self):
        page = INDEX.read_text(encoding="utf-8")
        start = page.index('id="communityExposures"')
        section = page[start:page.index("</section>", start)]
        self.assertIn("sub_commuID", section)
        self.assertIn("communityID", section)
        self.assertIn("通常用于连接社区、家庭和个人模块", section)
        self.assertIn("不把communityID当作唯一键", section)
        self.assertIn("随意去重", section)
        self.assertIn("CHARLS_nationalbaseline_users_guide.pdf", section)

    def test_duplicate_community_id_blocks_merge_even_with_full_person_key_coverage(self):
        community = pd.DataFrame({
            "communityID": ["a", "a", "b"],
            "sub_commuID": ["1", "2", pd.NA],
            "ja001": [1, 2, 1],
            "ja002": [2011, 2010, 2000],
        })
        persons = pd.DataFrame({"communityID": ["a", "b", "b"]})
        result = summarize_linkage(community, persons, ["ja001", "ja002", "missing"])
        self.assertEqual(result["linkage_status"], "blocked_duplicate_community_key")
        self.assertEqual(result["respondent_community_key_match_rate"], 1.0)
        self.assertEqual(result["community_duplicate_key_groups"], 1)
        self.assertEqual(result["distinct_subcommunity_keys_within_duplicate_groups"], 2)
        self.assertEqual(result["candidate_codes_found_in_community_file"], 2)
        self.assertEqual(result["candidate_fields_varying_within_duplicate_community_keys"], 2)
        self.assertFalse(result["merge_authorized_by_this_audit"])

    def test_unique_community_keys_only_pass_key_structure_not_full_analysis_gates(self):
        community = pd.DataFrame({
            "communityID": ["a", "b"],
            "sub_commuID": [pd.NA, pd.NA],
            "ja001": [1, 2],
        })
        persons = pd.DataFrame({"communityID": ["a", "b"]})
        result = summarize_linkage(community, persons, ["ja001"])
        self.assertEqual(result["linkage_status"], "key_structure_pass_needs_source_review")
        self.assertEqual(result["respondent_community_key_match_rate"], 1.0)
        self.assertIn("source identity", result["interpretation"])
        self.assertFalse(result["merge_authorized_by_this_audit"])

    def test_missing_keys_and_unmatched_person_keys_are_reported_without_values(self):
        community = pd.DataFrame({
            "communityID": ["a", pd.NA],
            "sub_commuID": [pd.NA, pd.NA],
            "ja001": [1, 2],
        })
        persons = pd.DataFrame({"communityID": ["a", "unmatched", pd.NA]})
        result = summarize_linkage(community, persons, ["ja001", "ja002"])
        self.assertEqual(result["community_key_missing_rows"], 1)
        self.assertEqual(result["respondent_community_key_missing_rows"], 1)
        self.assertEqual(result["respondent_unique_community_key_count"], 2)
        self.assertEqual(result["respondent_community_key_match_rate"], 0.5)
        self.assertEqual(result["candidate_codes_missing_from_community_file"], 1)
        serialized = str(result)
        self.assertNotIn("unmatched", serialized)


if __name__ == "__main__":
    unittest.main()
