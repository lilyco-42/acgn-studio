import os
import sys
import threading
import traceback
from pathlib import Path


def _write_log(msg: str):
    """写日志到 exe 所在目录，方便调试。"""
    if getattr(sys, "frozen", False):
        log_path = Path(sys.executable).parent / "crash.log"
    else:
        log_path = Path(__file__).parent / "crash.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


try:
    from core.paths import BASE_DIR

    _write_log(f"[OK] BASE_DIR = {BASE_DIR}")
    os.chdir(BASE_DIR)
    _write_log(f"[OK] CWD = {os.getcwd()}")
except Exception as e:
    _write_log(f"[FAIL] import core.paths: {e}\n{traceback.format_exc()}")
    raise

try:
    import uvicorn

    _write_log("[OK] import uvicorn")
except Exception as e:
    _write_log(f"[FAIL] import uvicorn: {e}\n{traceback.format_exc()}")
    raise

try:
    import webview

    _write_log("[OK] import webview")
except Exception as e:
    _write_log(f"[FAIL] import webview: {e}\n{traceback.format_exc()}")
    raise


def run_server():
    try:
        _write_log("[OK] Starting uvicorn server...")
        uvicorn.run(
            "server:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info",
        )
    except Exception as e:
        _write_log(f"[FAIL] uvicorn: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    _write_log("[OK] ui.py __main__ start")
    threading.Thread(target=run_server, daemon=True).start()

    webview.create_window(
        "ACGN Studio", "http://127.0.0.1:8000", width=1000, height=700
    )
    _write_log("[OK] webview.create_window done, calling webview.start()")
    webview.start()
    _write_log("[OK] webview.start() returned")
