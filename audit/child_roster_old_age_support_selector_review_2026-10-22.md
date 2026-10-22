# 子女名单选择字段：老年经济支持模块元数据分流

更新：2026-10-22。2015和2018官方问卷均把FN098置于“老年经济来源依赖子女”的FN097回答之后。2015问卷说明FN098为“Which child(ren)? (choose all that apply)”，2018问卷明确为预载子女列表（1–N）。Codebook进一步将变量标签与第1至第25名子女记录相连。2013数据目录也以`fn098_w2s1`等字段列为`Which Child XchildName[n]`。

这些槽位标识被受访者选择的具体子女/家庭成员记录，数据意义是 roster linkage，而非在样本之间同尺度的子女支持暴露值。已把2013、2015全部`fn098_w2s*`及2018 `fn098_w2_s*`槽位（含99“不知道”选项）从自动E候选转列C类元数据，排除关联矩阵并禁止公开链接身份或回答值。FN097“将来依靠什么养老”本身仍是独立社会支持/保障候选，未因此移除。

若后续在获准的个人数据环境中定义“依赖子女数”等汇总指标，须先核实多选槽的存储结构、子女名单波次变化、未问/缺失/拒答编码、是否可多选和调查权重适用性；不得从目前目录标签直接生成分析变量。

证据：`sources_official/CHARLS_2015_Questionnaire_extracted.txt`第6932–6939行及FN098题干；`sources_official/CHARLS_2018_Questionnaire_extracted.txt`第8636–8649行；`sources_official/CHARLS_2018_Codebook_extracted.txt`第65953行起；字段名见`audit/raw_variable_catalog_v1.csv`。实施规则见`audit/catalog_role_override_review_v1.csv`（`child_roster_link_selector`）和` scripts/apply_catalog_role_overrides.py`。仅审计公开问卷和字段目录，未读取个体记录。
