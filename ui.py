"""
MacVoice UI - 반투명 글래스모피즘 AI 비서 인터페이스
"""

import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGraphicsDropShadowEffect, QPushButton
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QObject, QPoint, QPropertyAnimation
)
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QPen, QBrush,
    QFont, QPainterPath, QRadialGradient
)
from config import get_style_mode, set_style_mode, STYLE_MODES


class SignalEmitter(QObject):
    """스레드 간 신호 전달"""
    update_status = pyqtSignal(str)
    update_text = pyqtSignal(str)
    update_response = pyqtSignal(str)
    update_level = pyqtSignal(float)
    set_listening = pyqtSignal(bool)
    set_processing = pyqtSignal(bool)
    update_console = pyqtSignal(str)
    style_changed = pyqtSignal(str)  # 스타일 모드 변경


class StyleButton(QPushButton):
    """스타일 선택 버튼"""

    def __init__(self, code: str, name: str, parent=None):
        super().__init__(name, parent)
        self.code = code
        self.is_selected = False
        self.setFixedSize(55, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 80, 60, 200);
                    color: white;
                    border: none;
                    border-radius: 13px;
                    font-size: 9px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 25);
                    color: rgba(255, 255, 255, 160);
                    border: 1px solid rgba(255, 255, 255, 30);
                    border-radius: 11px;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background: rgba(255, 100, 80, 80);
                    border: 1px solid rgba(255, 100, 80, 100);
                }
            """)


class VoiceOrb(QWidget):
    """ZZABIS 스타일 빨간색 구체 - 신비로운 3D 효과"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)

        self.state = "idle"
        self.pulse_phase = 0
        self.audio_level = 0
        self.wave_phase = 0
        self.rotation_phase = 0
        self.energy_rings = []
        self.particles = []

        # 빨간색/주황색 기반 색상
        self.colors = {
            "idle": (220, 60, 60),       # 어두운 빨강
            "listening": (255, 80, 40),   # 밝은 주황빨강
            "processing": (255, 120, 0),  # 주황색
            "speaking": (255, 50, 50)     # 밝은 빨강
        }

        # 파티클 초기화
        import random
        for _ in range(8):
            self.particles.append({
                'angle': random.random() * math.pi * 2,
                'speed': 0.02 + random.random() * 0.03,
                'dist': 25 + random.random() * 20,
                'size': 2 + random.random() * 2
            })

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def set_state(self, state: str):
        self.state = state

    def set_audio_level(self, level: float):
        target = min(1.0, level * 25)
        self.audio_level += (target - self.audio_level) * 0.3

    def animate(self):
        self.pulse_phase += 0.06
        self.wave_phase += 0.1
        self.rotation_phase += 0.02

        # 파티클 업데이트
        for p in self.particles:
            p['angle'] += p['speed'] * (1 + self.audio_level * 2)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        r, g, b = self.colors[self.state]
        pulse = (math.sin(self.pulse_phase) + 1) / 2
        is_active = self.state in ["listening", "speaking", "processing"]

        # === 1. 외부 에너지 필드 (신비로운 글로우) ===
        for i in range(5):
            ring_size = 55 + i * 6 + pulse * 8 + self.audio_level * 15
            alpha = int((40 - i * 7) * (0.6 + self.audio_level * 0.4))

            gradient = QRadialGradient(cx, cy, ring_size)
            gradient.setColorAt(0, QColor(r, g, b, 0))
            gradient.setColorAt(0.5, QColor(r, g, b, alpha // 2))
            gradient.setColorAt(0.8, QColor(r, g, b, alpha))
            gradient.setColorAt(1, QColor(r, g, b, 0))

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                int(cx - ring_size), int(cy - ring_size),
                int(ring_size * 2), int(ring_size * 2)
            )

        # === 2. 회전하는 에너지 링들 ===
        if is_active:
            for i in range(3):
                angle = self.rotation_phase + i * (math.pi * 2 / 3)
                ring_dist = 38 + self.audio_level * 10 + math.sin(self.wave_phase + i) * 5
                ring_alpha = int(80 + self.audio_level * 80)

                pen = QPen(QColor(r, g, b, ring_alpha))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)

                # 타원형 링 (3D 효과)
                painter.save()
                painter.translate(cx, cy)
                painter.rotate(math.degrees(angle))
                painter.scale(1, 0.4)  # 기울어진 링
                painter.drawEllipse(int(-ring_dist), int(-ring_dist), int(ring_dist * 2), int(ring_dist * 2))
                painter.restore()

        # === 3. 파동 링 (음성 감지 시) ===
        if self.audio_level > 0.05 or is_active:
            for i in range(3):
                wave_offset = (self.wave_phase + i * 0.5) % (math.pi * 2)
                wave_scale = (math.sin(wave_offset) + 1) / 2
                wave_size = 30 + i * 12 + self.audio_level * 25 + wave_scale * 8
                wave_alpha = int((70 - i * 20) * (0.4 + self.audio_level * 0.6) * (1 - wave_scale * 0.3))

                pen = QPen(QColor(255, 150, 100, wave_alpha))
                pen.setWidth(2 if i == 0 else 1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(
                    int(cx - wave_size), int(cy - wave_size),
                    int(wave_size * 2), int(wave_size * 2)
                )

        # === 4. 궤도 파티클들 ===
        for p in self.particles:
            px = cx + math.cos(p['angle']) * (p['dist'] + self.audio_level * 15)
            py = cy + math.sin(p['angle']) * (p['dist'] + self.audio_level * 15) * 0.6
            size = p['size'] * (1 + self.audio_level)

            particle_gradient = QRadialGradient(px, py, size * 2)
            particle_gradient.setColorAt(0, QColor(255, 200, 150, 200))
            particle_gradient.setColorAt(0.5, QColor(r, g, b, 150))
            particle_gradient.setColorAt(1, QColor(r, g, b, 0))

            painter.setBrush(particle_gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(px - size), int(py - size), int(size * 2), int(size * 2))

        # === 5. 메인 구체 (3D 입체 효과) ===
        core_size = 26 + pulse * 4 + self.audio_level * 10

        # 외부 글로우
        outer_glow = QRadialGradient(cx, cy, core_size + 15)
        outer_glow.setColorAt(0, QColor(r, g, b, 100))
        outer_glow.setColorAt(0.5, QColor(r, g, b, 50))
        outer_glow.setColorAt(1, QColor(r, g, b, 0))
        painter.setBrush(outer_glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(cx - core_size - 15), int(cy - core_size - 15),
            int((core_size + 15) * 2), int((core_size + 15) * 2)
        )

        # 구체 본체 (3D 그라디언트)
        sphere_gradient = QRadialGradient(cx - core_size * 0.35, cy - core_size * 0.35, core_size * 1.8)
        sphere_gradient.setColorAt(0, QColor(255, 255, 255, 220))  # 하이라이트
        sphere_gradient.setColorAt(0.15, QColor(255, 200, 180, 200))
        sphere_gradient.setColorAt(0.3, QColor(r, g, b, 255))
        sphere_gradient.setColorAt(0.6, QColor(int(r * 0.7), int(g * 0.5), int(b * 0.5), 255))
        sphere_gradient.setColorAt(1, QColor(int(r * 0.3), int(g * 0.2), int(b * 0.2), 200))

        painter.setBrush(sphere_gradient)

        # 미세한 테두리
        pen = QPen(QColor(255, 150, 100, 80))
        pen.setWidth(1)
        painter.setPen(pen)

        painter.drawEllipse(
            int(cx - core_size), int(cy - core_size),
            int(core_size * 2), int(core_size * 2)
        )

        # === 6. 내부 코어 빛 (심장 박동 효과) ===
        inner_pulse = (math.sin(self.pulse_phase * 2) + 1) / 2
        inner_size = 8 + inner_pulse * 6 + self.audio_level * 8

        inner_gradient = QRadialGradient(cx, cy, inner_size)
        inner_gradient.setColorAt(0, QColor(255, 255, 255, 255))
        inner_gradient.setColorAt(0.3, QColor(255, 200, 150, 200))
        inner_gradient.setColorAt(0.7, QColor(r, g, b, 100))
        inner_gradient.setColorAt(1, QColor(r, g, b, 0))

        painter.setBrush(inner_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(cx - inner_size), int(cy - inner_size),
            int(inner_size * 2), int(inner_size * 2)
        )

        # === 7. 하이라이트 반사광 ===
        highlight_x = cx - core_size * 0.4
        highlight_y = cy - core_size * 0.4
        highlight_size = core_size * 0.35

        highlight = QRadialGradient(highlight_x, highlight_y, highlight_size)
        highlight.setColorAt(0, QColor(255, 255, 255, 180))
        highlight.setColorAt(0.5, QColor(255, 255, 255, 50))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))

        painter.setBrush(highlight)
        painter.drawEllipse(
            int(highlight_x - highlight_size), int(highlight_y - highlight_size),
            int(highlight_size * 2), int(highlight_size * 2)
        )


