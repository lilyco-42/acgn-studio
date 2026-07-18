import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def build():
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--enable-plugin=pywebview",
        "--windows-console-mode=disable",
        "--company-name=ACGN-Studio",
        "--product-name=ACGN-Studio",
        "--product-version=0.1.0",
        f"--output-dir={ROOT / 'build'}",
        f"--output-filename=ACGN-Studio.exe",
        # 自动下载依赖工具，CI 无需交互
        "--assume-yes-for-downloads",
        # 不包含 Windows Runtime DLLs（减小体积）
        "--include-windows-runtime-dlls=no",
        # 数据文件
        f"--include-data-dir={ROOT / 'frontend'}=frontend",
        # 隐式依赖
        "--include-package=sqlmodel",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=starlette",
        "--include-package=pydantic",
        "--include-package=httpx",
        "--include-package=mwparserfromhell",
        "--include-package=webview",
        # 排除不需要的平台模块
        "--nofollow-import-to=webview.platforms.android",
        "--nofollow-import-to=webview.platforms.gtk",
        "--nofollow-import-to=webview.platforms.cocoa",
        "--nofollow-import-to=playwright",
        "--nofollow-import-to=meilisearch",
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        # 入口
        str(ROOT / "ui.py"),
    ]

    # data/app.db 可能不存在（CI 环境），单独处理
    db_path = ROOT / "data" / "app.db"
    if db_path.exists():
        cmd.insert(-1, f"--include-data-dir={ROOT / 'data'}=data")

    print("Building with Nuitka...")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build()
