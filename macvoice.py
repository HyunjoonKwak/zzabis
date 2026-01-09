#!/usr/bin/env python3
"""
MacVoice - 맥북 음성 제어 시스템
항상 음성 대기 → 말하면 인식 → 명령어 실행 또는 텍스트 입력
"""

import threading
import numpy as np
import sounddevice as sd
import whisper
from pynput.keyboard import Controller, Key
import pyperclip
import time

from commands import CommandExecutor

# 설정
SAMPLE_RATE = 16000
MODEL_SIZE = "large"  # tiny, base, small, medium, large
SILENCE_THRESHOLD = 0.01  # 무음 감지 임계값
SILENCE_DURATION = 1.5  # 이 시간(초) 동안 무음이면 인식 시작
MIN_AUDIO_LENGTH = 0.5  # 최소 오디오 길이 (초)


class MacVoice:
    def __init__(self):
        self.audio_buffer = []
        self.is_speaking = False
        self.silence_start = None
        self.keyboard_controller = Controller()
        self.model = None
        self.command_executor = CommandExecutor()
        self.running = True
        self.processing = False

        print()
        print("=" * 50)
        print("  MacVoice - 맥북 음성 제어 시스템")
        print("=" * 50)
        print()
        print(f"Whisper 모델 로딩 중: {MODEL_SIZE}")
        print("(large 모델은 첫 로딩에 시간이 걸릴 수 있습니다...)")
        self.model = whisper.load_model(MODEL_SIZE)
        print()
        print("준비 완료!")
        print()
        print("-" * 50)
        print("  사용법: 그냥 말하세요!")
        print("-" * 50)
        print("  - 말을 멈추면 자동으로 인식됩니다")
        print("  - Ctrl+C로 종료")
        print()
        print("-" * 50)
        print("  음성 명령어 예시")
        print("-" * 50)
        print("  [앱 실행] 사파리 열어, 크롬 열어, 터미널 열어")
        print("  [볼륨]   볼륨 올려, 볼륨 내려, 음소거")
        print("  [밝기]   밝기 올려, 밝기 낮춰")
        print("  [창]    창 최소화, 창 최대화, 풀스크린")
        print("  [마우스] 클릭, 오른쪽 클릭, 스크롤 위로")
        print("  [시스템] 화면 잠금, 스크린샷")
        print()
        print("  * 명령어가 아닌 경우 텍스트로 입력됩니다")
        print("=" * 50)
        print()
        print("[대기 중] 말씀하세요...")
        print()

    def get_audio_level(self, audio_chunk):
        """오디오 레벨 계산"""
        return np.sqrt(np.mean(audio_chunk ** 2))

    def audio_callback(self, indata, frames, time_info, status):
        """오디오 스트림 콜백 - 연속 모니터링"""
        if status:
            pass  # 상태 메시지 무시

        if self.processing:
            return

        audio_chunk = indata.copy().flatten()
        level = self.get_audio_level(audio_chunk)

        if level > SILENCE_THRESHOLD:
            # 소리 감지됨
            if not self.is_speaking:
                self.is_speaking = True
                self.audio_buffer = []
            self.audio_buffer.append(audio_chunk)
            self.silence_start = None
        else:
            # 무음
            if self.is_speaking:
                self.audio_buffer.append(audio_chunk)

                if self.silence_start is None:
                    self.silence_start = time.time()
                elif time.time() - self.silence_start > SILENCE_DURATION:
                    # 충분한 무음 → 인식 시작
                    self.is_speaking = False
                    self.silence_start = None

                    # 최소 길이 확인
                    total_samples = sum(len(chunk) for chunk in self.audio_buffer)
                    audio_length = total_samples / SAMPLE_RATE

                    if audio_length >= MIN_AUDIO_LENGTH:
                        # 별도 스레드에서 처리
                        audio_data = self.audio_buffer.copy()
                        self.audio_buffer = []
                        threading.Thread(
                            target=self.process_audio,
                            args=(audio_data,),
                            daemon=True
                        ).start()
                    else:
                        self.audio_buffer = []

    def process_audio(self, audio_chunks):
        """오디오 처리 및 변환"""
        self.processing = True

        try:
            print("[인식 중...]")

            # 오디오 데이터 합치기
            audio = np.concatenate(audio_chunks)

            # Whisper로 변환
            result = self.model.transcribe(
                audio,
                fp16=False,
                language=None  # 자동 감지
            )

            text = result["text"].strip()
            detected_lang = result.get("language", "unknown")

            if not text:
                print("[대기 중] 말씀하세요...")
                return

            print(f"[{detected_lang}] \"{text}\"")

            # 명령어 실행 시도
            if self.command_executor.execute(text):
                pass  # 명령어 실행됨
            else:
                # 명령어가 아니면 텍스트 입력
                print("  → 텍스트 입력")
                self.type_text(text)

            print()
            print("[대기 중] 말씀하세요...")

        except Exception as e:
            print(f"오류: {e}")
        finally:
            self.processing = False

    def type_text(self, text):
        """텍스트 입력 (클립보드 사용)"""
        old_clipboard = pyperclip.paste()
        pyperclip.copy(text)

        # Cmd+V로 붙여넣기
        self.keyboard_controller.press(Key.cmd)
        self.keyboard_controller.press('v')
        self.keyboard_controller.release('v')
        self.keyboard_controller.release(Key.cmd)

        # 원래 클립보드 복원
        threading.Timer(0.1, lambda: pyperclip.copy(old_clipboard)).start()

    def run(self):
        """메인 루프 - 연속 음성 인식"""
        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype=np.float32,
                callback=self.audio_callback,
                blocksize=int(SAMPLE_RATE * 0.1)  # 100ms 블록
            ):
                while self.running:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nMacVoice 종료")
            self.running = False


def main():
    print()
    print("필요한 macOS 권한:")
    print("  1. 마이크 접근 권한")
    print("  2. 손쉬운 사용 (키보드/마우스 제어)")
    print("  → 시스템 설정 > 개인정보 보호 및 보안")
    print()

    app = MacVoice()
    app.run()


if __name__ == "__main__":
    main()
