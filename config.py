"""
MacVoice 설정 파일
"""

import os
import json

CONFIG_FILE = os.path.expanduser("~/.macvoice_config.json")

def load_config():
    """설정 파일 로드"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """설정 파일 저장"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_api_key():
    """Gemini API 키 가져오기"""
    # 환경변수 먼저 확인
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # 설정 파일에서 확인
    config = load_config()
    return config.get("gemini_api_key")


def get_openai_api_key():
    """OpenAI API 키 가져오기"""
    # 환경변수 먼저 확인
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # 설정 파일에서 확인
    config = load_config()
    return config.get("openai_api_key")


def set_openai_api_key(key):
    """OpenAI API 키 저장"""
    config = load_config()
    config["openai_api_key"] = key
    save_config(config)
    print("OpenAI API 키가 저장되었습니다.")

def set_api_key(key):
    """Gemini API 키 저장"""
    config = load_config()
    config["gemini_api_key"] = key
    save_config(config)
    print("✅ API 키가 저장되었습니다.")


def get_microphone():
    """마이크 장치 인덱스 가져오기"""
    config = load_config()
    return config.get("microphone_device")  # None이면 기본 장치 사용


def set_microphone(device_index):
    """마이크 장치 설정"""
    config = load_config()
    config["microphone_device"] = device_index
    save_config(config)


def get_screen():
    """UI 표시 화면 인덱스 가져오기"""
    config = load_config()
    return config.get("screen_index", 0)  # 기본값 0 (주 모니터)


def set_screen(screen_index):
    """UI 표시 화면 설정"""
    config = load_config()
    config["screen_index"] = screen_index
    save_config(config)


def get_hotkey():
    """녹음 트리거 핫키 가져오기"""
    config = load_config()
    # 기본값: 마우스 사이드 버튼
    return config.get("hotkey", {"type": "mouse", "button": "side"})


def set_hotkey(hotkey_config):
    """녹음 트리거 핫키 설정

    hotkey_config 형식:
    - {"type": "mouse", "button": "side"}  # 마우스 사이드 버튼
    - {"type": "mouse", "button": "middle"}  # 마우스 휠 버튼
    - {"type": "keyboard", "key": "f5"}  # F5 키
    - {"type": "keyboard", "key": "space"}  # 스페이스바
    """
    config = load_config()
    config["hotkey"] = hotkey_config
    save_config(config)


# 스타일 모드 정의
STYLE_MODES = {
    "normal": "그대로",
    "formal": "공적",
    "polite": "정중",
    "casual": "반말",
    "cute": "귀엽게",
    "aegyo": "애교",
    "romantic": "다정",
    "cold": "쿨하게",
    "humor": "유머",
    "pro": "비즈니스",
}


def get_style_mode():
    """스타일 모드 가져오기"""
    config = load_config()
    return config.get("style_mode", "normal")  # 기본값: 그대로


def set_style_mode(mode: str):
    """스타일 모드 설정"""
    config = load_config()
    config["style_mode"] = mode
    save_config(config)


def setup_api_key():
    """API 키 설정 (대화형)"""
    print()
    print("=" * 50)
    print("  Google Gemini API 키 설정")
    print("=" * 50)
    print()
    print("API 키를 입력하세요 (https://aistudio.google.com/apikey)")
    print()
    key = input("API Key: ").strip()

    if key.startswith("AI"):
        set_api_key(key)
        return key
    else:
        print("❌ 올바른 API 키 형식이 아닙니다. (AI로 시작해야 함)")
        return None


# Whisper 설정
WHISPER_MODEL = "turbo"  # tiny, base, small, medium, large, turbo

# 언어 설정
LANGUAGE = "ko"  # ko, en, ja, zh, etc.

# 음성 감지 설정
SILENCE_THRESHOLD = 0.008
SILENCE_DURATION = 1.0
MIN_AUDIO_LENGTH = 0.3
SAMPLE_RATE = 16000
