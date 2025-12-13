# -*- mode: python ; coding: utf-8 -*-
"""
◈ CYBER RESUME PARSER v1.0 ◈
PyInstaller 打包配置
"""

import os
import sys

block_cipher = None

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['desktop_app.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('Templates', 'Templates'),
        ('resume_parser.py', '.'),
        ('resume_template_generator.py', '.'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'webview',
        'openpyxl',
        'fitz',  # PyMuPDF
        'docx',
        'openai',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CyberResumeParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS 需要
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CyberResumeParser',
)

# macOS .app 打包
app = BUNDLE(
    coll,
    name='Cyber Resume Parser.app',
    icon='app_icon.icns',
    bundle_identifier='com.polly.cyberresumeparser',
    info_plist={
        'CFBundleName': 'Cyber Resume Parser',
        'CFBundleDisplayName': 'Cyber Resume Parser',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
