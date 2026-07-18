# CLAUDE.md — 项目上下文

## 项目概述

ACGN Studio — 二次创作基础设施平台的 MVP。

核心目标：从 PRTS Wiki 抓取明日方舟干员数据，提供搜索和分析工具，服务二创生态。

## 架构

```
用户 → PyWebView 桌面端 / 浏览器 → FastAPI → SQLite → 干员数据
                ↑
          前端 index.html
```

数据流：PRTS Wiki → x_search.py 抓取 → init_db.py 导入 → SQLite → search.py 查询 → server.py API → 前端展示

## 关键文件

| 文件 | 职责 | 当前状态 |
|------|------|----------|
| `core/prts/x_search.py` | Wiki 数据抓取原型 | 仅支持单个干员，需重构 |
| `core/models.py` | 数据模型 | 3 字段：name, faction, avatar |
| `core/search.py` | 搜索逻辑 | 按名字模糊搜索 |
| `server.py` | API 服务 | 仅 /api/search 端点 |
| `init_db.py` | 数据初始化 | 硬编码 2 个干员，需改为自动抓取 |
| `ui.py` | 桌面入口 | PyWebView + FastAPI 线程 |
| `frontend/index.html` | 前端 | 空白占位 |

## 代码约定

- ruff 格式化，类型注解完整
- 变量 snake_case，类名 PascalCase
- 中文注释
- 抓取请求间隔 ≥ 1s
- 数据库用 SQLModel ORM
- PRTS Wiki API：`https://prts.wiki/api.php?action=parse&page={name}&prop=wikitext&format=json`

## 干员数据字段映射

| 目标字段 | Wiki 模板参数 | 示例 |
|----------|--------------|------|
| name | `干员名` | 凯尔希 |
| faction | `所属国家` | 罗德岛 |
| avatar | 由 `干员id` 拼接 | char_003_kalts |

## 常用命令

```bash
uv sync              # 安装依赖
python init_db.py    # 初始化数据库
python ui.py         # 启动桌面端
ruff check .         # lint
ruff format .        # 格式化
```

## 核心数据

三类素材是平台核心价值：

| 数据 | 说明 | 抓取来源 |
|------|------|----------|
| 立绘 | 精0/精1/精2/皮肤立绘图片 | PRTS Wiki 图片链接 |
| 语音 | 语音文件 + 台词文本 | PRTS Wiki 语音模块 |
| 资料 | 档案、属性、技能等 | PRTS Wiki 模板参数 |

## 业务上下文

平台定位：二创生态的"AWS"——提供基础设施，不直接生产内容。
商业模式：订阅制（高级工具 + 数据分析 + 自动化）。
当前阶段：验证需求，用明日方舟角色数据作为切入点。
