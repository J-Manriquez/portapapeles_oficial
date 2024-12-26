# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],  # Actualiza la ruta al main.py
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),
        ('src/*.py', 'src'),  # Incluye todos los archivos Python
    ],
    hiddenimports=[
        'win32clipboard',
        'win32con',
        'win32gui',
        'win32com.client',
        'win32api',
        'keyboard',
        'pyautogui',
        'pyperclip',
        'bs4',
        'tkinter',
        'json',
        'threading',
        'pystray',
        'PIL'
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

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ClipboardManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    manifest='app.manifest'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClipboardManager',
)
