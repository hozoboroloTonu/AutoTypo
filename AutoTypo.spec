# -*- mode: python ; coding: utf-8 -*-

import os
import io
import struct
from pathlib import Path
from PIL import Image

block_cipher = None
base_dir = Path(os.path.abspath(SPECPATH))

# Ensure high-quality multi-layer Windows ICO (256, 128, 64, 48, 32, 24, 16) is generated
png_icon = base_dir / 'assets' / 'app_icon.png'
ico_icon = base_dir / 'assets' / 'app_icon.ico'
if png_icon.exists():
    try:
        base_img = Image.open(str(png_icon)).convert('RGBA')
        sizes = [256, 128, 64, 48, 32, 24, 16]
        png_data_list = []
        for s in sizes:
            resized = base_img.resize((s, s), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            resized.save(buf, format='PNG')
            png_data_list.append((s, buf.getvalue()))

        num_images = len(png_data_list)
        header = struct.pack('<HHH', 0, 1, num_images)
        offset = 6 + (16 * num_images)
        entries = bytearray()
        image_data_block = bytearray()

        for s, data in png_data_list:
            width = 0 if s == 256 else s
            height = 0 if s == 256 else s
            entry = struct.pack(
                '<BBBBHHII',
                width, height, 0, 0, 1, 32, len(data), offset + len(image_data_block)
            )
            entries.extend(entry)
            image_data_block.extend(data)

        full_ico = header + bytes(entries) + bytes(image_data_block)
        with open(str(ico_icon), 'wb') as f:
            f.write(full_ico)
    except Exception as e:
        print(f"Warning: Could not auto-generate multi-layer ICO: {e}")

added_files = [
    (str(base_dir / 'assets'), 'assets'),
]

hidden_imports = [
    'pynput',
    'pynput.keyboard',
    'pynput.mouse',
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'app',
    'app.core',
    'app.core.automation_engine',
    'app.core.keyboard_listener',
    'app.services',
    'app.services.app_state',
    'app.services.settings_manager',
    'app.services.logger',
    'app.services.session_manager',
    'app.services.config_manager',
    'app.services.notification_manager',
    'app.services.lifecycle_manager',
    'app.utils',
    'app.utils.constants',
    'app.utils.resources',
    'app.ui',
    'app.ui.styles',
    'app.ui.main_window',
    'app.ui.pages',
    'app.ui.pages.dashboard',
    'app.ui.pages.settings',
    'app.ui.pages.logs',
    'app.ui.pages.about',
    'app.ui.widgets',
    'app.ui.widgets.buttons',
    'app.ui.widgets.counters',
    'app.ui.widgets.dialogs',
    'app.ui.widgets.notifications',
    'app.ui.widgets.sidebar',
    'app.ui.widgets.title_bar',
]

a = Analysis(
    ['main.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'email', 'http', 'xmlrpc'],
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
    name='AutoTypo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(base_dir / 'assets' / 'app_icon.ico'),
    version=str(base_dir / 'version_info.txt') if (base_dir / 'version_info.txt').exists() else None,
)
