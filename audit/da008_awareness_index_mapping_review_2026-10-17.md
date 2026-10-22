# DA008_W2_1 慢病知晓方式字段索引复核

更新：2026-10-17。依CHARLS 2013/2015/2018官方变量目录、各波代码本和2018问卷整理；只处理字段元数据与公开编码说明，不读取受访者值。

## 映射结论

2013、2015、2018年的`DA008_W2_1_[i]`是针对`DA007`慢病列表第i项询问受访者如何知道自己有该病。三个波次的原始代码本常以“the Nth disease of DA007”给字段命名；2018问卷明确说明，只有`DA007[i]=1`或前次已知状态`DA008[i]=1`的返访路径才继续询问知晓方式。由于字段索引与已审核的慢病疾病概念crosswalk一致，本项目将每波1–14号字段映射至相同疾病概念的“自知/知晓方式”辅助字段。

这些变量记录信息来源，不是疾病有无或医生诊断。网站值标签为：`1=Exam after disease attack; 2=Exam after illness; 3=Work-unit exam; 4=Community exam; 5=CHARLS physical exam; 6=Other`。值标签不带代码本频数；正式分析前仍需为目标波次/人群复核分支资格和结构性缺失。

2013年的`DA007`第15槽位不在慢病概念字典的1–14项中，故`DA007_W2_*_15_`和`DA009_*_15_`不作为一个命名疾病结局。代码本对少数第15槽位字段的稀疏记录不构成稳定构念证据；“其他疾病”不应混入任一种具体病种。

## 可复现位置

- 字段映射：`audit/chronic_disease_ancillary_variable_mapping_v1.csv`
- 官方索引：`audit/chronic_disease_concept_crosswalk_v2.csv`
- 构建脚本：`scripts/build_chronic_disease_ancillary_crosswalk.py`
- 来源：`sources_official/CHARLS_2013_Codebook_extracted.txt`、`sources_official/CHARLS_2015_Codebook_extracted.txt`、`sources_official/CHARLS_2018_Codebook_extracted.txt`和`CHARLS_2018_Questionnaire_extracted.txt`
