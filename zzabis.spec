# -*- mode: python ; coding: utf-8 -*-
# ZZABIS PyInstaller Spec File

import sys
import os

block_cipher = None

# 플랫폼별 설정
is_mac = sys.platform == 'darwin'
is_windows = sys.platform == 'win32'

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'sounddevice',
        'numpy',
        'openai',
        'pyperclip',
        'pyautogui',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if is_mac:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='ZZABIS',
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
    )
    app = BUNDLE(
        exe,
        name='ZZABIS.app',
        icon='icon.icns',
        bundle_identifier='com.zzabis.app',
        info_plist={
            'NSMicrophoneUsageDescription': '음성 인식을 위해 마이크 접근이 필요합니다.',
            'NSAppleEventsUsageDescription': '키보드 입력을 위해 접근성 권한이 필요합니다.',
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='ZZABIS',
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
        icon='icon.ico',
    )
