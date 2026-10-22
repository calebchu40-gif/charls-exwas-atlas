# 居民养老保险转入来源：2013补录与2015保留待核

更新：2026-10-22。将2013 `fn064_w2_2_`接入既有`resident_pension_transfer_source`候选概念。官方2013问卷显示，FN063_w2/FN064_w2仅在受访者参加居民养老计划（对应计划路由）时询问；FN063_w2=No跳过FN064_w2，FN063_w2=Yes才询问养老保险从何种方案转入。问卷与Codebook的分类一致：1=农村养老保险，2=企业职工基本养老保险，3=其他。值标签只抄答案类别，不用代码本频数；Other附带自由文本不另作为标准类别。

2015同码`fn064_w2_2_`暂不接入此跨波概念。2015问卷摘录确认FN063_w2=Yes后进入FN064_w2，但页面提取文本未完整显示来源选项；2015 Codebook当前摘录只列出1=Firm Pension，不能据此断定这是完整类别集或与2013代码完全同义。保留E类待审状态，待核对该发行版完整问卷/数据字典后再决定是否能与现有概念合并；不得把未列值推断为无。

来源：`sources_official/CHARLS_2013_Questionnaire_extracted.txt`（约第7604–7619行）、`sources_official/CHARLS_2013_Codebook_extracted.txt`（fn063/fn064标签）、`sources_official/CHARLS_2015_Questionnaire_extracted.txt`（约第6588–6605行）、`sources_official/CHARLS_2015_Codebook_extracted.txt`（fn064标签）。映射写入`audit/pension_supplementary_plan_mapping_review_2026-10-17.md`所用构建脚本及`audit/pension_supplementary_crosswalk_v1.csv`；本审计未读取个体记录或代码本频数。
