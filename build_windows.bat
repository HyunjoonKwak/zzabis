@echo off
REM ZZABIS Windows 빌드 스크립트

echo ===================================
echo   ZZABIS Windows 빌드
echo ===================================

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM PyInstaller 설치
pip install pyinstaller

REM 빌드
pyinstaller --name "ZZABIS" ^
    --windowed ^
    --onefile ^
    --icon "icon.ico" ^
    --hidden-import "PyQt6" ^
    --hidden-import "pynput" ^
    --hidden-import "sounddevice" ^
    --hidden-import "numpy" ^
    --hidden-import "openai" ^
    main.py

echo.
echo 빌드 완료!
echo 결과물: dist\ZZABIS.exe
pause
