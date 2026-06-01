# -*- coding: utf-8 -*-
"""VLC Web 平台 - 一键启动"""

import sys, os, webbrowser, threading, time
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PROJECT_ROOT)

def main():
    print("=" * 55)
    print("  VLC 智能解调系统 - Web 平台 v3.0")
    print("=" * 55)
    print()
    print("  后端 API:     http://localhost:8000")
    print("  仪表盘:       http://localhost:8000/")
    print("  PPT 演示:     http://localhost:8000/slides")
    print("  API 文档:     http://localhost:8000/docs")
    print()
    print("  按 Ctrl+C 停止服务")
    print("=" * 55)

    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")

    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run("web.backend.app:app", host="0.0.0.0", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    main()
