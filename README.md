<p align="center">
  <img src="icon.png" alt="ZZABIS" width="120" />
</p>

<h1 align="center">ZZABIS</h1>
<p align="center"><strong>AI 음성 타이핑 도우미</strong></p>

<p align="center">
  핫키를 누르고 말하면, AI가 음성을 인식하고 원하는 말투로 변환하여 커서 위치에 자동 입력합니다.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey" alt="Platform" />
  <img src="https://img.shields.io/badge/UI-PyQt6-green?logo=qt" alt="PyQt6" />
  <img src="https://img.shields.io/badge/AI-OpenAI%20Whisper%20%2B%20GPT--4o--mini-orange?logo=openai" alt="OpenAI" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
</p>

---

## 주요 기능

- **음성 인식** - OpenAI Whisper API를 통한 정확한 한국어 음성 인식
- **10가지 말투 스타일 변환** - GPT-4o-mini를 활용한 실시간 말투 변환
- **자동 타이핑** - 변환된 텍스트를 현재 커서 위치에 자동 입력
- **맞춤법 교정** - AI 기반 자동 맞춤법/띄어쓰기 수정
- **Push-to-Talk** - 핫키를 누르고 있는 동안만 녹음
- **음성 명령** - 50개 이상의 macOS 시스템 제어 음성 명령 (앱 실행, 볼륨, 밝기, 창 관리 등)

## 스타일 모드

| 모드 | 설명 | 변환 예시 |
|:---:|------|------|
| **그대로** | 맞춤법만 수정 | 원본 유지 |
| **공적** | 격식체 존댓말 | ~습니다, ~합니다 |
| **정중** | 공손한 존댓말 | ~해요, ~세요 |
| **반말** | 친구끼리 반말 | ~야, ~어, ~지 |
| **귀엽게** | 귀여운 말투 | ~용, ~당, ~해용 |
| **애교** | 애교 섞인 말투 | ~잉, ~쪄, ~행 |
| **다정** | 따뜻한 말투 | ~해줄게, ~고 싶어 |
| **쿨하게** | 담담한 말투 | ~임, ㅇㅇ |
| **유머** | 재미있게 | 드립/재치 추가 |
| **비즈니스** | 전문가 말투 | ~드립니다, ~하겠습니다 |

---

## 설치

### 사전 준비

