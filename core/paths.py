import sys
from pathlib import Path


def get_base_dir() -> Path:
    """获取基础目录：编译后为 exe 所在目录，开发时为项目根目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


BASE_DIR = get_base_dir()
