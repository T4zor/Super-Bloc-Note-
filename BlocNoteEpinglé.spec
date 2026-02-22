# -*- mode: python ; coding: utf-8 -*-

import os

icon_file = os.path.join(os.path.dirname(__file__), "icon.ico")

a = Analysis(
    ['main.py'],
    pathex=[r"c:\\Users\\T4zor\\Documents\\ICT L2\\ICT-205\\Projet Bloc note"],
    binaries=[],
    datas=[('app image', 'app image'), ('nav', 'nav'), ('fonts', 'fonts'), ('icon.ico', '.')],
    hiddenimports=['PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
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
    name='BlocNoteEpinglé',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
