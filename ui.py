import threading

import uvicorn
import webview


def run_server():

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    # 启动 FastAPI
    threading.Thread(target=run_server, daemon=True).start()

    # 打开窗口
    webview.create_window(
        "ACGN Studio", "http://127.0.0.1:8000", width=1000, height=700
    )

    webview.start()
