#!/bin/bash
# ZZABIS 설치 스크립트
# 더블클릭으로 실행하세요

cd "$(dirname "$0")"

echo "=================================================="
echo "  ZZABIS - AI 음성 비서 설치"
echo "=================================================="
echo ""

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "Python 3이 설치되어 있지 않습니다."
    echo "https://www.python.org/downloads/ 에서 Python을 설치해주세요."
    echo ""
    read -p "아무 키나 눌러 종료하세요..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "Python 버전: $PYTHON_VERSION"

# 가상환경 생성
if [ ! -d "venv" ]; then
    echo ""
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo ""
echo "가상환경 활성화..."
source venv/bin/activate

# 의존성 설치
echo ""
echo "필요한 패키지 설치 중... (시간이 좀 걸릴 수 있습니다)"
pip install --upgrade pip > /dev/null 2>&1

# requirements.txt 업데이트 확인 및 설치
pip install PyQt6 pynput pyaudio numpy openai google-genai sounddevice SpeechRecognition openai-whisper

echo ""
echo "=================================================="
echo "  설치 완료!"
echo "=================================================="
echo ""
echo "사용 방법:"
echo "1. ZZABIS.command 를 더블클릭하여 실행"
echo "2. 설정에서 API 키 입력 (Gemini/OpenAI)"
echo "3. 핫키를 누르고 말하세요!"
echo ""
echo "처음 실행 시 마이크 권한과 접근성 권한이 필요합니다."
echo ""
read -p "아무 키나 눌러 종료하세요..."
