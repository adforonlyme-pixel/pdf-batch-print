# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包設定檔
# 使用方式：pyinstaller auto_print_pdf.spec

block_cipher = None

a = Analysis(
    ['auto_print_pdf.py'],
    pathex=[],
    binaries=[],
    # 將 SumatraPDF.exe 一起打包進去，使用者只需單一 .exe 即可執行
    datas=[('SumatraPDF.exe', '.')],
    hiddenimports=['win32print', 'win32api'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pdf-batch-print',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # onefile 模式：所有資源打包成單一執行檔
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # 若有 icon 檔可取消註解
)