class WaveformBar(QWidget):
    """파형 바"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 30)  # 더 큰 파형
        self.bars = 20
        self.levels = [0.15] * self.bars
        self.phase = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def set_level(self, level: float):
        import random
        for i in range(self.bars):
            center = self.bars // 2
            dist = abs(i - center) / center
            wave = math.sin(i * 0.4 + self.phase) * 0.3 + 0.5
            self.levels[i] = min(1.0, level * 20 * wave * (1 - dist * 0.4) + random.random() * 0.1 + 0.15)

    def animate(self):
        self.phase += 0.1
        for i in range(self.bars):
            base = 0.15 + math.sin(self.phase + i * 0.2) * 0.05
            self.levels[i] = max(base, self.levels[i] * 0.9)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bar_width = 3
        gap = 3
        total_width = self.bars * (bar_width + gap)
        start_x = (self.width() - total_width) / 2
        center_y = self.height() / 2

        for i, level in enumerate(self.levels):
            x = start_x + i * (bar_width + gap)
            bar_height = max(3, level * 16)

            # 빨간색/주황색 그라디언트
            red = int(200 + level * 55)
            green = int(60 + level * 60)
            color = QColor(red, green, 50, int(150 + level * 100))
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                int(x), int(center_y - bar_height / 2),
                int(bar_width), int(bar_height),
                1, 1
            )


class MacVoiceUI(QWidget):
    """메인 UI - 가로 레이아웃"""

    def __init__(self):
        super().__init__()
        self.signals = SignalEmitter()
        self.drag_pos = None
        self.current_style = get_style_mode()
        self.style_buttons = {}
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("ZZABIS")
        self.setFixedSize(520, 300)  # 더 컴팩트하게
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)

        # 메인 프레임 - 반투명 배경 (빨간 테두리)
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame {
                background: rgba(20, 10, 10, 180);
                border-radius: 18px;
                border: 1px solid rgba(255, 80, 60, 120);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(255, 80, 60, 80))
        shadow.setOffset(0, 4)
        self.main_frame.setGraphicsEffect(shadow)

        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setContentsMargins(0, 10, 0, 8)
        frame_layout.setSpacing(6)

        # === 상단 헤더 ===
        header_container = QVBoxLayout()
        header_container.setSpacing(4)

        # 첫 번째 줄: 타이틀 + 설정/닫기
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title = QLabel("ZZABIS")
        title.setStyleSheet("""
            color: rgba(255, 100, 80, 255);
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 4px;
        """)
        title_row.addWidget(title)
        title_row.addStretch()

        # 설정 버튼
        self.settings_btn = QLabel("⚙")
        self.settings_btn.setStyleSheet("color: rgba(255, 255, 255, 150); font-size: 16px;")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setToolTip("설정")
        title_row.addWidget(self.settings_btn)

        # 닫기 버튼
        close_btn = QLabel("×")
        close_btn.setStyleSheet("color: rgba(255, 255, 255, 100); font-size: 18px;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.mousePressEvent = lambda e: QApplication.quit()
        title_row.addWidget(close_btn)

        header_container.addLayout(title_row)

        # 두 번째 줄: 스타일 버튼들 (2줄로 배치)
        style_container = QVBoxLayout()
        style_container.setSpacing(3)

        # 스타일 버튼 데이터
        styles = [
            ("normal", "그대로"), ("formal", "공적"), ("polite", "정중"),
            ("casual", "반말"), ("cute", "귀엽게"),
            ("aegyo", "애교"), ("romantic", "다정"), ("cold", "쿨하게"),
            ("humor", "유머"), ("pro", "비즈니스"),
        ]

        # 첫 번째 줄 (5개)
        row1 = QHBoxLayout()
        row1.setSpacing(4)
        for code, name in styles[:5]:
            btn = StyleButton(code, name)
            btn.clicked.connect(lambda checked, c=code: self.on_style_click(c))
            self.style_buttons[code] = btn
            row1.addWidget(btn)
        row1.addStretch()
        style_container.addLayout(row1)

        # 두 번째 줄 (5개)
        row2 = QHBoxLayout()
        row2.setSpacing(4)
        for code, name in styles[5:]:
            btn = StyleButton(code, name)
            btn.clicked.connect(lambda checked, c=code: self.on_style_click(c))
            self.style_buttons[code] = btn
            row2.addWidget(btn)
        row2.addStretch()
        style_container.addLayout(row2)

        self.style_buttons[self.current_style].set_selected(True)

        header_container.addLayout(style_container)
        frame_layout.addLayout(header_container)

        # === 메인 콘텐츠 (가로 레이아웃) ===
        content = QHBoxLayout()
        content.setSpacing(15)

        # 왼쪽: 오브 + 파형
        left_section = QVBoxLayout()
        left_section.setSpacing(4)

        orb_container = QHBoxLayout()
        self.orb = VoiceOrb()
        orb_container.addWidget(self.orb)
        left_section.addLayout(orb_container)

        wave_container = QHBoxLayout()
        self.waveform = WaveformBar()
        wave_container.addWidget(self.waveform)
        left_section.addLayout(wave_container)

        content.addLayout(left_section)

        # 오른쪽: 텍스트 영역
        right_section = QVBoxLayout()
        right_section.setSpacing(6)

        # 상태 영역
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        # 녹음 활성화 인디케이터
        self.recording_indicator = QLabel("● REC")
        self.recording_indicator.setStyleSheet("""
            color: rgba(100, 100, 100, 150);
            font-size: 10px;
            font-weight: bold;
            padding: 2px 6px;
            background: rgba(50, 50, 50, 100);
            border-radius: 4px;
        """)
        self.recording_indicator.setFixedWidth(50)
        status_row.addWidget(self.recording_indicator)

        # 상태 텍스트
        self.status_label = QLabel("초기화 중...")
        self.status_label.setStyleSheet("""
            color: rgba(255, 150, 100, 200);
            font-size: 10px;
            letter-spacing: 1px;
        """)
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        right_section.addLayout(status_row)

        # 인식 텍스트 + 복사 버튼
        text_row = QHBoxLayout()
        text_row.setSpacing(8)

        self.text_label = QLabel("")
        self.text_label.setWordWrap(True)
        self.text_label.setMinimumHeight(40)
        self.text_label.setStyleSheet("""
            color: rgba(255, 255, 255, 220);
            font-size: 14px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 12);
            border-radius: 10px;
        """)
        text_row.addWidget(self.text_label, 1)

        # 복사 버튼
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(36, 36)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setToolTip("텍스트 복사")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: rgba(80, 80, 100, 150);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(100, 150, 200, 200);
            }
        """)
        self.copy_btn.clicked.connect(self._copy_text)
        text_row.addWidget(self.copy_btn)

        right_section.addLayout(text_row)

        # AI 응답
        self.response_label = QLabel("")
        self.response_label.setWordWrap(True)
        self.response_label.setMinimumHeight(50)
        self.response_label.setStyleSheet("""
            color: rgba(255, 200, 150, 255);
            font-size: 15px;
            font-weight: 500;
            padding: 12px 14px;
            background: rgba(255, 80, 50, 15);
            border-radius: 12px;
            border: 1px solid rgba(255, 100, 80, 60);
        """)
        right_section.addWidget(self.response_label)

        right_section.addStretch()
        content.addLayout(right_section, 1)

        frame_layout.addLayout(content)

        # === 콘솔 출력 ===
        self.console_label = QLabel("")
        self.console_label.setStyleSheet("""
            color: rgba(150, 255, 150, 200);
            font-size: 10px;
            font-family: 'Menlo', 'Monaco', monospace;
            padding: 6px 10px;
            background: rgba(0, 0, 0, 100);
            border-radius: 6px;
        """)
        self.console_label.setWordWrap(True)
        self.console_label.setMinimumHeight(30)
        self.console_label.setMaximumHeight(50)
        frame_layout.addWidget(self.console_label)

        layout.addWidget(self.main_frame)

        # 화면 위치
        self.position_window()

    def ensure_on_top(self):
        """항상 최상위 유지 - 포커스 뺏지 않음"""
        if self.isVisible():
            self.raise_()

    def on_style_click(self, code: str):
        """스타일 버튼 클릭"""
        if code != self.current_style:
            self.style_buttons[self.current_style].set_selected(False)
            self.current_style = code
            self.style_buttons[code].set_selected(True)
            set_style_mode(code)
            self.signals.style_changed.emit(code)
            self.status_label.setText(f"{STYLE_MODES.get(code, code)} 모드")

    def get_current_style(self) -> str:
        return self.current_style

    def connect_signals(self):
        self.signals.update_status.connect(self.set_status)
        self.signals.update_text.connect(self.set_text)
        self.signals.update_response.connect(self.set_response)
        self.signals.update_level.connect(self.on_level)
        self.signals.set_listening.connect(self.on_listening)
        self.signals.set_processing.connect(self.on_processing)
        self.signals.update_console.connect(self.set_console)

    def position_window(self, screen_index: int = 0):
        """창 위치 설정 (모니터 선택 가능)"""
        screens = QApplication.screens()
        if screen_index >= len(screens):
            screen_index = 0
        screen = screens[screen_index].geometry()
        # 화면 중앙 상단
        x = screen.x() + (screen.width() - self.width()) // 2
        y = screen.y() + 50
        self.move(x, y)
        self.current_screen = screen_index

    def next_screen(self):
        """다음 모니터로 이동"""
        screens = QApplication.screens()
        if len(screens) > 1:
            next_idx = (getattr(self, 'current_screen', 0) + 1) % len(screens)
            self.position_window(next_idx)
            return next_idx + 1
        return 1

    def move_to_screen(self, screen_index: int):
        """특정 모니터로 이동 (0-indexed)"""
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            self.position_window(screen_index)
            return True
        return False

    def set_status(self, text: str):
        self.status_label.setText(text)

    def set_text(self, text: str):
        if text:
            self.text_label.setText(f'"{text}"')
        else:
            self.text_label.setText("")

    def set_response(self, text: str):
        self.response_label.setText(text)
        self.orb.set_state("speaking")
        QTimer.singleShot(3000, lambda: self.orb.set_state("idle") if self.orb.state == "speaking" else None)

    def on_level(self, level: float):
        self.waveform.set_level(level)
        self.orb.set_audio_level(level)

    def on_listening(self, listening: bool):
        if listening:
            self.orb.set_state("listening")
            # 녹음 인디케이터 활성화 (빨간색)
            self.recording_indicator.setStyleSheet("""
                color: rgba(255, 50, 50, 255);
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                background: rgba(255, 50, 50, 50);
                border-radius: 4px;
                border: 1px solid rgba(255, 50, 50, 150);
            """)
        else:
            self.orb.set_state("idle")
            self.status_label.setText("대기 중")
            # 녹음 인디케이터 비활성화 (회색)
            self.recording_indicator.setStyleSheet("""
                color: rgba(100, 100, 100, 150);
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                background: rgba(50, 50, 50, 100);
                border-radius: 4px;
            """)

    def on_processing(self, processing: bool):
        if processing:
            self.orb.set_state("processing")
            self.status_label.setText("처리 중...")

    def set_console(self, text: str):
        """콘솔 출력 표시"""
        self.console_label.setText(f"▸ {text}")

    def _copy_text(self):
        """인식된 텍스트 클립보드에 복사"""
        text = self.text_label.text()
        if text and text.startswith('"') and text.endswith('"'):
            text = text[1:-1]  # 따옴표 제거
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            # 복사 완료 피드백
            self.copy_btn.setText("✓")
            QTimer.singleShot(1000, lambda: self.copy_btn.setText("📋"))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None


def create_ui():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MacVoiceUI()
    window.show()
    return app, window


if __name__ == "__main__":
    app, window = create_ui()
    window.set_status("대기 중")
    window.orb.set_state("listening")
    sys.exit(app.exec())
