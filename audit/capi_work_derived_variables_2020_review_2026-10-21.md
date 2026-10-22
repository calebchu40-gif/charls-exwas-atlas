# CHARLS 2020 CAPI派生工作状态变量审计

日期：2026-10-21。来源为CHARLS 2020官方英文问卷（辅助变量定义，印刷页约69–71）、Codebook和字段目录。只使用官方变量定义及问卷公式，不使用Codebook描述性频数作选项、有效样本量或分析结果；未读取个人级记录。

## 已确认并进入候选目录的派生量

| 字段 | 官方公式/含义 | 当前处理和分析边界 |
|---|---|---|
| `xworking` | 若`FA001`、`FA004`、`FA007`、`FA008`任一为1，则1，否则0 | 单波总体工作状态汇总；与非农工作`FA004`不是同一范围，也不是独立题目。目录保留公式来源，配对时应选一个预先定义的工作状态，避免同模型重复调整原始构成字段。 |
| `xemployed` | 根据`FA010/FA011`主业类型及`FA002`是否选择他人付薪农业工作生成：代码1代表受雇工作（含付薪农业工作），代码0代表自营或无酬家族企业帮助 | 问卷标题“Whether self-employed or not”与公式的正负方向容易误读，目录按公式并明确编码方向；获准数据中核验缺失/条件路线前只作候选。 |
| `xworkjuststarted` | 依`FC018/FC019`开始时间与`XIWYear/XIWMonth`比较：1=最近一个月、2=最近一年内、0=不在上述近期范围 | 派生时间段分类而非原始工龄；保留原始年月，分析前核验月份边界、无效/缺失年月与条件路线。 |
| `xgetjob` | `ZWorking=0`且`XWorking=1`时为1，否则0 | 前次非工作到本轮工作的算法派生状态；与条件性自报的`FA013`相关但不是同一题义/分母，需预先选择估计目标并核验ZWorking预载可用性。 |
| `xquitjob` | `ZWorking=1`且`XWorking=0`时为1，否则0 | 前次工作到本轮非工作算法派生状态；与条件性日期题`FA016`相关但不是同一题义/分母，需核验ZWorking。 |
| `xsidejobdays` | `FE001`（每周副业天数）乘52；公式把乘积缺失设为0 | CAPI年化派生量，不是直接报告年总天数；保留52周假设，不能未经路线核验就把0等同于确认没有副业。 |

以上仅是逐波搜索目录中的候选E字段，非已经批准的分析暴露。其余字段仍逐字段保留原题/波次信息；不合并跨波不同题目。

## 明确排除/暂停的近邻派生字段

- `xmainjobdays`：问卷公式两个分支均判断`XEmployed=1`，然后依次写入`FC026*52`和`FD008*52`。第二分支不可达，且无法确认是文档笔误还是实际CAPI逻辑。2020 Codebook的字段标题“Days of Main Job”和摘要统计仅描述发布变量分布，未说明实际采用了哪一个输入公式，不能据此裁定其计算来源。当前仍排除分析，等待官方勘误或发行版程序说明。
- 其他CAPI/预载字段如`xfgsample`（疫情题组抽样/路由）、`zworking`（前次访问工作状态预载）属于提问资格/跨轮输入，不作为独立E/P暴露；只有像`xgetjob`这种有明确定义、且研究目标需要的派生状态才保留候选并标记为算法产生。

## 复现与来源

- 项目本地：`sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`（FA010/FA011及工作辅助变量定义）、`sources_official/CHARLS_2020_Codebook_extracted.txt`（字段标签）。
- 官方发布页：[2020 Wave 5 文档与数据页面](https://charls.charlsdata.com/pages/Data/2020-charls-wave5/en.html)；官方问卷PDF：[CHARLS 2020 Questionnaire English](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_Questionnaire_English.pdf)。
- 可重建映射：`scripts/build_work_exposure_crosswalk.py`和`scripts/build_work_exposure_value_labels.py`。手工整理的类别解释从问卷公式转录，不复制频数。
