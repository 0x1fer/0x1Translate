# PyInstaller spec — Linux build (--onedir)
#
# Build:   pyinstaller build_linux.spec
# Output:  dist/TranslateApp/  (folder; entry exe is TranslateApp inside)
#
# This bundles Python, PyQt6, evdev, and pynput-free deps. System tools
# (wl-paste, xclip, xdotool) are NOT bundled — they're optional fallbacks
# that the app probes at runtime.
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("PyQt6")

# openpyxl is imported lazily inside words_tab._write_xlsx; PyInstaller's
# static analysis won't see it unless we declare it explicitly.
hiddenimports += ["openpyxl"]

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "PIL"],
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
    name="TranslateApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.png",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TranslateApp",
)
