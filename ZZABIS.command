#!/bin/bash
# ZZABIS 실행 스크립트
# 더블클릭으로 실행하세요

cd "$(dirname "$0")"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "가상환경이 없습니다. install.command를 먼저 실행해주세요."
    read -p "아무 키나 눌러 종료하세요..."
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# 실행
python main.py
