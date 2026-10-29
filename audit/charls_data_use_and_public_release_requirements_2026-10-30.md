# CHARLS 数据使用条款与公开发布边界

**核对日期：2026-10-30**  
**用途：CHARLS ExWAS Atlas 的公开目录、分析代码和结果发布控制。**

## 官方条款

CHARLS 官方数据访问条款要求：数据仅用于学术研究，不用于商业用途；原始微观数据不得以任何形式出版；只能公开统计/分析结果，且结果不得泄露受访者个人信息；不得发布、转让、出售、出租、借贷或以其他方式提供 CHARLS 数据给他人。官方要求使用 2011/2013 数据的发表物致谢：“感谢北京大学国家发展研究院中国经济研究中心提供CHARLS数据。”并引用《China Health and Retirement Longitudinal Study, 2011-2012 National Baseline Users' Guide》（Zhao et al., 2013）。

依据：[CHARLS 官方数据访问条款（北京大学开放研究数据平台所列 CHARLS 条款）](https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=92&fileId=77)；[CHARLS 官方用户条款入口](https://charls.charlsdata.com/users/sign_up/agreement/zh-cn.html)；[CHARLS 官方 FAQ](https://charls.pku.edu.cn/en/Faq/Frequently_Asked_Questions.htm)。正式发表时，应同时按所用波次、数据模块及各波次指南补充相应的官方推荐引用。

## 本项目执行边界

- 原始 CHARLS 压缩包、Stata 文件、个体 ID、逐人派生表、模型对象及任何可反推出个体记录的产物只留在受控私有分析目录，不进入 GitHub、OneDrive、协作者交接包或 GitHub Pages。
- GitHub 仓库和网站可放置项目代码、经审阅的公开问卷/Codebook 元数据、方法说明和官方文档引用；不放置 CHARLS 原始微观数据。
- 网站上的关联结果只有在模型设计与审查准入完成、聚合结果通过披露审查后才发布。不得展示小单元、可识别地理/社区键或其他可重识别信息。
- 当前线上平台展示目录和方法状态；正式关联结果仍为 0，结果 JSON 不存在。结果状态不得用合成演示或未批准的探索结果替代。
- 网站页脚使用上文的官方数据致谢原文，并链接到 CHARLS 官方 Wave 1 数据目录和用户条款。该致谢要求针对使用数据的发表物；网站包含该文字是额外透明说明，不改变任何访问授权。

## 本次网站边界核对

核对了当前 Git 跟踪文件扩展名，未发现 `.dta`、`.sav`、`.sas7bdat`、`.zip` 或 `.rar` 数据包；线上首页 HTTP 200，`data/association_results_v1.json` HTTP 404。首页方法区已说明 CHARLS 条款和不得发布微观数据。本次修正将页脚致谢改成官方要求的原文，并把官方数据目录链接更新为当前 Wave 1 页面。没有将个体数据或分析结果加入站点。
