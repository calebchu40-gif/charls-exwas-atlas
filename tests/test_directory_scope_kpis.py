import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DirectoryScopeKpiTests(unittest.TestCase):
    def test_homepage_reports_exposure_and_phenotype_counts_separately(self):
        scope = json.loads((ROOT / "audit/directory_scope_counts_v1.json").read_text(encoding="utf-8"))
        html = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<p class="stats-note">五轮常规主调查去重后共有'), 1)
        match = re.search(r'<div class="stats"[^>]*>(.*?)</div>\s*<p class="stats-note">(.*?)</p>', html, re.S)
        self.assertIsNotNone(match)
        cards = re.findall(r'<div class="stat"><b>([^<]+)</b><span>([^<]+)</span></div>', match.group(1))
        self.assertEqual(
            cards,
            [
                (f"{scope['exposure_concept_ids_including_dual']:,}", "暴露候选概念"),
                (f"{scope['phenotype_concept_ids_including_dual']:,}", "表型候选概念"),
                ("5", "调查波次：2011–2020"),
                ("0", "正式关联模型"),
            ],
        )
        unique = scope["candidate_concept_ids"]
        dual = scope["exposure_concept_ids_including_dual"] + scope["phenotype_concept_ids_including_dual"] - unique
        self.assertIn(f"{unique:,} 个 E/P 候选概念", match.group(2))
        self.assertIn(f"{dual} 个同时承担暴露与表型角色", match.group(2))
        self.assertIn(f"{scope['wave_field_mapping_rows']:,} 条概念—源字段映射", match.group(2))
        self.assertIn("不是样本量或关联结果", match.group(2))
        self.assertIn("2014生命历程特殊调查单独展示", match.group(2))
        self.assertIn("2014 生命历程回顾性调查", html)
        self.assertIn("481条概念—字段映射", html)
        self.assertIn("不计入上述五波统计", match.group(2))
        self.assertIn("30个大型社区曾按地理子区拆分抽样", html)
        self.assertIn("communityID 仅是 PSU 候选", html)
        self.assertIn("可能包含45岁以下个体", html)
        self.assertIn("该调查没有权重", html)
        self.assertIn("CHARLS官方数据页与文件", html)

    def test_readme_snapshot_matches_generated_catalog_and_pair_index(self):
        scope = json.loads((ROOT / "audit/directory_scope_counts_v1.json").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        pair_index = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))
        catalogs = {
            role: json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
            for role in "epc"
        }
        self.assertIn(f"E={len(catalogs['e']):,}、P={len(catalogs['p']):,}、C={len(catalogs['c']):,}", readme)
        self.assertIn(f"{scope['candidate_concept_ids']:,} 个候选概念", readme)
        self.assertIn(f"{scope['exposure_concept_ids_including_dual']:,}", readme)
        self.assertIn(f"{scope['phenotype_concept_ids_including_dual']:,}", readme)
        self.assertIn(f"{scope['wave_field_mapping_rows']:,} 条概念—来源映射", readme)
        for wave, details in pair_index["waves"].items():
            self.assertIn(f"{details['candidate_pair_count']:,}", readme)


if __name__ == "__main__":
    unittest.main()
