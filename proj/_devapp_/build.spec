# -*- mode: python ; coding: utf-8 -*-

import os

filename = os.environ.get("PUBLISH_NAME", "파일명")
use_console = os.environ.get("USE_CONSOLE", "False").lower() in ("True", "true", "1")

# Analysis.datas

datalist_paddleocr = [
    ('D:/language/Python/Python310/lib/site-packages/paddleocr/tools', 'paddleocr/tools'),
    ('D:/language/Python/Python310/lib/site-packages/paddleocr/ppocr', 'paddleocr/ppocr'),
    ('D:/language/Python/Python310/lib/site-packages/paddleocr/ppstructure', 'paddleocr/ppstructure'),
]
datalist_scripts = [
    ('scripts', 'scripts'),
]

# Analysis.binaries
binarylist_lupa = [
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\lupa\\\\lua51.cp310-win_amd64.pyd', 'lupa'),
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\lupa\\\\lua52.cp310-win_amd64.pyd', 'lupa'),
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\lupa\\\\lua53.cp310-win_amd64.pyd', 'lupa'),
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\lupa\\\\lua54.cp310-win_amd64.pyd', 'lupa'),
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\lupa\\\\luajit20.cp310-win_amd64.pyd', 'lupa'),
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\lupa\\\\luajit21.cp310-win_amd64.pyd', 'lupa'),
]
dll_names_paddle = [
    "mkldnn.dll", "mkml.dll", "libomp5md.dll", "libgfortran-3.dll"
]
binarylist_paddle = [
    ('D:\\\\language\\\\Python\\\\Python310\\\\lib\\\\site-packages\\\\paddle\\\\libs\\\\' + name, 'paddle/libs')
    for name in dll_names_paddle
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binarylist_lupa + binarylist_paddle,
    datas=datalist_paddleocr,
    hiddenimports = [
        'shapely.geometry',
        'pyclipper',
        'imghdr',
        'skimage', 'skimage.morphology', 'skimage.morphology._skeletonize',
        'imgaug', 'imgaug.augmenters',
        'scipy.io', 'scipy.special', 'scipy.spatial',
        'lmdb',
        ],
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
