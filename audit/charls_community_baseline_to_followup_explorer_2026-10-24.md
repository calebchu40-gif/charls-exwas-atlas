# 2011基线社区环境—随访表型候选浏览器

## 页面新增内容

候选配对页新增一个独立设计选项：把2011年社区层级E候选，与2013、2015、2018或2020波次的P概念按目录配对。当前官方审阅过的2011社区目录含113个候选概念。每个随访波次的组合数是113乘以该波次表型概念数，仅表示概念目录组合。

该视图只收录来源模块明确为`community`的2011暴露字段。它不读取或连接CHARLS受访者、社区或家庭记录，不计算任一配对的实际样本量、效应或显著性，也不把社区层级信息称为个人污染剂量。

## 官方ID依据

- `sources_official/CHARLS_2013_Wave2_Release_Note_extracted.txt` 第62行附近：individualID、householdID和communityID可匹配到基线样本对应记录；说明community IDs相同，同时警告householdID格式不同。此处采用的只是社区ID说明，不采用个体或家庭ID假定。
- `sources_official/CHARLS_2018_Users_Guide_extracted.txt` 第529行附近：ID、householdID和communityID可与前序波次对应ID匹配；指南还指出基线householdID和ID需要按Wave 2发布说明调整。
- `sources_official/CHARLS_2020_User_Guide_English_extracted.txt` 第508行附近：同样说明三类ID可与前序波次对应记录匹配，并提示基线ID调整。
- `sources_official/CHARLS_2018_Users_Guide_extracted.txt` 第348–355行附近：CHARLS称会尽量面对面追访受访者，不论其迁居到何处，并说明会用既有联系信息寻找迁居者。因此不能假设迁居者不再追访；当前浏览器也没有连接个人迁移史或目的地字段。

官方ID说明支持研究者检查跨波次社区键的可连接性，但不能证明每名受访者持续居住在基线社区，也不能确定某社区题项是否适合代表随访时期的暴露。CHARLS会尽量追访迁居者，因此正式队列定义应核查迁移状态及目的地。项目已有`audit/charls_psu_mapping_aggregate_v1.csv`仅为旧版聚合键覆盖核查，并明确标记`aggregate_key_coverage_only_not_variance_design_validation`；它不是本次跨波次连接，也不构成方差设计验证。

## 正式分析前仍需核查

1. 使用每一波正式发布的社区/个人文件及其哈希，核对社区键格式和一对多结构；不得将聚合键覆盖检查当作个体匹配成功。
2. 依据研究问题定义基线暴露、基线时点、随访结局和居住迁移处理策略；不能把基线社区条件解释为随访时的现居环境。
3. 确认队列资格、基线/随访题目路由、死亡与失访、缺失处理，以及实际配对的可分析样本量。
4. 逐波核实官方权重适用范围、纵向权重/样本标志和抽样方差设计。权重、PSU或层变量不能从本目录或聚合映射推定。
5. 预先规定模型、协变量因果结构、多重检验家族与结果披露规则，再运行正式关联分析。

## 实现与验证

数据由`scripts/build_candidate_pair_explorer.py`从已审核的E/P来源交叉表生成；测试保证跨波次暴露字段全部来自2011 `community`模块、表型来自指定随访波次、四波共用同一组113个暴露概念，并保留“未连接个体记录”的状态。页面明确显示迁移、权重、失访和方差设计限制。


## 页面修订与部署验证

审计后补充了Wave 4用户指南中“尽量追访迁居者”的说明，修正早期页面对迁移能力的宽泛表述。`tests/test_candidate_pair_explorer.py`校验页面同时说明CHARLS追访迁居者、此浏览器不连接个人迁移史。全套341项Python测试通过；提交`e3934be`已推送，公开Pages index返回HTTP 200并包含修订文案。


Direct official document links shown in the page:

- Wave 2 Release Note: <https://charls.pku.edu.cn/en/data/Release2013.pdf>
- Wave 4 User Guide: <https://charls.pku.edu.cn/en/data/User2018.pdf>
- Wave 5 (2020) User Guide, corrected official CHARLS data-host URL: <https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf>

The published HTML returned HTTP 200 and contains these links and the mover-tracking note. The separate official PDFs were verified through the official sites; a shell-only HEAD check was inconclusive because of local TLS EOFs.
