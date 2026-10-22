# 当前欠薪及欠薪金额字段审计（2011–2018）

审计日期：2026-10-21。范围仅为官方问卷、Codebook及字段元数据；未读取或分析受访者个人记录，亦未将Codebook频数作为样本量。

## 构念与波次

CHARLS 2011、2013、2015、2018个人收入模块包含HC033与HC034。各波问卷的HC033询问雇主/工作单位目前是否拖欠受访者工资；回答“是”后由HC034询问拖欠金额（人民币元）。因此分别保留“当前欠薪状态”和“当前欠薪金额”两个概念。后者是面访时点的名义应收款，不是月收入或年收入。2011–2015问卷用1=是、2=否；2018另含999=拒答，必须单独保留。

## 路由、邻近字段与处理限制

HC034仅在HC033回答是时适用；结构性未询问必须与否、拒答及普通缺失区分。HC035属于不愿回答/记不清时的区间追问，不得用区间端点或中点代填HC034。HC031问的是“集资款”相关事项，与雇主欠薪不同，不得合并。欠薪金额跨波次比较前须预先指定价格指数与基年进行通胀调整；网站目前只展示原始量纲及限制，不生成调整值。

问卷和Codebook响应标签用来描述公开字段语义与编码，不以其频数、代码本样本数或资格筛选数表示本研究分析样本量。是否进入最终ExWAS候选集仍需在获准个人数据环境中核查分支、特殊值、分布及可分析性。

## 官方依据与复现

- `sources_official/CHARLS_2011_Questionnaire_extracted.txt`及`CHARLS_2011_Codebook_extracted.txt`
- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`及`CHARLS_2013_Codebook_extracted.txt`
- `sources_official/CHARLS_2015_Questionnaire_extracted.txt`及`CHARLS_2015_Codebook_extracted.txt`
- `sources_official/CHARLS_2018_Questionnaire_extracted.txt`及`CHARLS_2018_Codebook_extracted.txt`
- 可复现映射：`scripts/build_personal_income_crosswalk.py`；全量入口：`python scripts/build_ep_atlas_metadata.py`

映射表记录逐波来源字段、路由提示、量纲、标签及限制。此项扩充只处理公开元数据，未读取微观数据或拟合关联模型。
