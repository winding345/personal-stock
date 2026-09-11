# 同类项目调研（个人库存 / 药箱 / 保质期）

> star 数为调研时（2026-09）的实时值。

## 开源项目

| # | 项目 | Stars | 定位 | Demo |
|---|---|---|---|---|
| 1 | [grocy/grocy](https://github.com/grocy/grocy) | 9,476 | 自托管「冰箱之外」的家居/食品 ERP，**保质期(best-before)追踪**、库存、购物清单 | https://demo.grocy.info |
| 2 | [snipe/snipe-it](https://github.com/snipe/snipe-it) | 14,920 | IT 资产/许可证管理（星最高，偏企业） | https://snipeitapp.com/demo |
| 3 | [TandoorRecipes/recipes](https://github.com/TandoorRecipes/recipes) | 8,583 | 菜谱 + 备餐 + 采购清单（含库存概念） | https://app.tandoor.dev |
| 4 | [inventree/InvenTree](https://github.com/inventree/InvenTree) | 7,539 | 开源库存管理系统（零件/物料/批次） | https://demo.inventree.org |
| 5 | [sysadminsmedia/homebox](https://github.com/sysadminsmedia/homebox) | 7,131 | **家庭物品库存**，自托管，标签/位置/图片 | https://homebox.software |
| 6 | [TomBursch/kitchenowl](https://github.com/TomBursch/kitchenowl) | 3,673 | 家庭共享采购/库存清单 | https://kitchenowl.org |
| 7 | [Part-DB/Part-DB-server](https://github.com/Part-DB/Part-DB-server) | 1,756 | 电子元件库存管理 | https://demo.part-db.de |
| 8 | [Timmoth/RackPeek](https://github.com/Timmoth/RackPeek) | 1,679 | 家庭机房/IT 资产清点 | https://timmoth.github.io/RackPeek/ |
| 9 | [lorenzovngl/FoodExpirationDates](https://github.com/lorenzovngl/FoodExpirationDates) | 223 | **食品保质期追踪** App（Android，Compose） | https://foodexpirationdates.app |
| 10 | [matt-schwartz/personal-inventory](https://github.com/matt-schwartz/personal-inventory) | 112 | **个人库存 Web 应用**（与本项目最接近的形态） | 无（自托管） |

## 闭源 / 商业产品

| # | 产品 | 定位 | 链接 |
|---|---|---|---|
| 11 | Sortly | 家庭/商用物品库存，卡片+图片+二维码 | https://sortly.com |
| 12 | Medisafe | 用药提醒，千万级用户 | https://medisafe.com |
| 13 | MyTherapy | 用药提醒 + 健康日志 | https://www.mytherapyapp.com |
| 14 | Encircle | 家庭物品存档（保险理赔向） | https://encircleapp.com |

## 与「个人药箱记录」最接近的三个

1. **grocy**（9.5k）——功能最全、最贴近「家居物品 + 保质期」。有库存、保质期、购物清单、按位置分组。
2. **homebox**（7.1k）——纯粹的「家庭物品库存」，卡片式、标签/位置/图片，交互最简洁。
3. **matt-schwartz/personal-inventory**（112）——形态上就是「个人库存 Web 应用」，小而近。

## 可借鉴的点

- **保质期视觉分级**（grocy）：按「已过期 / 临期 / 正常」分色，直接扫一眼就知道要处理什么。
- **卡片 + 缩略图/图标**（homebox、Sortly）：一物一卡，视觉识别快。
- **位置/容器维度**（grocy、homebox）：不止「分类」，还有「放在哪」（药箱/抽屉/柜子）。
- **数量步进 + 低库存阈值**（InvenTree、Sortly）：扫一眼就知道要不要补。
- **移动端底部导航 + FAB**（kitchenowl、foodexpiry）：单手可操作。
- **统计概览头**（grocy、InvenTree）：顶部给「健康度/临期数/过期数」。
