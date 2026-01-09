#!/bin/bash
# ZZABIS macOS 빌드 스크립트

echo "==================================="
echo "  ZZABIS macOS 빌드"
echo "==================================="

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# PyInstaller 설치
pip install pyinstaller

# 빌드
pyinstaller --name "ZZABIS" \
    --windowed \
    --onefile \
    --icon "icon.icns" \
    --add-data "*.py:." \
    --hidden-import "PyQt6" \
    --hidden-import "pynput" \
    --hidden-import "sounddevice" \
    --hidden-import "numpy" \
    --hidden-import "openai" \
    --osx-bundle-identifier "com.zzabis.app" \
    main.py

echo ""
echo "빌드 완료!"
echo "결과물: dist/ZZABIS.app"
