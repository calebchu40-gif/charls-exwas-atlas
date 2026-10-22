# CHARLS ExWAS Atlas 历史目录快照（2026-10-20）

> 本文数字是2026-10-20当时状态，现已由[current_directory_snapshot_2026-10-22.md](current_directory_snapshot_2026-10-22.md)取代；请勿将本文作为当前目录规模或待办数量。

## 当前规模与口径

- 元数据目录覆盖2011、2013、2015、2018、2020五轮；这是CHARLS纵向队列的重复访问，不是五个相互独立的横断面周期。
- 当前候选E/P Concept ID共840个：E=580、P=269，交集9个。18个经审查的同测量/同分析物别名已规范到一个Concept ID；原始ID记录在source crosswalk及网站字段的别名元数据中。候选概念仍不等同于最终分析指标。
- E/P概念—源字段链接5,236条，均匹配主字段目录；另有C类测量/流程/资格元数据23条（20条匹配目录、3条未匹配项均为非E/P权重资格记录）。此前38条同概念重复来源记录已在crosswalk中合并，出处仍保留。
- 网站字段目录7,623行：E/P字段—波次—角色—类别7,145行，C类478行。E/P目录去重后4,461条变量码—角色—类别序列；重复类别行不能计为不同指标。
- E/P目录中5,757行附有候选Concept ID；有官方类别标签复核或C类格式标签记录的目录行2,378条，覆盖2,127个波次—字段码；连续测量语义和区间组件另有独立复核状态。逐类别状态见`charls_ep_catalog_value_label_coverage_v1.csv`；自动标签检查仍有11条来源冲突/标签冲突需要专题审查。
- 未归属字段序列：E-only 848、P-only 73、双角色2。E-only空Concept ID主要仍是社会保障/养老金、就业职业、收入资产、教育社会位置和退休转换史字段家族；原先行为候选中4条（qa017三波、xpsyacttype三项）已转入C类元数据，剩余空ID行为序列以睡眠字段为主。变量序列数不是遗漏指标数。
- 同波字段元数据共现候选配对：2011 75,613；2013 65,392；2015 62,692；2018 58,108；2020 8,173。未计算配对样本量、复杂抽样分析或关联估计，正式模型数为0。

## 本轮新增内容

对正确的CHARLS 2011基线家户问卷及2013、2015、2018官方问卷进行户口生命周期题审计，新增8个候选E概念、31条波次字段映射：改革前户口类型、统一居民户口取得年月、当前户口取得年月、离开户口县市时长、曾持农业/非农业户口年份区间、访谈间户口类型变化年月、访谈间户口所在地变化年月。年/月/起止组件分开保留，条件分母、不同波次时间精度和特殊码边界已记录；不推导总时长，不映射或展示详细地理文本。详细依据见[`hukou_lifecourse_timing_and_absence_review_2026-10-20.md`](hukou_lifecourse_timing_and_absence_review_2026-10-20.md)。

户口专题crosswalk现有：生命周期历史36条映射/13个概念；访谈间变化16条映射/5个概念。E/P总体、波次配对和类别汇总见[`ep_concept_mapping_coverage_v1.md`](ep_concept_mapping_coverage_v1.md)、[`ep_candidate_pair_wave_coverage_v1.md`](ep_candidate_pair_wave_coverage_v1.md)及[`candidate_concept_category_counts_v1.md`](candidate_concept_category_counts_v1.md)。

## 2026-10-20续审：养老金与社会保障字段族

按官方2011基线、2013、2015、2018问卷/代码本补充养老金转移状态与来源、计划对应工作单位关系/提供单位类型、养老金计划地点、DB/DC类型、新农保参保与缴费承担者/月待遇、高龄津贴领取和DC账户查看题；2011企业补充养老金FN039=1题路另增计划类型、预期领取时点、缴费、DB待遇、DC账户查询、最早领取年龄及提前离岗待遇扣减映射。2011 `fn035`接入既有“缴费年限不足时的养老金安排”概念。保留方案限定、条件题分母、稀疏/无观测警示以及永久地址/当前居住地参照差异；不映射详细地点/自由文本，不将跳题空值解释为No或0。全量候选E/P概念840（E580/P269/交集9），E/P唯一概念—字段链接5,236且全部匹配目录。`fn011`、`fn036`、`fn042`（2011）与`fn094_w2`（2013/2015/2018）为C类格式父字段；实际金额/时点在配套字段，不能混合周期或单位。依据、路由与构建状态见[`pension_social_protection_field_family_review_2026-10-20.md`](pension_social_protection_field_family_review_2026-10-20.md)。正式模型仍为0。

