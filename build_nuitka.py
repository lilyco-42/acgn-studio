import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def build():
    # 清理上次构建缓存，避免残留文件冲突
    build_dir = ROOT / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("已清理 build 目录")

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--enable-plugin=pywebview",
        "--windows-console-mode=force",
        "--company-name=ACGN-Studio",
        "--product-name=ACGN-Studio",
        "--product-version=0.1.0",
        f"--output-dir={ROOT / 'build'}",
        "--output-filename=ACGN-Studio.exe",
        f"--windows-icon-from-ico={ROOT / 'assets' / 'icon.ico'}",
        "--assume-yes-for-downloads",
        "--include-windows-runtime-dlls=no",
        # 数据文件
        f"--include-data-dir={ROOT / 'frontend'}=frontend",
        f"--include-data-dir={ROOT / 'assets'}=assets",
        # 包含
        "--include-package=sqlmodel",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=starlette",
        "--include-package=pydantic",
        "--include-package=httpx",
        "--include-package=mwparserfromhell",
        "--include-package=pythonnet",
        "--include-module=server",
        "--include-package=core",
        # 排除非 Windows 平台
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
