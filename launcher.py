#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import webbrowser
import time
import socket
from pathlib import Path

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def main():
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys._MEIPASS)
    else:
        app_dir = Path(__file__).parent
    
    os.chdir(app_dir)
    port = find_free_port()
    
    print(f"正在启动简历解析助手...")
    print(f"端口: {port}")
    
    import streamlit.web.cli as stcli
    
    def open_browser():
        time.sleep(2)
        webbrowser.open(f"http://localhost:{port}")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    sys.argv = [
        "streamlit", "run",
        str(app_dir / "app.py"),
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false"
    ]
    stcli.main()

if __name__ == "__main__":
    main()
