# 2011–2015住房出租月收入来源字段审计

更新：2026-10-22。2011、2013、2015官方问卷对HA052题意一致：主要受访者或配偶拥有、目前正在出租的所有房屋/房间月租；2011和2013另有HA053，询问其他家户成员拥有且正在出租的房屋/房间月租。金额分别存于HA052_1和HA053_1，单位为元/月。将金额字段映射为两个家户层候选概念，不把其他成员资产并入受访者/配偶名下，也不与家庭其他资产（非住房/非土地）租赁收入混同。

父项HA052/HA053不是直接的收入有无问项，而是回答适用性/格式选择：1=提供元/月金额，2=Not applicable/没有出租。故2011–2015父项改列C类元数据，仅金额子项入E。问卷/Codebook中金额字段报告0最小值，但不据此解释0为未出租；Not applicable走父项类别。结构性跳题、拒答和缺失不可补零，金额不可年化。

2015 Codebook对HA053及HA053_1明确标记No Observations，虽保留问卷/字段目录信息，改列C类inactive legacy metadata；不将其视为Other household member租赁收入的实际观测。2015 HA052及HA052_1仍有观测。

来源：2011基线问卷HA052–HA053及对应Codebook；2013问卷/Codebook HA052–HA053；2015问卷/Codebook HA052–HA053。实现见`scripts/build_residential_rental_income_crosswalk.py`及`audit/catalog_role_override_review_v1.csv`。只用官方问卷、Codebook和字段元数据，未读取个人记录。
