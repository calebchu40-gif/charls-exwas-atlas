# CHARLS ExWAS Atlas 当前工作状态（2026-10-24）

## 已完成

- 公开静态原型已部署在 <https://calebchu40-gif.github.io/charls-exwas-atlas/>，包含项目介绍、候选配对查询、E/P/C字段目录及多个专题索引。
- 五波字段分片为E 4,723、P 2,067、C 979；E/P目录通用“not yet reviewed”状态为0，C目录仍有202条通用待核记录（本轮共8条Wave 5人口学源字段进入专门审查状态）。正式关联模型数为0，没有公开效应估计或显著性结果。
- 89条 `DO NOT ANALYZE` 锁与审计表逐项一致。抽样权重、目标样本标记、PSU/方差估计、模块资格和特殊波次缺失仍是正式分析门槛。
- 已整理核心年龄、性别、教育、婚姻、户籍、居住地/城乡及调查设计的字段来源与准备状态，见[`core_covariate_readiness_2026-10-23.md`](core_covariate_readiness_2026-10-23.md)。它们仍是候选方案，没有固定的统一调整集。
- 新核对了Gateway to Global Aging Data的Harmonized CHARLS Version D Codebook：前四波年龄算法明确包含访谈年月、最近出生年月、缺出生月按6月、前两波缺出生年才用自报年龄及农历转换；性别字段需要保留跨模块/跨波冲突标记。审计说明和来源见[`official_age_gender_harmonization_review_2026-10-23.md`](official_age_gender_harmonization_review_2026-10-23.md)。
- 在本机受控准备数据内存中比较性别来源字段，仅写入波次级汇总：2013/2015/2018访员记录与`xrgender`分歧125/19/0；2020访员记录分歧小于10并抑制，`zrgender`与`xrgender`分歧36。没有导出ID或个人行；Wave 5官方优先级已按问卷公式补记，汇总差异继续作为整合 QA。
- 年龄输入清点发现，现有2011/2013个人分析准备表缺访谈年月`iyear/imonth`（字段在官方变量目录中指向weight/Weights模块）；2015–2020准备表有这些列。精确按Codebook重算前两波年龄需先恢复辅助模块并本地安全连接，不能用年份差代替。

## 本轮修正：关键词命中与协变量的区分

此前C目录使用较宽的关键词将人口学、年龄、性别、教育、婚姻、户籍、城乡和地区等字段归入“协变量候选”。抽查发现其中也包含预期寿命、疾病发生年龄、迁移史、访谈语言、家属名册槽位等不应自动用于调整的记录。目录生成规则和网站现已将自动命中类别改为“自动关键词检索线索（未核验协变量）”，并在字段状态中声明其只供检索，不代表变量含义已经核实或适合作调整。

当前C类自动关键词检索线索为456个波次字段行、300个不同变量码。202是C类通用值标签待核行数，不是核心混杂因素数，也不表示独立指标或混杂因素数。连续年龄等字段可能不需要离散类别标签。

## 验证

- 完成 `python scripts/build_ep_atlas_metadata.py --finalize-only`，重建主目录、C目录分片、候选配对索引和网站汇总。
- Python测试147项通过；`node --check site-prototype/dist/app.js`、延迟JSON加载器、`git diff --check`均通过。
- 本地目录检查确认C分片979行、E/P/C通用待核数为0/0/202，关键词自动命中类别419行，正式关联模型数仍为0。

## 接下来

1. 用核心协变量审计和合成边界测试核实年龄生成与性别冲突处理，再逐波明确教育/户籍状态机和居住地构念。
2. 完成调查设计字段的来源闭环，优先解决2013官方权重/样本标记及各波模块目标权重、PSU和方差字段。
3. 用合成数据搭好ExWAS统一结果表和模型管线，检查模型失败、样本流、多重检验与网站导入流程；仍不把合成数据当CHARLS结果。
4. 只有变量定义、样本资格、权重和方差处理经核验后，才运行正式关联扫描并将获准发布的汇总结果接入网站。


## 2026-10-24更新：Wave 5年龄与性别公式进入目录

- CHARLS 2020问卷辅助变量定义确认`xrage`：新访（`XRType=2`）或`ZRBirthYear`缺失时按`2020-BA003_1`；返访（`XRType=1`）且前波出生年存在时按`2020-ZRBirthYear`。这是年差算法，不是按访谈月日精算的周岁。
- 同一问卷确认`xrgender`：`zrgender`与访员记录`ba001`一致时取`ba001`，不一致时取当轮复核`ba002`；`zrgender`缺失时取`ba001`。`xr20gender`与`xr18gender`只是辅助字符串重编码。
- 已在目录中更新Wave 5的8条C字段元数据；候选状态保持不变，未把这些字段设成固定调整集。C目录通用值标签待核数从210降为202；C关键词线索总数当前为456行/300个变量码，这是不同口径。
- `python scripts/build_ep_atlas_metadata.py --finalize-only`完成；全套147项测试通过。配对索引仍只代表元数据共现，正式模型仍为0。
- 官方原始来源：`sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`与`CHARLS_2020_Codebook_extracted.txt`；复现脚本和测试：`scripts/apply_wave5_core_demographic_review.py`、`tests/test_wave5_core_demographic_review.py`。
