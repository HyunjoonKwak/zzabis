"""
ZZABIS 설정 다이얼로그 - 장치 설정
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QWidget, QComboBox, QMessageBox,
    QApplication, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from config import (
    get_microphone, set_microphone, get_screen, set_screen,
    get_hotkey, set_hotkey, get_style_mode, set_style_mode, STYLE_MODES
)
import sounddevice as sd


class SettingsDialog(QDialog):
    """설정 다이얼로그 - 장치 설정"""

    settings_changed = pyqtSignal()
    microphone_changed = pyqtSignal(object)
    screen_changed = pyqtSignal(int)
    hotkey_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ZZABIS 설정")
        self.setMinimumSize(420, 480)
        self.setMaximumSize(500, 600)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.is_capturing = False
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.setStyleSheet("""
            QDialog {
                background: #1a1a2e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QComboBox {
                padding: 8px 12px;
                font-size: 13px;
                background: #252540;
                border: 1px solid #404060;
                border-radius: 6px;
                color: white;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #00c8a0;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #888;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background: #252540;
                color: white;
                selection-background-color: #00a080;
                border: 1px solid #404060;
            }
            QPushButton {
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # 타이틀
        title = QLabel("ZZABIS 설정")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #00ffc8;
            padding-bottom: 10px;
        """)
        layout.addWidget(title)

        # === 핫키 설정 ===
        hotkey_section = self._create_section("녹음 트리거")

        self.hotkey_display = QLabel(self._get_hotkey_display_name())
        self.hotkey_display.setStyleSheet("""
            padding: 12px 16px;
            font-size: 14px;
            font-weight: bold;
            background: #252540;
            border: 2px solid #00c8a0;
            border-radius: 8px;
            color: #00ffc8;
        """)
        hotkey_section.addWidget(self.hotkey_display)

        hotkey_btns = QHBoxLayout()
        hotkey_btns.setSpacing(10)

        self.hotkey_btn = QPushButton("키보드 설정")
        self.hotkey_btn.setStyleSheet("""
            QPushButton {
                background: #00a080;
                color: white;
            }
            QPushButton:hover {
                background: #00c8a0;
            }
        """)
        self.hotkey_btn.clicked.connect(self._start_hotkey_capture)
        hotkey_btns.addWidget(self.hotkey_btn)

        self.mouse_btn = QPushButton("마우스 사이드")
        self.mouse_btn.setStyleSheet("""
            QPushButton {
                background: #6050a0;
                color: white;
            }
            QPushButton:hover {
                background: #7060b0;
            }
        """)
        self.mouse_btn.clicked.connect(self._set_mouse_hotkey)
        hotkey_btns.addWidget(self.mouse_btn)

        hotkey_section.addLayout(hotkey_btns)
        layout.addLayout(hotkey_section)

        # === 마이크 설정 ===
        mic_section = self._create_section("마이크")
        self.mic_combo = QComboBox()
        self._load_microphones()
        self.mic_combo.currentIndexChanged.connect(self._on_mic_changed)
        mic_section.addWidget(self.mic_combo)
        layout.addLayout(mic_section)

        # === 화면 설정 ===
        screen_section = self._create_section("UI 표시 화면")
        self.screen_combo = QComboBox()
        self._load_screens()
        self.screen_combo.currentIndexChanged.connect(self._on_screen_changed)
        screen_section.addWidget(self.screen_combo)
        layout.addLayout(screen_section)

        # === 스타일 설정 ===
        style_section = self._create_section("기본 스타일")
        self.style_combo = QComboBox()
        current_style = get_style_mode()
        for mode_key, mode_name in STYLE_MODES.items():
            self.style_combo.addItem(mode_name, mode_key)
            if mode_key == current_style:
                self.style_combo.setCurrentIndex(self.style_combo.count() - 1)
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        style_section.addWidget(self.style_combo)

        style_hint = QLabel("메인 화면에서 10가지 스타일 버튼으로 변경 가능")
        style_hint.setStyleSheet("color: #888; font-size: 11px; padding-top: 4px;")
        style_section.addWidget(style_hint)
        layout.addLayout(style_section)

        # 스페이서
        layout.addStretch()

        # 안내 문구
        hint = QLabel("설정은 자동 저장됩니다. 일부 설정은 재시작 후 적용됩니다.")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint)

        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #404060;
                color: white;
                padding: 12px;
            }
            QPushButton:hover {
                background: #505080;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _create_section(self, title: str) -> QVBoxLayout:
        """섹션 레이아웃 생성"""
        section = QVBoxLayout()
        section.setSpacing(8)

        label = QLabel(title)
        label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #00c8a0;
        """)
        section.addWidget(label)
        return section

    def _load_microphones(self):
        """마이크 목록 로드"""
        self.mic_combo.clear()
        self.mic_combo.addItem("시스템 기본 마이크", None)

        devices = sd.query_devices()
        saved_mic = get_microphone()

        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                name = dev['name']
                self.mic_combo.addItem(name, i)
                if saved_mic == i:
                    self.mic_combo.setCurrentIndex(self.mic_combo.count() - 1)

    def _load_screens(self):
        """화면 목록 로드"""
        self.screen_combo.clear()
        screens = QApplication.screens()
        saved_screen = get_screen()

        for i, screen in enumerate(screens):
            geo = screen.geometry()
            self.screen_combo.addItem(f"모니터 {i+1} ({geo.width()}x{geo.height()})", i)
            if saved_screen == i:
                self.screen_combo.setCurrentIndex(i)

    def _on_mic_changed(self, index):
        device = self.mic_combo.currentData()
        set_microphone(device)
        self.microphone_changed.emit(device)

    def _on_screen_changed(self, index):
        screen_idx = self.screen_combo.currentData()
        if screen_idx is not None:
            set_screen(screen_idx)
            self.screen_changed.emit(screen_idx)

    def _on_style_changed(self, index):
        style = self.style_combo.currentData()
        set_style_mode(style)

    def _get_hotkey_display_name(self) -> str:
        """현재 핫키 표시"""
        hotkey = get_hotkey()
        hotkey_type = hotkey.get("type", "mouse")

        if hotkey_type == "mouse":
            button = hotkey.get("button", "side")
            if button == "side":
                return "마우스 사이드 버튼"
            elif button == "middle":
                return "마우스 휠 버튼"
            return f"마우스 {button}"
        else:
            key = hotkey.get("key", "space")
            modifiers = hotkey.get("modifiers", [])

            key_names = {
                "space": "Space", "ctrl": "Ctrl", "alt": "Alt",
                "shift": "Shift", "cmd": "Cmd", "enter": "Enter",
                "tab": "Tab", "esc": "Esc", "backspace": "Backspace",
            }

            if key.startswith("f") and key[1:].isdigit():
                key_display = key.upper()
            else:
                key_display = key_names.get(key, key.upper())

            if modifiers:
                mod_display = "+".join([m.capitalize() for m in modifiers])
                return f"{mod_display}+{key_display}"
            return key_display

    def _set_mouse_hotkey(self):
        """마우스 사이드 버튼으로 설정"""
        hotkey_config = {"type": "mouse", "button": "side"}
        set_hotkey(hotkey_config)
        self.hotkey_changed.emit(hotkey_config)
        self.hotkey_display.setText(self._get_hotkey_display_name())
        QMessageBox.information(self, "설정 완료", "마우스 사이드 버튼으로 설정되었습니다.\n앱을 재시작하면 적용됩니다.")

    def _start_hotkey_capture(self):
        """핫키 캡처 시작"""
        if self.is_capturing:
            return

        self.is_capturing = True
        self.hotkey_btn.setText("키 입력 대기...")
        self.hotkey_btn.setEnabled(False)
        self.hotkey_display.setText("키보드 키를 누르세요...")
        self.hotkey_display.setStyleSheet("""
            padding: 12px 16px;
            font-size: 14px;
            font-weight: bold;
            background: #503000;
            border: 2px solid #ffa000;
            border-radius: 8px;
            color: #ffcc00;
        """)
        self.activateWindow()
        self.setFocus()

    def _finish_hotkey_capture(self):
        """핫키 캡처 완료"""
        self.is_capturing = False
        self.hotkey_btn.setText("키보드 설정")
        self.hotkey_btn.setEnabled(True)
        self.hotkey_display.setText(self._get_hotkey_display_name())
        self.hotkey_display.setStyleSheet("""
            padding: 12px 16px;
            font-size: 14px;
            font-weight: bold;
            background: #252540;
            border: 2px solid #00c8a0;
            border-radius: 8px;
            color: #00ffc8;
        """)
        QMessageBox.information(self, "설정 완료", f"핫키가 '{self._get_hotkey_display_name()}'(으)로 설정되었습니다.\n앱을 재시작하면 적용됩니다.")

    def keyPressEvent(self, event: QKeyEvent):
        """키보드 입력"""
        if self.is_capturing:
            key = event.key()
            modifiers = event.modifiers()

            # 수정자만 눌린 경우
            modifier_only = {
                Qt.Key.Key_Control, Qt.Key.Key_Shift,
                Qt.Key.Key_Alt, Qt.Key.Key_Meta
            }
            if key in modifier_only:
                mod_names = []
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    mod_names.append("Ctrl")
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    mod_names.append("Shift")
                if modifiers & Qt.KeyboardModifier.AltModifier:
                    mod_names.append("Alt")
                if modifiers & Qt.KeyboardModifier.MetaModifier:
                    mod_names.append("Cmd")
                if mod_names:
                    self.hotkey_display.setText("+".join(mod_names) + "+...")
                return

            key_name = self._qt_key_to_name(key)
            if not key_name:
                text = event.text()
                if text and text.isprintable():
                    key_name = text.lower()

            if key_name:
                modifier_list = []
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    modifier_list.append("ctrl")
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    modifier_list.append("shift")
                if modifiers & Qt.KeyboardModifier.AltModifier:
                    modifier_list.append("alt")
                if modifiers & Qt.KeyboardModifier.MetaModifier:
                    modifier_list.append("cmd")

                hotkey_config = {
                    "type": "keyboard",
                    "key": key_name,
                    "modifiers": modifier_list
                }
                set_hotkey(hotkey_config)
                self.hotkey_changed.emit(hotkey_config)
                self._finish_hotkey_capture()
            return

        super().keyPressEvent(event)

    def _qt_key_to_name(self, key) -> str:
        """Qt 키를 이름으로 변환"""
        key_map = {
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_F1: "f1", Qt.Key.Key_F2: "f2", Qt.Key.Key_F3: "f3",
            Qt.Key.Key_F4: "f4", Qt.Key.Key_F5: "f5", Qt.Key.Key_F6: "f6",
            Qt.Key.Key_F7: "f7", Qt.Key.Key_F8: "f8", Qt.Key.Key_F9: "f9",
            Qt.Key.Key_F10: "f10", Qt.Key.Key_F11: "f11", Qt.Key.Key_F12: "f12",
            Qt.Key.Key_Tab: "tab", Qt.Key.Key_Escape: "esc",
            Qt.Key.Key_Return: "enter", Qt.Key.Key_Enter: "enter",
            Qt.Key.Key_Backspace: "backspace", Qt.Key.Key_Delete: "delete",
        }

        if key in key_map:
            return key_map[key]

        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key).lower()

        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return chr(key)

        return None


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec())
