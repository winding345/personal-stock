# 个人库存记录（Personal Stock）

一个**个人用的通用库存/物品记录网站**。手机优先，Docker 部署，数据存 SQLite。
第一个用途是记录**药箱存量**，但数据模型是通用的——加个分类就能记别的东西（护肤品、食品、工具……）。

## 功能

- **卡片网格**布局，绿色主题，手机优先
- 按分类记录物品：名称、数量、单位
- **数量预警**：数量 ≤ 阈值自动标红（“需补充”）
- **有效期管理**：已过期 / 30 天内到期 会自动标注
- **包装图/照片**：给物品拍一张药盒照片，作为卡片图标（前端压缩后上传，无需装图像库）
- 手机友好：卡片内 `−/＋` 快速增减，数字带动效
- 分类管理：自定义药箱/食品/工具等
- 数据备份：一键导出全量 JSON
- **离线可用**：字体（Poppins）与图标（内联 SVG）全部自托管，不依赖 CDN

## 数据与图片位置

| 内容 | 路径（容器内） | 路径（宿主机） |
|---|---|---|
| 数据库 | `/data/stock.db` | `./data/stock.db` |
| 物品照片 | `/data/images/<id>.jpg` | `./data/images/` |

> 备份时把整个 `./data` 目录拷走即可（含数据库 + 照片）。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLite（+ python-multipart 处理上传） |
| 前端 | 单页 HTML/CSS/JS（无外部 CDN，可离线） |
| 字体 | 自托管 Poppins（latin 子集，OFL） |
| 图标 | 内联 SVG 线性图标（无图标库依赖） |
| 部署 | Docker / Docker Compose |

## 本地运行

### 生产模式
```bash
docker compose up -d --build
# 访问 http://localhost:8000
```

### 开发模式（源码热更新）
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

## 手机访问（局域网）

应用绑定 `0.0.0.0:8000`。同一局域网内的手机访问：

```
http://<你的电脑IP>:8000
```

找本机 IP：
```bash
hostname -I        # 或 ip addr | grep inet
```

> ⚠️ 手机和电脑必须在同一 WiFi。若要跨网络访问，需内网穿透或部署到公网。

## 数据存储

- SQLite 数据库文件：`./data/stock.db`（Docker 内 `/data/stock.db`）
- `./data` 已挂载为持久卷：删容器不丢数据，拷贝 `data/stock.db` 即备份
- 备份/恢复：网页右下角工具条「⬇️ 备份」导出 JSON；恢复时把 JSON 里的 `categories`/`items` 手工插入或后续加导入功能

## 部署到 NAS（Docker）

把整个项目目录拷到 NAS，改 `docker-compose.yml` 里 `./data` 的宿主机路径即可：

```yaml
volumes:
  - /volume1/docker/personal-stock/data:/data    # 改成你 NAS 的持久化目录
```

然后：
```bash
docker compose up -d --build
```

- 端口默认 `8000`，可改 `ports` 映射
- 注意 NAS 防火墙放行该端口
- 数据建议放 NAS 的持久化目录（非容器层），升级/重建不丢

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `STOCK_DB_PATH` | `/data/stock.db` | SQLite 文件路径 |

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/items` | 列表（支持 `?flag=low_stock\|expired\|expiring_soon`、`?category_id=`、`?include_archived=1`） |
| POST | `/api/items` | 新增 |
| PUT | `/api/items/{id}` | 修改 |
| POST | `/api/items/{id}/quantity` | 数量调整 `{delta:+1/-1}` |
| DELETE | `/api/items/{id}` | 删除 |
| GET/POST | `/api/categories` | 分类列表/新增 |
| DELETE | `/api/categories/{id}` | 删除分类 |
| GET | `/api/export` | 导出 JSON |
| GET | `/api/stats` | 统计（在用/需补充/已过期/将过期） |

## 目录结构

```
personal-stock/
├── app/
│   ├── main.py          # FastAPI 路由 + SPA 托管
│   ├── db.py            # SQLite 连接与建表
│   ├── schemas.py       # Pydantic 模型
│   └── static/index.html# 移动端前端
├── data/                # SQLite 持久化（gitignore）
├── Dockerfile
├── docker-compose.yml   # 生产
├── docker-compose.dev.yml # 开发（热更新）
└── requirements.txt
```
