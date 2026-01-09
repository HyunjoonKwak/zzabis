#!/usr/bin/env python3
"""
MacVoice 권한 설정 도우미
마이크 및 손쉬운 사용 권한을 요청합니다.
"""

import subprocess
import sys

def request_microphone():
    """마이크 권한 요청"""
    print("마이크 권한 요청 중...")
    try:
        import sounddevice as sd
        # 짧은 녹음으로 권한 요청 트리거
        sd.rec(int(0.1 * 16000), samplerate=16000, channels=1)
        sd.wait()
        print("  → 마이크 권한 요청 완료!")
        print("  → 팝업이 나타나면 '허용'을 클릭하세요")
    except Exception as e:
        print(f"  → 마이크 접근 시도: {e}")

def open_accessibility_settings():
    """손쉬운 사용 설정 열기"""
    print("\n손쉬운 사용 설정 열기...")
    subprocess.run([
        'open',
        'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
    ])
    print("  → 시스템 설정이 열렸습니다")
    print("  → '터미널' 또는 사용 중인 앱을 찾아 체크하세요")

def open_microphone_settings():
    """마이크 설정 열기"""
    print("\n마이크 설정 열기...")
    subprocess.run([
        'open',
        'x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone'
    ])
    print("  → 마이크 권한 설정이 열렸습니다")

def main():
    print()
    print("=" * 50)
    print("  MacVoice 권한 설정 도우미")
    print("=" * 50)
    print()

    # 1. 마이크 권한 요청
    request_microphone()

    # 2. 설정 열기
    print("\n시스템 설정을 엽니다...")
    input("Enter를 눌러 계속...")

    open_microphone_settings()

    print("\n마이크 권한 설정 후 Enter를 누르세요...")
    input()

    open_accessibility_settings()

    print()
    print("=" * 50)
    print("  설정 완료 후 MacVoice를 실행하세요:")
    print("  python main.py")
    print("=" * 50)
    print()

if __name__ == "__main__":
    main()
