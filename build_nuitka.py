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
        # 数据文件
        f"--include-data-dir={ROOT / 'frontend'}=frontend",
        f"--include-data-dir={ROOT / 'data'}=data",
        # 隐式依赖
        "--include-package=sqlmodel",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=starlette",
        "--include-package=pydantic",
        "--include-package=httpx",
        "--include-package=mwparserfromhell",
        # 入口
        str(ROOT / "ui.py"),
    ]

    print("Building with Nuitka...")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build()