## 2026-10-20续审：概念别名、来源重复与构念重叠

按唯一概念—角色—波次—字段码整理source crosswalk，合并38条相同概念链接的重复出处记录；进一步人工审查并规范18组确定的同测量/同分析物别名，42条来源链接统一到规范Concept ID，原始Concept ID、源文件和来源文档保存在`audit/ep_concept_source_crosswalk_v1.csv`。别名表见[`concept_alias_canonicalization_v1.csv`](concept_alias_canonicalization_v1.csv)。

别名规范后候选E/P Concept ID从842降至824（E=564、P=269、交集9），E/P唯一源字段链接5,200条。剩余28组同一波次字段指向多个构念，集中于身体活动总类与强度子项、吸烟状态的组成指标、饮酒频率与二分定义、疼痛等级与派生有无；依据现有波次代码本标签建立关系审计表，并在网站目录标注，不将重叠构念当独立关联检验。详见[`ep_concept_link_collision_review_v1.csv`](ep_concept_link_collision_review_v1.csv)及[`ep_concept_link_relationship_review_v1.csv`](ep_concept_link_relationship_review_v1.csv)；行为/疼痛关系的官方题意与路由依据汇总于[`behavior_overlap_relationship_review_2026-10-20.md`](behavior_overlap_relationship_review_2026-10-20.md)。

同时修正2011 `DB020` 的慢病治疗辅助误映射：题目为因健康/记忆问题造成的服药困难，归IADL功能表型。该项目前续审记录见[`source_crosswalk_duplicate_link_review_2026-10-20.md`](source_crosswalk_duplicate_link_review_2026-10-20.md)。



## 2026-10-20补充：测量/问卷元数据归类

将2011/2013/2015 `qa017` 从自动行为E候选移入C类。2013与2015官方体检问卷明确其为血压测试完成前30分钟内是否吸烟、运动、饮酒或进食；这是测量情境，不是习惯性暴露，也不是血检空腹指标。2011本地仅有代码本短标签，映射保守标记为临时C并要求回查体检问卷。另将2020 `xpsyacttype_1_`–`_3_`归入C：它们是DA032–DA035题干中的活动类型插入文本，真实行为回答在DA问卷字段。网站新增C类元数据检索页。逐项证据、路由与编码见[`qa017_and_xpsyacttype_metadata_review_2026-10-20.md`](qa017_and_xpsyacttype_metadata_review_2026-10-20.md)。

## 分析状态和边界

网站呈现CHARLS逐波原始变量码、官方标签、候选Concept ID、单位和审计状态，尚无关联结果。必须在获准取得相应数据后，逐波验证跳题与特殊缺失、测量分母、复杂抽样权重/PSU/分层/子样本资格、波次重复测量策略和协变量方案，再冻结分析指标与模型。禁止将共现数当作样本量、将未映射字段数当作可新增指标数，或将概念候选当作已经估计的显著关联。

网站原型：`site-prototype/dist/`；完整重建入口：`python scripts/build_ep_atlas_metadata.py`；协作者交接压缩包由 `scripts/package_collaborator_bundle.ps1` 生成。
## 分析状态和边界

网站呈现CHARLS逐波原始变量码、官方标签、候选Concept ID、单位和审计状态，尚无关联结果。必须在获准取得相应数据后，逐波验证跳题与特殊缺失、测量分母、复杂抽样权重/PSU/分层/子样本资格、波次重复测量策略和协变量方案，再冻结分析指标与模型。禁止将共现数当作样本量、将未映射字段数当作可新增指标数，或将概念候选当作已经估计的显著关联。

网站原型：`site-prototype/dist/`；完整重建入口：`python scripts/build_ep_atlas_metadata.py`；协作者交接压缩包由 `scripts/package_collaborator_bundle.ps1` 生成。
