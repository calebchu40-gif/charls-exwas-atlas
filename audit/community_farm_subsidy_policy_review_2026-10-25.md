# 2011 CHARLS村级农业补贴政策背景候选（2026-10-25）

## 官方字段与含义

2011 Community Questionnaire Part G 的JG017–JG020记录村级农业补贴项目：JG017询问是否实施；选择No跳至JG021；选择Yes后依次记录JG018项目开始年份、JG019在2010年领取农业补贴的户数、JG020平均补贴标准（元/亩）。问卷将粮食直补、良种补贴、农机具购置补贴和农资综合补贴列为示例。官方Codebook确认四个字段均存在；JG017官方类别为1=Yes、2=No。网页仅展示类别，不复制频数或统计摘要。

## 目录映射边界

四个字段被映射为单一村级候选概念`community_farm_subsidy_program`，保留问卷指定的村级适用路线、Yes/No跳转和各自单位。它是宽泛的农业政策背景，不能据此判断某户实际收款，也不识别具体补贴种类；它不是农药/化肥使用、食品摄入或个人污染剂量。后续分析前仍须核对授权发行版编码、缺失值、抽样设计、社区链接与明确的估计目标。当前不具备这些条件，因此不生成关联结果。

## 来源

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`，Part G，JG017–JG020。
- `sources_official/CHARLS_2011_Codebook_extracted.txt`，JG017–JG020字段条目。

本次只使用公开题目、字段定义和类别元数据，未读取个人回答或汇总频数。
