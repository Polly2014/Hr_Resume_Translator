#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将 Streamlit 应用打包为独立可执行文件
支持 Windows (.exe) 和 macOS (.app)
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 正在安装 PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_launcher():
    """创建启动器脚本"""
    launcher_code = """#!/usr/bin/env python3
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
"""
    
    launcher_path = Path(__file__).parent / "launcher.py"
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_code)
    print(f"✅ 创建启动器: {launcher_path}")
    return launcher_path

def build():
    """执行打包"""
    project_dir = Path(__file__).parent
    
    # 安装 PyInstaller
    install_pyinstaller()
    
    # 创建启动器
    launcher_path = create_launcher()
    
    # 数据文件
    data_files = [
        (str(project_dir / "app.py"), "."),
        (str(project_dir / "resume_parser.py"), "."),
        (str(project_dir / "resume_template_generator.py"), "."),
        (str(project_dir / ".env"), "."),
        (str(project_dir / "Templates"), "Templates"),
    ]
    
    # 构建 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=简历解析助手",
        "--onedir",  # 使用文件夹模式，比单文件更稳定
        "--windowed",  # 无控制台窗口
        "--noconfirm",  # 覆盖已有文件
        "--clean",  # 清理缓存
    ]
    
    # 添加数据文件
    for src, dst in data_files:
        if os.path.exists(src):
            cmd.append(f"--add-data={src}{os.pathsep}{dst}")
    
    # 添加隐藏导入
    hidden_imports = [
        "streamlit",
        "streamlit.web.cli",
        "streamlit.runtime.scriptrunner",
        "altair",
        "pandas",
        "numpy",
        "openpyxl",
        "fitz",
        "docx",
        "litellm",
        "dotenv",
    ]
    
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")
    
    # 添加启动器
    cmd.append(str(launcher_path))
    
    print("\n🔨 开始打包...")
    print(f"命令: {' '.join(cmd)}\n")
    
    subprocess.check_call(cmd)
    
    print("\n" + "="*50)
    print("✅ 打包完成!")
    print(f"📁 输出目录: {project_dir / 'dist' / '简历解析助手'}")
    print("="*50)

if __name__ == "__main__":
    build()
