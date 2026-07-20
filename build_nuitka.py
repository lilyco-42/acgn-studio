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
        f"--windows-console-mode={'force' if is_debug else 'disable'}",
        "--company-name=ACGN-Studio",
        "--product-name=ACGN-Studio",
        "--product-version=0.1.0",
        f"--output-dir={ROOT / 'build'}",
        "--output-filename=ACGN-Studio.exe",
        f"--windows-icon-from-ico={ROOT / 'assets' / 'prts.ico'}",
        "--assume-yes-for-downloads",
        "--include-windows-runtime-dlls=yes",
        # 数据文件
        f"--include-data-dir={ROOT / 'frontend'}=frontend",
        f"--include-data-dir={ROOT / 'assets'}=assets",
        f"--include-data-dir={ROOT / 'sponsor' / 'assets'}=sponsor/assets",
        # 入口
        "--include-module=server",
        "--include-package=server",
        "--include-package=core",
        "--include-package=httpx",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=starlette",
        "--include-package=sqlmodel",
        "--include-package=sponsor",
        "--nofollow-import-to=playwright",
        "--nofollow-import-to=meilisearch",
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=pydantic.v1",
        str(ROOT / "ui.py"),
    ]

    db_path = ROOT / "data" / "app.db"
    if db_path.exists():
        cmd.insert(-1, f"--include-data-dir={ROOT / 'data'}=data")

    if not is_debug:
        cmd.append("--python-flag=-O")

    print(f"Building [{mode.upper()}] with Nuitka...")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "release"
    if mode not in ("debug", "release"):
        print(f"用法: python build_nuitka.py [debug|release]")
        sys.exit(1)
    build(mode)
