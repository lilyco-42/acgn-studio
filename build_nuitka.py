import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def build():
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--enable-plugin=pywebview",
        "--windows-console-mode=disable",
        "--company-name=ACGN-Studio",
        "--product-name=ACGN-Studio",
        "--product-version=0.1.0",
        f"--output-dir={ROOT / 'build'}",
        "--output-filename=ACGN-Studio.exe",
        "--assume-yes-for-downloads",
        "--include-windows-runtime-dlls=no",
        # 数据文件
        f"--include-data-dir={ROOT / 'frontend'}=frontend",
        # 隐式依赖（不含 webview，插件自动处理）
        "--include-package=sqlmodel",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=starlette",
        "--include-package=pydantic",
        "--include-package=httpx",
        "--include-package=mwparserfromhell",
        # 排除非 Windows 平台模块
        "--nofollow-import-to=webview.platforms.android",
        "--nofollow-import-to=webview.platforms.gtk",
        "--nofollow-import-to=webview.platforms.cocoa",
        "--nofollow-import-to=webview.platforms.qt",
        "--nofollow-import-to=playwright",
        "--nofollow-import-to=meilisearch",
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        # 入口
        str(ROOT / "ui.py"),
    ]

    db_path = ROOT / "data" / "app.db"
    if db_path.exists():
        cmd.insert(-1, f"--include-data-dir={ROOT / 'data'}=data")

    print("Building with Nuitka...")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build()
