# ACGN Studio

明日方舟干员数据平台 — 搜索、浏览、下载角色立绘与语音素材。

## 功能

- **干员搜索**：按名称搜索 449 名干员
- **懒加载详情**：点击干员时自动抓取立绘、语音等详情并缓存
- **立绘浏览**：精0/精2/皮肤立绘预览与下载
- **语音播放**：在线播放干员语音，支持逐条或批量下载
- **批量下载**：一键下载全部立绘或语音，下载完成后提示路径并打开文件夹
- **桌面客户端**：基于 PyWebView 的独立桌面应用，无需浏览器

## 截图

<!-- TODO: 添加截图 -->

## 安装

### 方式一：下载 exe（推荐）

从 [Releases](https://github.com/lilyco-42/acgn-studio/releases) 下载最新版本，解压后运行 `ACGN-Studio.exe`。

首次启动会自动从 PRTS Wiki 抓取干员数据，进度条显示在界面上方。

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/lilyco-42/acgn-studio.git
cd acgn-studio

# 安装依赖
uv sync

# 启动桌面客户端
uv run python ui.py
```

## 使用

启动后自动打开桌面窗口：

1. **搜索**：在顶部搜索框输入干员名称，按回车或点击搜索
2. **查看详情**：点击干员卡片，自动加载详情（首次较慢，后续秒开）
3. **播放语音**：在详情页点击 ▶ 按钮播放语音
4. **下载素材**：
   - 单个文件：点击 ⬇ 按钮
   - 全部下载：点击"全部下载"按钮
   - 下载完成后 toast 提示路径，点击"打开文件夹"直接定位文件

## 技术栈

| 组件 | 技术 |
|------|------|
| 桌面客户端 | PyWebView |
| Web 服务 | FastAPI + Uvicorn |
| 数据存储 | SQLModel + SQLite |
| 数据抓取 | httpx + mwparserfromhell |
| 桌面打包 | Nuitka |
| CI/CD | GitHub Actions |

## 项目结构

```
├── core/
│   ├── models.py          # Character 数据模型
│   ├── database.py        # SQLite 引擎
│   ├── paths.py           # 路径解析（兼容 Nuitka 编译）
│   ├── search.py          # 搜索逻辑
│   └── prts/
│       └── x_search.py    # PRTS Wiki 数据抓取
├── server.py              # FastAPI 入口
├── ui.py                  # PyWebView 桌面入口
├── init_db.py             # 数据库初始化
├── export_training.py     # GPT-SoVITS 训练数据导出
├── build_nuitka.py        # Nuitka 打包脚本
├── frontend/
│   └── index.html         # 前端页面
└── .github/
    └── workflows/
        └── build.yml      # CI 自动构建 + 发布
```

## 开发

```bash
# 代码检查
ruff check .
ruff format .

# 初始化数据库
python init_db.py

# 仅启动 API 服务（浏览器访问 http://localhost:8000）
python server.py

# 打包为 exe
python build_nuitka.py
```

## API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/characters` | GET | 干员列表 |
| `/api/characters/{id}` | GET | 干员基础信息 |
| `/api/characters/{id}/detail` | GET | 干员详情（懒加载） |
| `/api/search?q=` | GET | 搜索干员 |
| `/api/download` | GET | 下载单个文件 |
| `/api/download/batch` | GET | 批量下载 |
| `/api/open-folder` | GET | 打开本地文件夹 |
| `/api/init-status` | GET | 初始化进度 |

## License

MIT
