# 2011 FN015/FN016 与 FN065/FN066 路由身份复核更正（2026-10-22）

> 此前冲突结论已撤销。旧审计误把 `CHARLS_2011_Baseline_Questionnaire_official_extracted.txt` 当作2011问卷；官方来源清单确认该摘录实际是2013问卷。现依据正确的 `CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` 与2011 Codebook复核。

2011有两组题干相近、但调查对象不同的居民养老金转入题，必须分开编码：

- FN015/FN016面向**正在领取居民养老金者**（FN002=4）。FN015为1=Yes、2=No；FN016仅在Yes后询问转入来源。使用概念 `pension_resident_transfer_status_current_recipient` 与 `resident_pension_transfer_source_current_recipient`。不与已参保者路线合并。
- FN065/FN066面向**已参加居民养老保险者**（FN039=4）。FN065为转入状态，FN066在Yes后询问来源。该路线与2013 FN063_W2/FN064_W2调查对象及回答语义一致，分别共用 `pension_resident_transfer_status` 和 `resident_pension_transfer_source`。

2015按具体养老金计划拆分字段，暂不自动合并。所有缺失/跳过均不推断为No；“其他”文本不纳入公开目录。候选概念仅用于公开元数据探索，不代表统计关联或可分析样本。

## 依据

- `sources_official/SOURCES.md`：核定问卷摘录实际所属波次。
- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` 与 `CHARLS_2011_Codebook_extracted.txt`：核对FN015/016和FN065/066题干、路由、选项及代码字段。
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt` 与 `CHARLS_2013_Codebook_extracted.txt`：核对FN063_W2/FN064_W2及其释放字段映射。

未读取受访者微观记录。规则见 `scripts/build_pension_exposure_crosswalk.py` 与 `scripts/apply_catalog_role_overrides.py`。
