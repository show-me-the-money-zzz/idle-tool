# -*- mode: python ; coding: utf-8 -*-

import os

filename = os.environ.get("PUBLISH_NAME", "파일명")
use_console = os.environ.get("USE_CONSOLE", "False").lower() in ("True", "true", "1")

datalist = [
    ('scripts', 'scripts')
]
binarylist = [
    ('C:\\\\Users\\\\ZV\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\lupa\\\\lua51.cp312-win_amd64.pyd', 'lupa'),
    ('C:\\\\Users\\\\ZV\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\lupa\\\\lua52.cp312-win_amd64.pyd', 'lupa'),
    ('C:\\\\Users\\\\ZV\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\lupa\\\\lua53.cp312-win_amd64.pyd', 'lupa'),
    ('C:\\\\Users\\\\ZV\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\lupa\\\\lua54.cp312-win_amd64.pyd', 'lupa'),
    ('C:\\\\Users\\\\ZV\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\lupa\\\\luajit20.cp312-win_amd64.pyd', 'lupa'),
    ('C:\\\\Users\\\\ZV\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python312\\\\Lib\\\\site-packages\\\\lupa\\\\luajit21.cp312-win_amd64.pyd', 'lupa')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binarylist,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=filename,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=use_console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=['zzz\\icon.ico'],
)
