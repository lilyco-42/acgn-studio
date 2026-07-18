# ACGN Studio — 二创基础设施平台

## 项目定位

面向二次创作生态的基础设施平台，当前 MVP 阶段从《明日方舟》角色数据切入。

商业逻辑：PRTS wiki 数据 → 干员库 → 搜索/分析工具 → 创作者使用 → 商业化

## 技术栈

- Python 3.11+
- FastAPI + Uvicorn（Web 服务）
- SQLModel + SQLite（数据存储）
- PyWebView（桌面客户端）
- httpx + mwparserfromhell（Wiki 数据抓取）
- Meilisearch（全文搜索，待接入）

## 项目结构

```
search/
├── core/
│   ├── models.py          # 数据模型：Character(name, faction, avatar)
│   ├── database.py        # SQLite 引擎
│   ├── search.py          # 搜索逻辑
│   └── prts/
│       └── x_search.py    # PRTS Wiki 数据抓取
├── server.py              # FastAPI 入口（API + 静态文件）
├── ui.py                  # PyWebView 桌面入口
├── init_db.py             # 数据库初始化 / 数据导入
├── frontend/
│   └── index.html         # 前端页面
└── data/
    └── app.db             # SQLite 数据库文件
```

## 开发规范

### 代码风格

- 使用 ruff 格式化和 lint
- Python 类型注解必须完整
- 函数和变量使用 snake_case
- 类名使用 PascalCase
- 中文注释和文档字符串

### 运行命令

```bash
# 安装依赖
uv sync

# 初始化数据库（含数据抓取）
python init_db.py

# 启动服务
python server.py          # 仅 API 服务
python ui.py              # 桌面客户端（PyWebView）

# 代码检查
ruff check .
ruff format .
```

### 数据抓取约定

- 抓取 PRTS Wiki（prts.wiki）使用 MediaWiki API
- 请求间隔 ≥ 1 秒，避免被封禁
- User-Agent 标识为 ACGN Studio
- 数据字段映射：干员名→name, 所属国家→faction, 干员id→avatar URL

### 数据库约定

- 使用 SQLModel 定义模型
- 数据库文件位于 `data/app.db`
- 通过 `init_db.py` 初始化和导入数据
- 支持 upsert 模式（按 name 去重）

## 后端 API

| 端点 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/search` | GET | `q` | 按名字搜索干员 |

返回格式：JSON 数组，每项包含 `id, name, faction, avatar`

## 核心数据（优先级最高）

平台核心价值是三类素材数据：

| 数据 | 内容 | 存储方式 |
|------|------|----------|
| 立绘 | 角色立绘图片（精0/精1/精2、皮肤） | 本地文件 + CDN URL |
| 语音 | 角色语音文件 + 台词文本 | 本地文件 + 文本字段 |
| 资料 | 角色档案、属性、技能等基础数据 | SQLite |

## 当前待办

- [ ] 重构 x_search.py 为可复用的数据抓取模块
- [ ] 实现立绘数据抓取（图片 URL 解析 + 本地缓存）
- [ ] 实现语音数据抓取（音频 URL 解析 + 本地缓存）
- [ ] 扩展 Character 模型（rarity, profession 等字段）
- [ ] 实现批量干员抓取（从干员一览页遍历）
- [ ] 实现前端搜索界面（展示立绘、播放语音、查看资料）
- [ ] 接入 Meilisearch 全文搜索
