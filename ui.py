import os
import random
import socket
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


def find_available_port(default: int = 8000) -> int:
    """检测默认端口是否可用，不可用则随机 8000-8999"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", default))
            return default
    except OSError:
        port = random.randint(8000, 8999)
        while port == default:
            port = random.randint(8000, 8999)
        _write_log(f"[Port] 端口 {default} 被占用，随机使用 {port}")
        return port


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


SERVER_PORT = find_available_port()


def run_server():
    try:
        from server import app as server_app
        _write_log("[OK] Starting uvicorn server...")
        uvicorn.run(
            server_app,
            host="127.0.0.1",
            port=SERVER_PORT,
            reload=False,
            log_level="info",
        )
    except Exception as e:
        _write_log(f"[FAIL] uvicorn: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    _write_log("[OK] ui.py __main__ start")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    import time
    time.sleep(2)

    webview.create_window(
        "ACGN Studio",
        f"http://127.0.0.1:{SERVER_PORT}",
        width=1000,
        height=700,
    )
    _write_log("[OK] webview.create_window done, calling webview.start()")
    webview.start()
    _write_log("[OK] webview.start() returned")
