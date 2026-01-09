#!/usr/bin/env python3
"""
ZZABIS - AI 음성 비서
Gemini + Whisper + 멋진 UI
스페이스바 Push-to-Talk
"""

import sys
import threading
import time
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt6.QtCore import Qt
from pynput import keyboard, mouse

from ui import MacVoiceUI
from ai_agent import AIAgent
from commands import CommandExecutor
from config import get_microphone, get_openai_api_key, set_openai_api_key, get_hotkey, get_style_mode
from settings_dialog import SettingsDialog
from speech_openai import OpenAISpeechRecognizer


class APIKeyDialog(QDialog):
    """API 키 입력 다이얼로그 - Gemini + OpenAI"""

    def __init__(self, key_type="gemini"):
        super().__init__()
        self.key_type = key_type
        title = "GEMINI API KEY" if key_type == "gemini" else "OPENAI API KEY"
        url = "https://aistudio.google.com/apikey" if key_type == "gemini" else "https://platform.openai.com/api-keys"
        placeholder = "AIza..." if key_type == "gemini" else "sk-..."

        self.setWindowTitle(f"ZZABIS - {title}")
        self.setFixedSize(480, 240)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 배경 프레임
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 20, 40, 245),
                    stop:1 rgba(5, 10, 25, 250));
                border-radius: 20px;
                border: 1px solid rgba(0, 200, 180, 100);
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(18)
        layout.setContentsMargins(35, 30, 35, 30)

        # 안내 텍스트
        label = QLabel(title)
        label.setStyleSheet("""
            color: rgba(0, 255, 200, 240);
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 3px;
        """)
        layout.addWidget(label)

        sub_label = QLabel(f"{url} 에서 발급받으세요")
        sub_label.setStyleSheet("font-size: 12px; color: rgba(150, 200, 255, 180);")
        layout.addWidget(sub_label)

        # 입력 필드
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                font-size: 14px;
                background: rgba(0, 0, 0, 40);
                border: 1px solid rgba(0, 200, 180, 80);
                border-radius: 10px;
                color: rgba(255, 255, 255, 220);
            }
            QLineEdit:focus {
                border-color: rgba(0, 255, 200, 150);
            }
        """)
        layout.addWidget(self.input)

        # 버튼 영역
        btn_layout = QHBoxLayout()

        # 취소 버튼
        cancel_btn = QPushButton("취소")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 120, 100);
                color: rgba(255, 255, 255, 180);
                padding: 12px 30px;
                font-size: 13px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 140, 150);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()

        # 확인 버튼
        btn = QPushButton("확인")
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 180, 160, 200),
                    stop:1 rgba(0, 200, 180, 200));
                color: white;
                padding: 12px 40px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 200, 180, 220),
                    stop:1 rgba(0, 220, 200, 220));
            }
        """)
        btn.clicked.connect(self.save_key)
        btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)
        main_layout.addWidget(frame)

    def save_key(self):
        key = self.input.text().strip()
        if len(key) > 10:
            if self.key_type == "gemini":
                set_api_key(key)
            else:
                set_openai_api_key(key)
            self.accept()
        else:
            QMessageBox.warning(self, "오류", "올바른 API 키를 입력해주세요.")


def check_api_keys():
    """API 키 확인 및 입력 요청 (OpenAI만 필요)"""
    # OpenAI API 키 확인 (음성인식 + 스타일 변환용)
    if not get_openai_api_key():
        dialog = APIKeyDialog("openai")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False

    return True

# 설정
SAMPLE_RATE = 16000
MIN_AUDIO_LENGTH = 0.3


