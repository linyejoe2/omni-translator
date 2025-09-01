# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# Get the project directory
project_dir = Path.cwd()

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        ('icon.png', '.'),
    ],
    hiddenimports=[
        'googletrans',
        'langdetect',
        'gtts',
        'pygame',
        'keyboard',
        'keyboard._winkeyboard',
        'keyboard._winmouse',
        'keyboard._generic',
        'keyboard._keyboard_event',
        'requests',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.messagebox',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='omni-translator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',  # Use the project icon
)