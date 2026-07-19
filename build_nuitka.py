import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def build(mode: str = "release"):
    build_dir = ROOT / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("已清理 build 目录")

    is_debug = mode == "debug"

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--enable-plugin=pywebview",
        f"--windows-console-mode={'force' if is_debug else 'disable'}",
        "--company-name=ACGN-Studio",
        "--product-name=ACGN-Studio",
        "--product-version=0.1.0",
        f"--output-dir={ROOT / 'build'}",
        "--output-filename=ACGN-Studio.exe",
        f"--windows-icon-from-ico={ROOT / 'assets' / 'prts.ico'}",
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
        # 排除非 Windows 平台和不兼容 Nuitka 的包
        "--nofollow-import-to=playwright",
        "--nofollow-import-to=meilisearch",
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        # 入口
        str(ROOT / "ui.py"),
    ]

    if is_debug:
        cmd.append("--debug")
    else:
        cmd.append("--python-flag=-O")

    db_path = ROOT / "data" / "app.db"
    if db_path.exists():
        cmd.insert(-1, f"--include-data-dir={ROOT / 'data'}=data")

    print(f"Building [{mode.upper()}] with Nuitka...")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "release"
    if mode not in ("debug", "release"):
        print(f"用法: python build_nuitka.py [debug|release]")
        sys.exit(1)
    build(mode)
