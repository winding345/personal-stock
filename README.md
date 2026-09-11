# 个人库存记录（Personal Stock）

一个**个人用的通用库存/物品记录网站**。手机优先，Docker 部署，数据存 SQLite。
最初用来记录**家庭药箱**，但数据模型是通用的——建个「冰箱」「工具箱」就能记别的。

## 装到手机（PWA）

本项目带 **PWA** 支持，可以像 App 一样装到手机桌面——**不用上架、不用签名、不花钱**。

| 平台 | 安装方式 |
|---|---|
| **iPhone / iPad** | Safari 打开 → 「分享」→「添加到主屏幕」 |
| **Android** | Chrome 打开 → 菜单 →「安装应用」/「添加到主屏幕」 |

装好后：
- 桌面出现独立图标「**家库**」
- 点开**全屏**运行，没有浏览器地址栏
- 有启动画面、状态栏跟随主题色
- **断网也能打开**（Service Worker 缓存了页面；数据仍需连到后端）

> iOS 必须用 **Safari**（Chrome 在 iOS 上不支持添加到主屏幕）。

## 功能

- **多仓库**：药箱 / 冰箱 / 工具箱…各自独立；**每个仓库有独立 URL**（`/w/1`），可收藏、可加到手机主屏
- **底部横滑 Tab** 切换仓库，角标显示物品数；有临期/过期时角标**变红**提示
- **长按仓库 Tab** → 改名 / 导出该仓库 / 删除
- **卡片网格**布局，绿色主题，手机优先；**默认半透明加号**不挡内容
- **物品包装图**：拍照或选图作为卡片图标（前端压缩后上传，容器无需图像库）
- **有效期管理**：已过期 / 30 天内到期自动标注
- **数量预警**：数量 ≤ 阈值标红（“需补充”）
- **排序**：名称 / 有效期 × 正序 / 倒序（无有效期恒排最后，偏好本地记忆）
- **搜索**：按名称 / 备注实时过滤
- **导出**：`/api/export` 全量，`/api/export?category_id=N` 单仓库
- **离线可用**：字体（Poppins）与图标（内联 SVG）全部自托管，不依赖 CDN

## 界面结构

```
家庭药箱                        ← 当前仓库名
家庭物品记录
[🔍 搜索名称 / 备注…]
总数量 53  过期数量 1  临期数量 0     ← 点数字可筛选
排序  [名称|有效期] [正序|倒序]
──────────────────────────────
物品卡片网格                 (＋) ← 加物品（半透明悬浮）
──────────────────────────────
[家庭药箱 ①] [test 0] [＋ 仓库]      ← 底部仓库栏
```

## 数据与图片位置

| 内容 | 路径（容器内） | 路径（宿主机） |
|---|---|---|
| 数据库 | `/data/stock.db` | `./data/stock.db` |
| 物品照片 | `/data/images/<id>.jpg` | `./data/images/` |

> 备份时把整个 `./data` 目录拷走即可（含数据库 + 照片）。`./data` 已 gitignore，**不会上传到 GitHub**。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLite（+ python-multipart 处理上传） |
| 前端 | 单页 HTML/CSS/JS（无外部 CDN，可离线） |
| 字体 | 自托管 Poppins（latin 子集，OFL） |
| 图标 | 内联 SVG 线性图标（无图标库依赖） |
| 部署 | Docker / Docker Compose |

## 本地运行

```bash
# 生产模式
docker compose up -d --build
# 访问 http://localhost:8000

# 开发模式（挂载源码 + 热更新）
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

## 手机访问（局域网）

应用绑定 `0.0.0.0:8000`。同一局域网内的手机访问 `http://<你的电脑IP>:8000`：

```bash
hostname -I        # 查本机 IP
```

> ⚠️ 手机和电脑必须在同一 WiFi。跨网络访问需内网穿透或部署到公网。

## 部署到 NAS（Docker）

把整个项目目录拷到 NAS，改 `docker-compose.yml` 里 `./data` 的宿主机路径：

```yaml
volumes:
  - /volume1/docker/personal-stock/data:/data    # 改成你 NAS 的持久化目录
```

```bash
docker compose up -d --build
```

- 端口默认 `8000`，可改 `ports` 映射；注意放行防火墙
- 数据放 NAS 持久化目录（非容器层），升级/重建不丢
- `data/` 里的文件由容器内 root 写入；若 NAS 以非 root 用户跑容器，可能需 `chown`

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `STOCK_DB_PATH` | `/data/stock.db` | SQLite 文件路径 |
| `STOCK_IMAGES_DIR` | `/data/images` | 物品照片目录 |

> 端口和数据路径直接在 `docker-compose.yml` 里改（见下方「更新部署」）。

## 更新部署

```bash
cd <项目目录>
git pull                          # 拉最新代码（data/ 不受影响）
docker compose up -d --build      # 重新构建并重启
```

> `data/` 是 gitignore 的本地目录，`git pull` **不会覆盖你的数据**。

**如果你在 NAS 上改过 `docker-compose.yml`**（比如换端口、改数据路径），而这次更新恰好也动到了这个文件，`git pull` 会报冲突。两种处理：

```bash
# 方式一：先看自己改了什么，再决定保留哪边
git diff docker-compose.yml

# 方式二：暂存本地改动 → 拉取 → 放回
git stash && git pull && git stash pop
```

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/items` | 列表（`?flag=low_stock\|expired\|expiring_soon`、`?category_id=`、`?include_archived=1`） |
| POST | `/api/items` | 新增物品 |
| PUT | `/api/items/{id}` | 修改物品 |
| POST | `/api/items/{id}/quantity` | 数量调整 `{delta:+1/-1}` |
| DELETE | `/api/items/{id}` | 删除物品（连带删图） |
| POST | `/api/items/{id}/image` | 上传包装图（multipart） |
| DELETE | `/api/items/{id}/image` | 移除包装图 |
| GET | `/api/categories` | 仓库列表 |
| POST | `/api/categories` | 新建仓库 |
| PATCH | `/api/categories/{id}` | 重命名仓库 |
| DELETE | `/api/categories/{id}` | 删除仓库（物品变为未分类） |
| GET | `/api/export` | 导出 JSON（`?category_id=N` 只导该仓库） |
| GET | `/api/stats` | 统计 |
| GET | `/w/{id}` | 仓库直达 URL（返回 SPA，前端按路径切换） |

## 目录结构

```
personal-stock/
├── app/
│   ├── main.py             # FastAPI 路由 + SPA 托管
│   ├── db.py               # SQLite 连接与建表（含轻量迁移）
│   ├── schemas.py          # Pydantic 模型
│   └── static/
│       ├── index.html      # 移动端前端（单文件 SPA）
│       ├── manifest.json   # PWA 清单
│       ├── sw.js           # Service Worker（离线缓存）
│       ├── icons/          # PWA 图标（192/512/掩码/apple-touch/favicon）
│       └── fonts/          # 自托管 Poppins（OFL，见 NOTICE.txt）
├── data/                   # SQLite + 照片（gitignore，私有数据）
├── docs/research/          # 同类项目调研清单（仅结论，无截图）
├── Dockerfile
├── docker-compose.yml      # 生产
├── docker-compose.dev.yml  # 开发（热更新）
└── requirements.txt
```
