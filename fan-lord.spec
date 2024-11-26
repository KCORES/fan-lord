# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['supermicro-x-series.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('IPMICFG-Win.exe', '.'),  # 包含 IPMI 工具
        ('pmdll.dll', '.'),        # 包含 DLL 依赖
        ('fan-lord.ico', '.'),     # 添加图标文件
    ],
    hiddenimports=[],
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
    name='FanLord',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='fan-lord.ico',  # 如果你有图标的话
)
