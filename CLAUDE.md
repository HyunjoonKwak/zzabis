# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZZABIS는 macOS/Windows용 AI 음성 타이핑 도우미 데스크탑 앱이다. 핫키를 누르고 말하면 OpenAI Whisper API로 음성인식 후 GPT-4o-mini로 스타일 변환하여 커서 위치에 자동 입력한다.

**스택:** Python 3.9+ / PyQt6 / OpenAI API (Whisper + GPT-4o-mini) / PyInstaller

## Commands

```bash
# 실행
python main.py

# macOS 빌드 (.app 번들 생성 → dist/ZZABIS.app)
chmod +x build_mac.sh && ./build_mac.sh

# Windows 빌드 (→ dist/ZZABIS.exe)
build_windows.bat

# 의존성 설치
pip install -r requirements.txt
```

테스트 프레임워크는 아직 없음.

## Architecture

### 핵심 흐름

```
핫키 입력 → 음성 녹음(sounddevice) → Whisper STT → GPT-4o-mini 스타일 변환 → 클립보드+자동입력(pyautogui)
```

### 모듈 구조

| 모듈 | 역할 |
|------|------|
| `main.py` | 앱 진입점, 녹음/핫키/스레드 오케스트레이션 |
| `ui.py` | PyQt6 UI (glassmorphism 디자인, VoiceOrb 애니메이션, 10개 스타일 버튼) |
| `ai_agent.py` | GPT-4o-mini 스타일 변환 (10가지 모드: 일반/격식/공손/캐주얼/귀여움/애교/로맨틱/차가움/유머/프로) |
| `speech_openai.py` | OpenAI Whisper API 래퍼 (numpy float32 → WAV → API) |
| `speech_gemini.py` | Gemini API 대체 음성인식 (현재 메인 플로우에 미사용) |
| `commands.py` | 50+ 음성 명령 실행기 (AppleScript macOS 제어, pyautogui 키보드/마우스) |
| `config.py` | JSON 설정 관리 (`~/.macvoice_config.json`) |
| `settings_dialog.py` | 설정 다이얼로그 UI (마이크/핫키/API키/디스플레이) |
| `database.py` | SQLite 명령 이력 (현재 미사용, 향후 분석용) |

### 스레딩 모델

- 핫키 감지: `pynput` 백그라운드 스레드
- 음성 녹음/처리: 워커 스레드
- UI 업데이트: Qt 시그널/슬롯으로 스레드 안전하게 전달 (`SignalEmitter`)

### 설정 파일

- `~/.macvoice_config.json` — API 키, 마이크, 핫키, 스타일 모드, 화면 인덱스
- API 키는 환경변수 폴백 지원 (`OPENAI_API_KEY`)
- 핫키 포맷: `{"type": "mouse", "button": "side"}` 또는 `{"type": "keyboard", "key": "space"}`

### 빌드 설정

- `zzabis.spec` — PyInstaller 설정 (windowed mode, macOS 번들 ID: `com.zzabis.app`)
- macOS 최소 버전: 10.15 (Catalina)
- Info.plist에 마이크/접근성 권한 포함

## Platform-Specific Notes

- **macOS:** 입력 모니터링 권한 필수 (접근성 아님), AppleScript로 시스템 제어
- **Windows:** pyaudio 사용, Python 3.9+ PATH 필요
- `commands.py`의 AppleScript 명령들은 macOS 전용