- **Python 3.9 이상**
- **OpenAI API 키** ([platform.openai.com](https://platform.openai.com)에서 발급, 결제 수단 등록 필요)
- **마이크**
- **인터넷 연결**

### macOS

```bash
# 1. Homebrew로 Python 설치 (없는 경우)
brew install python

# 2. 프로젝트 클론
git clone https://github.com/johunsang/zzabis.git
cd zzabis

# 3. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 실행
python main.py
```

### Windows

```batch
:: 1. https://www.python.org/downloads/ 에서 Python 설치
::    (설치 시 "Add Python to PATH" 반드시 체크!)

:: 2. 프로젝트 클론
git clone https://github.com/johunsang/zzabis.git
cd zzabis

:: 3. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate

:: 4. 의존성 설치
pip install -r requirements.txt

:: 5. 실행
python main.py
```

### 간편 설치 (macOS)

`install.command` 파일을 더블클릭하면 가상환경 생성과 패키지 설치를 자동으로 진행합니다. 설치 후 `ZZABIS.command`를 더블클릭하여 실행합니다.

> 처음 실행 시 API 키 입력창이 나타납니다. OpenAI API 키(`sk-`로 시작)를 입력하세요.

---

## 사용 방법

### 기본 사용법

1. `python main.py`로 앱 실행
2. 상단 스타일 버튼에서 원하는 말투 선택
3. **핫키를 누른 상태**로 말하기
4. 핫키를 떼면 자동으로 **음성 인식 → 스타일 변환 → 커서 위치에 입력**

### 핫키 설정

| 기본 핫키 | 변경 방법 |
|----------|----------|
| 마우스 사이드 버튼 | 설정(⚙) → "마우스 사이드" 또는 "키보드 설정" |

지원하는 핫키: 마우스 사이드/휠 버튼, F1~F12, 수정자 키 조합 (Ctrl+Alt+Z 등)

### 마이크 설정

설정(⚙) → 마이크 드롭다운에서 선택 (자동 저장)

### 음성 명령 (macOS)

핫키를 누르고 다음과 같이 말하면 시스템을 제어할 수 있습니다:

| 분류 | 명령어 예시 |
|------|-----------|
| 앱 실행 | "사파리 열어", "크롬 열어", "터미널 열어", "카카오톡 열어" |
| 볼륨 | "볼륨 올려", "볼륨 내려", "음소거", "소리 켜" |
| 밝기 | "밝기 올려", "밝기 내려" |
| 창 관리 | "창 최소화", "창 최대화", "풀스크린", "창 왼쪽", "창 닫아" |
| 마우스 | "클릭", "오른쪽 클릭", "더블 클릭", "스크롤 위로" |
| 탭 | "새 탭", "탭 닫아", "다음 탭", "이전 탭" |
| 미디어 | "재생", "일시정지", "다음 곡", "이전 곡" |
| 시스템 | "화면 잠금", "스크린샷", "잠자기" |
| 텍스트 | "엔터" (Enter 키 입력) |

> 명령어가 아닌 음성은 말투 변환 후 텍스트로 자동 입력됩니다.

---

## macOS 권한 설정 (필수)

핫키와 음성 인식이 작동하려면 **두 가지 권한**이 필요합니다.

### 1. 마이크 권한

시스템 설정 → 개인 정보 보호 및 보안 → **마이크** → 터미널(또는 사용 중인 터미널 앱) 체크

### 2. 입력 모니터링 권한

시스템 설정 → 개인 정보 보호 및 보안 → **입력 모니터링** → + 버튼으로 추가:

| 실행 방법 | 권한 부여 대상 |
|-----------|-------------|
| 터미널에서 `python main.py` | 터미널.app |
| `ZZABIS.command` 더블클릭 | 터미널.app |
| `ZZABIS.app` 빌드 후 실행 | ZZABIS.app |

> **"접근성"이 아닌 "입력 모니터링" 권한**이 필요합니다.
>
> 권한 변경 후 **터미널/앱을 완전히 종료하고 다시 열어야** 적용됩니다.

---

## 빌드 (배포용 실행 파일)

### macOS (.app)

```bash
chmod +x build_mac.sh
./build_mac.sh
# 결과: dist/ZZABIS.app
```

### Windows (.exe)

```batch
build_windows.bat
# 결과: dist/ZZABIS.exe
```

### PyInstaller 직접 사용

```bash
pip install pyinstaller
pyinstaller zzabis.spec
```

---

## 아키텍처

```
핫키 입력 (pynput)
    │
    ▼
음성 녹음 (sounddevice, 16kHz mono float32)
    │
    ▼
OpenAI Whisper API (speech_openai.py)
    │  음성 → 텍스트
    ▼
명령어 판별 (commands.py)
    │
    ├─ 명령어 → AppleScript / pyautogui 실행
    │
    └─ 일반 텍스트 → GPT-4o-mini 스타일 변환 (ai_agent.py)
                        │
                        ▼
                  클립보드 + Cmd+V 자동 입력 + Enter
```

### 모듈 구조

| 파일 | 역할 |
|------|------|
| `main.py` | 앱 진입점, 녹음/핫키/스레드 오케스트레이션 |
| `ui.py` | PyQt6 UI (glassmorphism, VoiceOrb 애니메이션, 스타일 버튼) |
| `ai_agent.py` | GPT-4o-mini 스타일 변환 (10가지 모드) |
| `speech_openai.py` | OpenAI Whisper API 래퍼 |
| `speech_gemini.py` | Gemini API 음성인식 (대체 엔진) |
| `commands.py` | 50+ 음성 명령 실행기 (AppleScript, pyautogui) |
| `config.py` | JSON 설정 관리 (`~/.macvoice_config.json`) |
| `settings_dialog.py` | 설정 다이얼로그 UI |
| `database.py` | SQLite 명령 이력 (향후 분석용) |
| `macvoice.py` | 레거시 연속 음성 인식 모드 (로컬 Whisper) |

---

## 자주 묻는 질문

### "API 키가 올바르지 않습니다" 오류
- API 키가 `sk-`로 시작하는지 확인
- OpenAI 계정에 **결제 수단이 등록**되어 있는지 확인
- 설정(⚙) → API 키 재입력

### 핫키가 작동하지 않아요
- macOS: **입력 모니터링** 권한 확인 ("접근성"이 아님!)
- 권한 추가 후 **터미널 완전 종료 → 재시작**
- 다른 앱과 핫키 충돌 여부 확인 → 설정에서 다른 핫키로 변경

### 음성이 인식되지 않아요
- 마이크 권한 확인
- 설정에서 올바른 마이크 장치 선택
- 핫키를 **충분히 길게** 누르고 말하기 (최소 0.3초)

### 한글이 깨져서 입력돼요
- 한글 입력기(한국어 키보드)가 활성화된 상태인지 확인
- 입력 대상 앱이 한글 입력을 지원하는지 확인

---

## 시스템 요구사항

- macOS 10.15 (Catalina) 이상 또는 Windows 10 이상
- Python 3.9~3.12
- 인터넷 연결 (OpenAI API)
- 마이크

## 라이선스

MIT License