class ZzabisApp:
    """메인 앱 - Push-to-Talk 타이핑 전용"""

    def __init__(self, ui: MacVoiceUI):
        self.ui = ui
        self.ai = AIAgent()
        self.commands = CommandExecutor()
        self.settings_dialog = None

        self.audio_buffer = []
        self.is_recording = False
        self.processing = False
        self.running = True
        self.language = "ko"
        self.listening_start = None
        self.current_style = get_style_mode()
        self.openai_stt = None
        self.mic_device = get_microphone()

        # 핫키 설정 로드
        self.hotkey_config = get_hotkey()
        self.mouse_listener = None
        self.keyboard_listener = None
        self.pressed_modifiers = set()

        # 스타일 변경 시그널 연결
        self.ui.signals.style_changed.connect(self.on_style_changed)

        # 설정 버튼 연결
        self.ui.settings_btn.mousePressEvent = lambda e: self.open_settings()

        # UI 업데이트
        self.ui.signals.update_status.emit("초기화 중...")
        self.ui.signals.update_response.emit("초기화 중...")

        # 백그라운드에서 초기화
        threading.Thread(target=self.load_model, daemon=True).start()

        # 핫키 리스너 시작
        self._start_hotkey_listener()

    def _start_hotkey_listener(self):
        """핫키 리스너 시작"""
        hotkey_type = self.hotkey_config.get("type", "mouse")

        if hotkey_type == "mouse":
            # 마우스 버튼 리스너
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()
            print(f"마우스 핫키 리스너 시작: {self.hotkey_config.get('button', 'side')}")
        else:
            # 키보드 리스너
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.keyboard_listener.start()
            print(f"키보드 핫키 리스너 시작: {self.hotkey_config.get('key', 'space')}")

    def _get_hotkey_name(self) -> str:
        """현재 핫키 이름 반환"""
        hotkey_type = self.hotkey_config.get("type", "mouse")
        if hotkey_type == "mouse":
            button = self.hotkey_config.get("button", "side")
            if button == "side":
                return "마우스 사이드 버튼"
            elif button == "middle":
                return "마우스 휠 버튼"
            return f"마우스 {button}"
        else:
            key = self.hotkey_config.get("key", "space")
            modifiers = self.hotkey_config.get("modifiers", [])

            key_names = {
                "space": "Space",
                "ctrl": "Ctrl",
                "alt": "Alt",
                "shift": "Shift",
                "cmd": "Cmd",
                "enter": "Enter",
                "tab": "Tab",
                "esc": "Esc",
            }

            # 키 이름 변환
            if key.startswith("f") and key[1:].isdigit():
                key_display = key.upper()
            else:
                key_display = key_names.get(key, key.upper())

            # 수정자 조합
            if modifiers:
                mod_display = "+".join([m.capitalize() for m in modifiers])
                return f"{mod_display}+{key_display}"
            return key_display
        return "핫키"

    def _is_target_mouse_button(self, button) -> bool:
        """설정된 마우스 버튼인지 확인"""
        target_button = self.hotkey_config.get("button", "side")

        if target_button == "side":
            # 사이드 버튼 감지 (플랫폼별로 다를 수 있음)
            button_str = str(button)
            is_side = button_str in ['Button.x1', 'Button.x2', 'Button.button8', 'Button.button9']

            # button8, button9 속성이 있는 경우 확인
            try:
                is_side = is_side or button == mouse.Button.button8 or button == mouse.Button.button9
            except AttributeError:
                pass

            return is_side
        elif target_button == "middle":
            return button == mouse.Button.middle

        return False

    def _is_target_key(self, key) -> bool:
        """설정된 키보드 키인지 확인"""
        target_key = self.hotkey_config.get("key", "space")

        # 키 매핑
        key_mapping = {
            "space": keyboard.Key.space,
            "f1": keyboard.Key.f1,
            "f2": keyboard.Key.f2,
            "f3": keyboard.Key.f3,
            "f4": keyboard.Key.f4,
            "f5": keyboard.Key.f5,
            "f6": keyboard.Key.f6,
            "f7": keyboard.Key.f7,
            "f8": keyboard.Key.f8,
            "f9": keyboard.Key.f9,
            "f10": keyboard.Key.f10,
            "f11": keyboard.Key.f11,
            "f12": keyboard.Key.f12,
            "ctrl": keyboard.Key.ctrl_l,
            "ctrl_l": keyboard.Key.ctrl_l,
            "ctrl_r": keyboard.Key.ctrl_r,
            "alt": keyboard.Key.alt_l,
            "alt_l": keyboard.Key.alt_l,
            "alt_r": keyboard.Key.alt_r,
            "shift": keyboard.Key.shift_l,
            "shift_l": keyboard.Key.shift_l,
            "shift_r": keyboard.Key.shift_r,
            "cmd": keyboard.Key.cmd_l,
            "cmd_l": keyboard.Key.cmd_l,
            "cmd_r": keyboard.Key.cmd_r,
            "enter": keyboard.Key.enter,
            "tab": keyboard.Key.tab,
            "esc": keyboard.Key.esc,
            "backspace": keyboard.Key.backspace,
        }

        expected_key = key_mapping.get(target_key)

        if expected_key is not None:
            # 특수 키 매핑에 있는 경우
            if key == expected_key:
                return True
            # ctrl_l과 ctrl_r 모두 ctrl로 처리
            if target_key in ["ctrl", "alt", "shift", "cmd"]:
                alt_keys = {
                    "ctrl": [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r],
                    "alt": [keyboard.Key.alt_l, keyboard.Key.alt_r],
                    "shift": [keyboard.Key.shift_l, keyboard.Key.shift_r],
                    "cmd": [keyboard.Key.cmd_l, keyboard.Key.cmd_r],
                }
                return key in alt_keys.get(target_key, [])
            return False

        # 일반 문자 키 (a-z, 0-9 등) 처리
        try:
            if hasattr(key, 'char') and key.char:
                # 직접 비교
                if key.char.lower() == target_key.lower():
                    return True

            # vk 코드로 확인 (Alt가 눌려있으면 특수문자로 변환됨)
            if hasattr(key, 'vk') and key.vk is not None:
                # macOS에서 z의 vk 코드는 6 (kVK_ANSI_Z)
                vk_map = {
                    'z': 6, 'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 5,
                    'h': 4, 'j': 38, 'k': 40, 'l': 37, 'q': 12, 'w': 13,
                    'e': 14, 'r': 15, 't': 17, 'y': 16, 'u': 32, 'i': 34,
                    'o': 31, 'p': 35, 'x': 7, 'c': 8, 'v': 9, 'b': 11,
                    'n': 45, 'm': 46
                }
                if len(target_key) == 1 and target_key.lower() in vk_map:
                    if key.vk == vk_map[target_key.lower()]:
                        return True
        except Exception as e:
            print(f"[DEBUG] key check error: {e}")

        return False

    def _track_modifier(self, key, pressed: bool):
        """수정자 키 추적"""
        modifier_map = {
            keyboard.Key.ctrl_l: "ctrl",
            keyboard.Key.ctrl_r: "ctrl",
            keyboard.Key.alt_l: "alt",
            keyboard.Key.alt_r: "alt",
            keyboard.Key.shift_l: "shift",
            keyboard.Key.shift_r: "shift",
            keyboard.Key.cmd_l: "cmd",
            keyboard.Key.cmd_r: "cmd",
        }
        mod = modifier_map.get(key)
        if mod:
            if pressed:
                self.pressed_modifiers.add(mod)
            else:
                self.pressed_modifiers.discard(mod)

    def _check_modifiers(self) -> bool:
        """현재 수정자 조합이 설정과 일치하는지 확인"""
        required_modifiers = set(self.hotkey_config.get("modifiers", []))
        pressed = self.pressed_modifiers.copy()

        # macOS에서 cmd와 ctrl을 동일하게 처리
        if "ctrl" in required_modifiers and "cmd" in pressed:
            pressed.discard("cmd")
            pressed.add("ctrl")
        if "cmd" in required_modifiers and "ctrl" in pressed:
            pressed.discard("ctrl")
            pressed.add("cmd")

        return pressed == required_modifiers

    def on_key_press(self, key):
        """키보드 키 누름 - 녹음 시작"""
        # 수정자 키 추적
        self._track_modifier(key, True)

        # 타겟 키인지 확인
        if not self._is_target_key(key):
            return

        # 수정자 조합 확인
        if not self._check_modifiers():
            return

        if self.processing:
            return

        if self.openai_stt is None:
            self.ui.signals.update_status.emit("초기화 중... 잠시만 기다려주세요")
            return

        if not self.is_recording:
            self.is_recording = True
            self.audio_buffer = []
            self.listening_start = time.time()
            self.ui.signals.set_listening.emit(True)
            self.ui.signals.update_text.emit("")
            self.ui.signals.update_status.emit("녹음 중... (키 떼면 인식)")
            print(f"녹음 시작! ({self._get_hotkey_name()})")

    def on_key_release(self, key):
        """키보드 키 뗌 - 녹음 종료"""
        # 수정자 키 추적
        self._track_modifier(key, False)

        if not self._is_target_key(key):
            return

        if self.is_recording and not self.processing:
            self.is_recording = False
            print(f"녹음 종료! ({self._get_hotkey_name()})")
            self._process_recorded_audio()

    def on_mouse_click(self, x, y, button, pressed):
        """마우스 버튼 - 녹음"""
        if not self._is_target_mouse_button(button):
            return

        if self.processing:
            return

        if self.openai_stt is None:
            self.ui.signals.update_status.emit("초기화 중... 잠시만 기다려주세요")
            return

        if pressed:
            # 버튼 누름 - 녹음 시작
            if not self.is_recording:
                self.is_recording = True
                self.audio_buffer = []
                self.listening_start = time.time()
                self.ui.signals.set_listening.emit(True)
                self.ui.signals.update_text.emit("")
                self.ui.signals.update_status.emit("녹음 중... (버튼 떼면 인식)")
                print(f"녹음 시작! ({self._get_hotkey_name()})")
        else:
            # 버튼 뗌 - 녹음 종료
            if self.is_recording and not self.processing:
                self.is_recording = False
                print(f"녹음 종료! ({self._get_hotkey_name()})")
                self._process_recorded_audio()

    def _process_recorded_audio(self):
        """녹음된 오디오 처리"""
        if len(self.audio_buffer) > 0:
            total_samples = sum(len(c) for c in self.audio_buffer)
            audio_length = total_samples / SAMPLE_RATE

            if audio_length >= MIN_AUDIO_LENGTH:
                print(f"음성 길이: {audio_length:.2f}초")
                audio_data = self.audio_buffer.copy()
                self.audio_buffer = []
                threading.Thread(
                    target=self.process_audio,
                    args=(audio_data,),
                    daemon=True
                ).start()
            else:
                print(f"녹음이 너무 짧음: {audio_length:.2f}초")
                self.audio_buffer = []
                self.ui.signals.set_listening.emit(False)
                self.ui.signals.update_status.emit(f"{self._get_hotkey_name()} 길게 누르세요")
        else:
            self.ui.signals.set_listening.emit(False)
            self.ui.signals.update_status.emit(f"{self._get_hotkey_name()}으로 녹음")

    def on_style_changed(self, style_code: str):
        """스타일 모드 변경 처리"""
        from config import STYLE_MODES
        self.current_style = style_code
        style_name = STYLE_MODES.get(style_code, style_code)
        print(f"스타일 변경: {style_name}")
        self.ui.signals.update_console.emit(f"스타일: {style_name}")

    def load_model(self):
        """OpenAI Whisper API 초기화"""
        try:
            print("OpenAI Whisper 음성 인식 초기화 중...")
            self.openai_stt = OpenAISpeechRecognizer()
            print("OpenAI Whisper 준비 완료!")

            hotkey_name = self._get_hotkey_name()
            self.ui.signals.update_status.emit(f"{hotkey_name}으로 녹음")
            self.ui.signals.update_response.emit("준비 완료!")
            self.ui.signals.set_listening.emit(False)

            # 오디오 스트림 시작
            self.start_audio()
        except Exception as e:
            print(f"초기화 실패: {e}")
            self.ui.signals.update_status.emit(f"오류: {e}")

    def start_audio(self):
        """오디오 스트림 시작 - Push-to-Talk"""
        def audio_thread():
            print("오디오 스트림 시작...")
            try:
                # 마이크 장치 설정
                device = self.mic_device
                print(f"마이크 장치: {device if device else '시스템 기본'}")

                with sd.InputStream(
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype=np.float32,
                    callback=self.audio_callback,
                    blocksize=int(SAMPLE_RATE * 0.1),
                    device=device
                ):
                    print("오디오 스트림 준비 완료!")
                    while self.running:
                        time.sleep(0.1)
            except Exception as e:
                print(f"오디오 오류: {e}")
                self.ui.signals.update_status.emit(f"마이크 오류: {e}")

        threading.Thread(target=audio_thread, daemon=True).start()

    def get_audio_level(self, chunk):
        return np.sqrt(np.mean(chunk ** 2))

    def audio_callback(self, indata, frames, time_info, status):
        """오디오 콜백 - 스페이스 누르고 있을 때만 녹음"""
        chunk = indata.copy().flatten()
        level = self.get_audio_level(chunk)

        # UI에 레벨 전달
        self.ui.signals.update_level.emit(level)

        # 스페이스 누르고 있을 때만 버퍼에 추가
        if self.is_recording and not self.processing:
            self.audio_buffer.append(chunk)

            # 실시간 녹음 시간 표시
            if self.listening_start:
                elapsed = time.time() - self.listening_start
                self.ui.signals.update_status.emit(f"녹음 중... {elapsed:.1f}초")

    def process_audio(self, audio_chunks):
        """음성 처리 - 타이핑 전용"""
        self.processing = True
        self.ui.signals.set_processing.emit(True)
        self.ui.signals.update_status.emit("인식 중...")

        try:
            # 오디오 데이터 준비
            audio = np.concatenate(audio_chunks)

            # OpenAI Whisper 음성 인식
            print("OpenAI Whisper 음성 인식 중...")
            text = self.openai_stt.transcribe(audio, SAMPLE_RATE, self.language)

            print(f"인식 결과: {text}")

            if not text:
                self.ui.signals.update_status.emit(f"{self._get_hotkey_name()}으로 녹음")
                self.ui.signals.set_listening.emit(False)
                return

            # UI에 인식된 텍스트 표시
            self.ui.signals.update_text.emit(text)

            # "엔터" 명령 처리
            text_lower = text.lower().strip()
            if "엔터" in text_lower and len(text_lower) < 10:
                self.commands._press_key("enter")
                self.ui.signals.update_response.emit("엔터")
                self.ui.signals.update_console.emit("Enter 키 입력")
                self.processing = False
                self.ui.signals.set_listening.emit(False)
                return

            # 스타일 변환 후 타이핑 + 자동 엔터
            self.ui.signals.update_status.emit("변환 중...")
            transformed_text = self.ai.transform_style(text, self.current_style)
            self.commands._type_text(transformed_text)
            time.sleep(0.1)
            self.commands._press_key("enter")

            if transformed_text != text:
                self.ui.signals.update_response.emit(f"→ {transformed_text}")
                self.ui.signals.update_console.emit(f"변환됨: {text} → {transformed_text}")
            else:
                self.ui.signals.update_response.emit(f"입력됨")
                self.ui.signals.update_console.emit(f"입력됨: {transformed_text}")

            self.ui.signals.update_status.emit(f"{self._get_hotkey_name()}으로 녹음")

        except Exception as e:
            print(f"처리 오류: {e}")
            self.ui.signals.update_response.emit("문제가 생겼어요")
            self.ui.signals.update_status.emit("오류 발생")
        finally:
            self.processing = False
            self.ui.signals.set_listening.emit(False)

    def open_settings(self):
        """설정 다이얼로그 열기"""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog()
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()

    def stop(self):
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()


def main():
    print()
    print("=" * 50)
    print("  ZZABIS - 음성 타이핑 도우미")
    print("  핫키를 누르고 말하면 텍스트로 입력됩니다")
    print("=" * 50)
    print()

    # Qt 앱 생성
    qt_app = QApplication(sys.argv)
    qt_app.setStyle("Fusion")

    # API 키 확인
    if not check_api_keys():
        print("API 키가 설정되지 않아 종료합니다.")
        sys.exit(1)

    print("OpenAI API 키 확인 완료!")

    # UI 생성
    ui = MacVoiceUI()
    ui.show()

    # 메인 앱 생성
    app = ZzabisApp(ui)

    # 종료 처리
    qt_app.aboutToQuit.connect(app.stop)

    print("ZZABIS 시작!")
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
