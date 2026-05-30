# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=['D:\\App\\Razer'],
    binaries=[],
    datas=[
        ('presets', 'presets'),
        ('sdk_legacy_led_x64.dll', '.'),
    ],
    hiddenimports=[
        'pystray._win32',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas'],
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
    name='G515-RGB-by-Nabs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # pas de fenêtre console
    windowed=True,
    icon=None,              # on génère l'icône dynamiquement dans le code
)
