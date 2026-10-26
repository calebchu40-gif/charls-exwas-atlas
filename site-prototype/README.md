2026-10-26本地待发布：新增硕士、博士学位路径及阶段中断66条字段映射；保留学位类型、学习方式、文凭支路及路由差异。Education History累计审查330/1,105字段，771个实质字段待核。总目录90概念、2,071映射（E 2,025、P 46）。审计见 udit/life_history_education_history_continuation_review_2026-10-26.md。本地app v152 / JSON v19，部署待验证。

2026-10-26本地待发布：大学专科、本科路径新增119条字段映射，分别保留就读方式、专业类别、毕业/文凭、双学位槽位、1971–1977年工农兵学员限定路由和中断原因。Education History累计映射264/1,105字段，837个实质字段待核。总目录86概念、2,005映射（E 1,959、P 46）。审计见 `audit/life_history_education_history_continuation_review_2026-10-26.md`。提交 `645b04a` 已上线为 app v151 / JSON v18；线上86条JSON记录且SHA-256与本地一致。

2026-10-26本地待发布：追加职业教育官方路径复核，纳入结构化就读方式、专业类别、毕业/文凭与中断字段48条；Life History目录82概念、1,914条字段映射（E 1,868、P 46）。Education History累计审查145/1,105字段，956个实质字段待核。学习方式分支各自保留；重复学校名称/地址和自由文本不纳入。详情见 `audit/life_history_education_history_continuation_review_2026-10-26.md`。提交 `eea2539` 已上线为 app v150 / JSON v17；线上82条JSON记录且SHA-256与本地一致。

2026-10-26本地待发布：Education History 续审新增高中教育经历、阶段中断细节和升学考试路径24条字段映射；该模块累计审查97/1,105字段，1,004个实质字段待核。Life History目录为80概念、1,866字段映射（E 1,820、P 46）。高中重复学校名称、起止时间和地址暂缓，待审查重复记录结构和隐私边界。来源审计：`audit/life_history_education_history_continuation_review_2026-10-26.md`。提交 `400085e` 已上线为 app v149 / JSON v16；线上80条JSON记录且SHA-256与本地一致。

2026-10-26本地待发布：Education History 续审对照官方问卷E012–E034c和Codebook字段身份，新增小学/初中教育完成情况及阶段中断原因4个概念、40条映射。目录重建为77个概念、1,842条映射（E 1,796、P 46）；教育史字段台账累计审查73/1,105，尚余1,028个实质字段待核。保留路由、回忆误差和无权重特殊调查限制；不发布Codebook频数、自由文本、学校名称地址或个体值。审计见 `audit/life_history_education_history_continuation_review_2026-10-26.md`。提交 `b70546e` 已上线为 app v148 / JSON v15；线上77条JSON记录且SHA-256与本地一致。

# CHARLS ExWAS Atlas 原型

这是一个本地静态查询原型，读取 `dist/` 中从CHARLS官方问卷、代码本及审计整理的字段级公开元数据。页面展示候选暴露（E）、候选表型（P）、字段角色、来源波次、答案标签、单位、路由及审校状态；不含受访者微观记录，也没有拟合或审查通过的关联结果。

当前目录覆盖2011、2013、2015、2018、2020五轮。最新全量重建见项目根目录 `README.md` 和 `audit/current_directory_snapshot_2026-10-22.md`。波次字段概念共现只表示目录元数据覆盖，不是实际人数、配对样本量或关联结果。

官方抽样权重核查记录在 `audit/charls_wave_sampling_and_weight_status_2026-10-22.md`。2018横截面权重有不同目标和非应答调整；2013提供独立横截面生物标志物权重；面板、体检/血样子样本须按各波官方说明处理。Wave 4权重和Sample_Info字段存在于本机受控准备表，但尚未核对其对应官方源文件的版本与哈希；现存历史聚合审计显示五波所有受访者的`communityID`均可匹配官方2013 PSU映射表；这仅验证社区ID键覆盖，原始文件版本及逐波适用性仍需重核，实际方差分层字段/估计方案尚未验证。2013准备脚本现要求保留官方`crosssection`与`longitudinal`标记，并在缺失时停止；由于原始发行包未在项目目录内，当前尚不能重建并拟合设计校正关联或发布实际pairwise N。Wave 5 年龄目标总体仍待官方样本信息与权重源文件校验，具体哈希和核对步骤见 `audit/wave5_sampling_file_source_verification_2026-10-22.md`。结果表规范使用 `audit/EXWAS_result_schema_v2.csv`。

启动：在项目根目录运行 `python -m http.server 8767 --bind 127.0.0.1 --directory site-prototype\dist`，然后访问 <http://127.0.0.1:8767/>。数据由 `scripts/build_ep_atlas_metadata.py` 生成。

只有在目标人群和资格、变量比较性、官方权重与方差设计、缺失处理、多重检验方案均落实，并获得相应数据许可后，才能接入通过披露审查的聚合关联结果。不得把代码本频数或字段共现数解释为个体分析结果。


2026-10-26更新：线上2014 Life History专题有73个概念组、1,802条字段映射（E 1,756、P 46）。Education History 首批审计将 E000–E011 的33个 Codebook字段映射到5个概念；其余1,068个实质字段明示待来源复核，暂不公开或用于分析。提交`ce4488f`已发布为 app v147 / JSON v14；539项测试、站点payload及前端检查通过，线上73条JSON记录与本地SHA-256一致。详情见 `audit/life_history_education_history_initial_review_2026-10-26.md`。

提交 `60360b1` 的 C1/C2 抚养人就业元数据复核已上线（app v141 / JSON v8）：覆盖8个结构化字段，细化了既有概念中的条件路由和缺失语义；自由文本职业详情排除。审计见 `audit/life_history_parent_employment_review_2026-10-26.md` 和 `audit/life_history_parent_employment_coverage_2014_v1.csv`。全套531项测试及公开包/分析锁检查已通过。

提交 `17d0c5c` 的 E7–E8/G1–G2敏感历史项目已上线（app v142 / JSON v9），使专题扩至42概念、1,033字段（E 1,005、P 28）。该批不包含参与者值或Codebook频数；警方拘留/指控仅标作敏感司法系统接触元数据，后续分析需要单独伦理、隐私和披露审查。审计见 `audit/life_history_sensitive_history_review_2026-10-26.md`。全量532项验证通过。

2014 `FAMILYINFORMATION` Codebook 473字段的全量唯一去向台账见 `audit/life_history_family_information_full_coverage_2014_v1.csv`；其中包括明确暂缓与排除字段，不把所有代码本字段都强行转为E/P。构建器和专项测试保证未分类字段不会静默漏过。

提交 `607d28a` 的RESIDENCE模块扩展已上线（app v143 / JSON v10），专题线上版本当时为44概念、1,452字段（E 1,424、P 28），新增T001迁入/迁出时间与T003e跨县迁移间隙停止原因。935条RESIDENCE字段均有唯一去向；县区和位置代码不公开映射或地理联结。完整台账和依据见 `audit/life_history_residence_full_coverage_2014_v1.csv`、`audit/life_history_residence_full_review_2026-10-26.md`。535项全量测试与公开包检查通过。

首页已调整为组会演示入口：先说明项目范围，再进入暴露/表型目录或关联状态；其余专题页收纳在更多专题目录。当前关联页明确显示0条已审查真实结果，目录字段数与潜在配对数均不是分析结果。