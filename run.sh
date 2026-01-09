#!/bin/bash
# ZZABIS 실행 스크립트

cd "$(dirname "$0")"

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 앱 실행
python main.py
