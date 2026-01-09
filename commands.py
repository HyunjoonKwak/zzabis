"""
MacVoice 명령어 시스템
음성으로 맥북 전체를 제어
"""

import subprocess
import re
import time
from typing import Optional, Callable
import pyautogui
import pyperclip

# 마우스 안전 설정
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class CommandExecutor:
    """음성 명령어 실행기"""

    def __init__(self):
        self.commands = self._build_commands()

    def _run_applescript(self, script: str) -> str:
        """AppleScript 실행"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"AppleScript 오류: {e}")
            return ""

    def get_frontmost_app(self) -> str:
        """현재 활성 앱 이름 가져오기"""
        script = 'tell application "System Events" to get name of first process whose frontmost is true'
        return self._run_applescript(script)

    def can_use_tabs(self) -> bool:
        """현재 앱이 탭을 지원하는지 확인"""
        app = self.get_frontmost_app().lower()
        tab_apps = ['safari', 'google chrome', 'firefox', 'arc', 'edge', 'brave',
                    'finder', 'terminal', 'iterm', 'visual studio code', 'code']
        return any(tab_app in app for tab_app in tab_apps)

    def _build_commands(self) -> dict:
        """명령어 사전 구축"""
        return {
            # === 앱 실행 ===
            "사파리 열어": lambda: self._open_app("Safari"),
            "safari 열어": lambda: self._open_app("Safari"),
            "크롬 열어": lambda: self._open_app("Google Chrome"),
            "chrome 열어": lambda: self._open_app("Google Chrome"),
            "파인더 열어": lambda: self._open_app("Finder"),
            "finder 열어": lambda: self._open_app("Finder"),
            "터미널 열어": lambda: self._open_app("Terminal"),
            "terminal 열어": lambda: self._open_app("Terminal"),
            "메모 열어": lambda: self._open_app("Notes"),
            "노트 열어": lambda: self._open_app("Notes"),
            "음악 열어": lambda: self._open_app("Music"),
            "뮤직 열어": lambda: self._open_app("Music"),
            "설정 열어": lambda: self._open_app("System Preferences"),
            "시스템 설정 열어": lambda: self._open_app("System Preferences"),
            "카카오톡 열어": lambda: self._open_app("KakaoTalk"),
            "슬랙 열어": lambda: self._open_app("Slack"),
            "slack 열어": lambda: self._open_app("Slack"),
            "비주얼 스튜디오 열어": lambda: self._open_app("Visual Studio Code"),
            "vscode 열어": lambda: self._open_app("Visual Studio Code"),
            "코드 열어": lambda: self._open_app("Visual Studio Code"),

            # === 볼륨 제어 ===
            "볼륨 올려": lambda: self._volume_up(),
            "소리 올려": lambda: self._volume_up(),
            "볼륨 높여": lambda: self._volume_up(),
            "볼륨 내려": lambda: self._volume_down(),
            "소리 내려": lambda: self._volume_down(),
            "볼륨 낮춰": lambda: self._volume_down(),
            "음소거": lambda: self._mute(),
            "뮤트": lambda: self._mute(),
            "소리 꺼": lambda: self._mute(),
            "음소거 해제": lambda: self._unmute(),
            "소리 켜": lambda: self._unmute(),

            # === 밝기 제어 ===
            "밝기 올려": lambda: self._brightness_up(),
            "화면 밝게": lambda: self._brightness_up(),
            "밝기 높여": lambda: self._brightness_up(),
            "밝기 내려": lambda: self._brightness_down(),
            "화면 어둡게": lambda: self._brightness_down(),
            "밝기 낮춰": lambda: self._brightness_down(),

            # === 창 관리 ===
            "창 최소화": lambda: self._minimize_window(),
            "최소화": lambda: self._minimize_window(),
            "창 최대화": lambda: self._maximize_window(),
            "최대화": lambda: self._maximize_window(),
            "풀스크린": lambda: self._fullscreen(),
            "전체 화면": lambda: self._fullscreen(),
            "창 닫아": lambda: self._close_window(),
            "닫아": lambda: self._close_window(),
            "창 왼쪽": lambda: self._move_window_left(),
            "왼쪽으로": lambda: self._move_window_left(),
            "창 오른쪽": lambda: self._move_window_right(),
            "오른쪽으로": lambda: self._move_window_right(),
            "다음 창": lambda: self._next_window(),
            "창 전환": lambda: self._next_window(),
            "이전 창": lambda: self._prev_window(),

            # === 마우스 제어 ===
            "클릭": lambda: self._mouse_click(),
            "왼쪽 클릭": lambda: self._mouse_click(),
            "오른쪽 클릭": lambda: self._mouse_right_click(),
            "우클릭": lambda: self._mouse_right_click(),
            "더블 클릭": lambda: self._mouse_double_click(),
            "더블클릭": lambda: self._mouse_double_click(),
            "스크롤 위로": lambda: self._scroll_up(),
            "위로 스크롤": lambda: self._scroll_up(),
            "스크롤 아래로": lambda: self._scroll_down(),
            "아래로 스크롤": lambda: self._scroll_down(),
            "마우스 위로": lambda: self._move_mouse(0, -100),
            "마우스 아래로": lambda: self._move_mouse(0, 100),
            "마우스 왼쪽으로": lambda: self._move_mouse(-100, 0),
            "마우스 오른쪽으로": lambda: self._move_mouse(100, 0),
            "마우스 중앙": lambda: self._mouse_center(),

            # === 시스템 제어 ===
            "화면 잠금": lambda: self._lock_screen(),
            "잠금": lambda: self._lock_screen(),
            "스크린샷": lambda: self._screenshot(),
            "캡처": lambda: self._screenshot(),
            "화면 캡처": lambda: self._screenshot(),
            "잠자기": lambda: self._sleep(),
            "슬립": lambda: self._sleep(),

            # === 미디어 제어 ===
            "재생": lambda: self._media_play_pause(),
            "일시정지": lambda: self._media_play_pause(),
            "플레이": lambda: self._media_play_pause(),
            "다음 곡": lambda: self._media_next(),
            "이전 곡": lambda: self._media_prev(),

            # === 탭 제어 ===
            "새 탭": lambda: self._new_tab(),
            "탭 닫아": lambda: self._close_tab(),
            "다음 탭": lambda: self._next_tab(),
            "이전 탭": lambda: self._prev_tab(),
        }

    # === 앱 실행 ===
    def _open_app(self, app_name: str):
        """앱 열기"""
        self._run_applescript(f'tell application "{app_name}" to activate')
        print(f"  → {app_name} 실행")

    # === 볼륨 제어 ===
    def _volume_up(self, amount: int = 10):
        self._run_applescript(f'set volume output volume ((output volume of (get volume settings)) + {amount})')
        print(f"  → 볼륨 +{amount}")

    def _volume_down(self, amount: int = 10):
        self._run_applescript(f'set volume output volume ((output volume of (get volume settings)) - {amount})')
        print(f"  → 볼륨 -{amount}")

    def _volume_set(self, level: int):
        level = max(0, min(100, level))  # 0-100 사이로 제한
        self._run_applescript(f'set volume output volume {level}')
        print(f"  → 볼륨 {level}%로 설정")

    def _mute(self):
        self._run_applescript('set volume output muted true')
        print("  → 음소거")

    def _unmute(self):
        self._run_applescript('set volume output muted false')
        print("  → 음소거 해제")

    # === 밝기 제어 ===
    def _brightness_up(self, steps: int = 1):
        for _ in range(steps):
            pyautogui.press('brightnessup')
        print(f"  → 밝기 +{steps}단계")

    def _brightness_down(self, steps: int = 1):
        for _ in range(steps):
            pyautogui.press('brightnessdown')
        print(f"  → 밝기 -{steps}단계")

    def _brightness_set(self, level: int):
        """밝기를 특정 레벨로 설정 (1-16단계)"""
        # 먼저 최소로 낮춤
        for _ in range(16):
            pyautogui.press('brightnessdown')
        # 원하는 단계까지 올림
        steps = max(1, min(16, level))
        for _ in range(steps):
            pyautogui.press('brightnessup')
        print(f"  → 밝기 {steps}단계로 설정")

    # === 창 관리 ===
    def _minimize_window(self):
        pyautogui.hotkey('command', 'm')
        print("  → 창 최소화")

    def _maximize_window(self):
        # macOS에서 녹색 버튼 더블클릭 효과
        self._run_applescript('''
            tell application "System Events"
                tell (first process whose frontmost is true)
                    try
                        click button 2 of window 1
                    end try
                end tell
            end tell
        ''')
        print("  → 창 최대화")

    def _fullscreen(self):
        pyautogui.hotkey('command', 'ctrl', 'f')
        print("  → 전체 화면")

    def _close_window(self):
        pyautogui.hotkey('command', 'w')
        print("  → 창 닫기")

    def _move_window_left(self):
        # Rectangle 또는 기본 Split View 사용
        pyautogui.hotkey('ctrl', 'option', 'left')
        print("  → 창 왼쪽 이동")

    def _move_window_right(self):
        pyautogui.hotkey('ctrl', 'option', 'right')
        print("  → 창 오른쪽 이동")

    def _next_window(self):
        pyautogui.hotkey('command', '`')
        print("  → 다음 창")

    def _prev_window(self):
        pyautogui.hotkey('command', 'shift', '`')
        print("  → 이전 창")

    # === 마우스 제어 ===
    def _mouse_click(self):
        pyautogui.click()
        print("  → 클릭")

    def _mouse_right_click(self):
        pyautogui.rightClick()
        print("  → 오른쪽 클릭")

    def _mouse_double_click(self):
        pyautogui.doubleClick()
        print("  → 더블 클릭")

    def _scroll_up(self):
        pyautogui.scroll(5)
        print("  → 스크롤 위로")

    def _scroll_down(self):
        pyautogui.scroll(-5)
        print("  → 스크롤 아래로")

    def _move_mouse(self, x: int, y: int):
        pyautogui.moveRel(x, y, duration=0.2)
        print(f"  → 마우스 이동 ({x}, {y})")

    def _mouse_center(self):
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=0.3)
        print("  → 마우스 중앙으로")

    # === 시스템 제어 ===
    def _lock_screen(self):
        pyautogui.hotkey('command', 'ctrl', 'q')
        print("  → 화면 잠금")

    def _screenshot(self):
        pyautogui.hotkey('command', 'shift', '4')
        print("  → 스크린샷 (영역 선택)")

    def _sleep(self):
        self._run_applescript('tell application "System Events" to sleep')
        print("  → 잠자기 모드")

    # === 미디어 제어 ===
    def _media_play_pause(self):
        pyautogui.press('playpause')
        print("  → 재생/일시정지")

    def _media_next(self):
        pyautogui.press('nexttrack')
        print("  → 다음 곡")

    def _media_prev(self):
        pyautogui.press('prevtrack')
        print("  → 이전 곡")

    # === 탭 제어 ===
    def _new_tab(self) -> bool:
        if not self.can_use_tabs():
            app = self.get_frontmost_app()
            print(f"  ✗ {app}에서는 탭을 사용할 수 없습니다")
            return False
        pyautogui.hotkey('command', 't')
        print("  → 새 탭")
        return True

    def _close_tab(self) -> bool:
        if not self.can_use_tabs():
            app = self.get_frontmost_app()
            print(f"  ✗ {app}에서는 탭을 사용할 수 없습니다")
            return False
        pyautogui.hotkey('command', 'w')
        print("  → 탭 닫기")
        return True

    def _next_tab(self) -> bool:
        if not self.can_use_tabs():
            app = self.get_frontmost_app()
            print(f"  ✗ {app}에서는 탭을 사용할 수 없습니다")
            return False
        pyautogui.hotkey('command', 'shift', ']')
        print("  → 다음 탭")
        return True

    def _prev_tab(self) -> bool:
        if not self.can_use_tabs():
            app = self.get_frontmost_app()
            print(f"  ✗ {app}에서는 탭을 사용할 수 없습니다")
            return False
        pyautogui.hotkey('command', 'shift', '[')
        print("  → 이전 탭")
        return True

    # === 키보드 입력 ===
    def _type_text(self, text: str):
        """텍스트 입력 (한글 지원) - 클립보드 방식"""
        import pyperclip
        try:
            # 기존 클립보드 백업
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""

        try:
            # 텍스트를 클립보드에 복사
            pyperclip.copy(text)
            # 붙여넣기
            pyautogui.hotkey('command', 'v')
            time.sleep(0.1)
        finally:
            # 클립보드 복원
            try:
                time.sleep(0.2)
                pyperclip.copy(old_clipboard)
            except:
                pass

    def _press_key(self, key: str):
        """단일 키 누르기"""
        key_map = {
            'enter': 'return',
            'return': 'return',
            'tab': 'tab',
            'escape': 'escape',
            'esc': 'escape',
            'space': 'space',
            'backspace': 'backspace',
            'delete': 'delete',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'home': 'home',
            'end': 'end',
            'pageup': 'pageup',
            'pagedown': 'pagedown',
        }
        mapped_key = key_map.get(key.lower(), key.lower())
        pyautogui.press(mapped_key)

    def _select_all(self):
        """전체 선택 (Cmd+A)"""
        pyautogui.hotkey('command', 'a')
        print("  → 전체 선택")

    def _copy(self):
        """복사 (Cmd+C)"""
        pyautogui.hotkey('command', 'c')
        print("  → 복사")

    def _paste(self):
        """붙여넣기 (Cmd+V)"""
        pyautogui.hotkey('command', 'v')
        print("  → 붙여넣기")

    def _cut(self):
        """잘라내기 (Cmd+X)"""
        pyautogui.hotkey('command', 'x')
        print("  → 잘라내기")

    def _undo(self):
        """실행 취소 (Cmd+Z)"""
        pyautogui.hotkey('command', 'z')
        print("  → 실행 취소")

    def _redo(self):
        """다시 실행 (Cmd+Shift+Z)"""
        pyautogui.hotkey('command', 'shift', 'z')
        print("  → 다시 실행")

    def _save(self):
        """저장 (Cmd+S)"""
        pyautogui.hotkey('command', 's')
        print("  → 저장")

    def _find(self):
        """찾기 (Cmd+F)"""
        pyautogui.hotkey('command', 'f')
        print("  → 찾기")

    def _switch_app(self):
        """앱 전환 (Cmd+Tab)"""
        pyautogui.hotkey('command', 'tab')
        print("  → 앱 전환")

    def _switch_input_method(self):
        """입력 소스 전환 (Ctrl+Space)"""
        pyautogui.hotkey('ctrl', 'space')
        print("  → 입력 소스 전환")

    def _spotlight(self):
        """Spotlight 검색 (Cmd+Space)"""
        pyautogui.hotkey('command', 'space')
        print("  → Spotlight")

    def _focus_app(self, app_name: str):
        """특정 앱으로 포커스 이동"""
        self._run_applescript(f'tell application "{app_name}" to activate')
        print(f"  → {app_name}으로 포커스")

    def execute(self, text: str) -> bool:
        """
        텍스트에서 명령어 찾아서 실행
        반환: 명령어 실행 여부
        """
        text_lower = text.lower().strip()

        # 정확히 일치하는 명령어 찾기
        for cmd, action in self.commands.items():
            if cmd in text_lower:
                print(f"명령어 감지: {cmd}")
                action()
                return True

        # 동적 앱 열기 처리 ("~~ 열어" 패턴)
        app_match = re.search(r'(.+?)\s*(열어|실행|켜)', text_lower)
        if app_match:
            app_name = app_match.group(1).strip()
            print(f"앱 열기 시도: {app_name}")
            self._open_app(app_name)
            return True

        return False
