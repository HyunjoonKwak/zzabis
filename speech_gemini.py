"""
Gemini 기반 음성 인식
"""

import io
import wave
import numpy as np
from typing import Optional
from google import genai
from config import get_api_key


class GeminiSpeechRecognizer:
    """Gemini를 사용한 음성 인식"""

    def __init__(self, model: str = "gemini-3-flash-preview"):  # Gemini 3 Flash - 빠른 응답
        api_key = get_api_key()
        if not api_key:
            raise ValueError("Gemini API 키가 설정되지 않았습니다")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000, language: str = "ko") -> str:
        """
        오디오 데이터를 텍스트로 변환

        Args:
            audio_data: numpy array of audio samples (float32, -1 to 1)
            sample_rate: 샘플링 레이트 (기본 16000)
            language: 언어 코드 (기본 ko)

        Returns:
            인식된 텍스트
        """
        try:
            # float32 -> int16 변환
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # WAV 파일로 변환
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            wav_buffer.seek(0)
            audio_bytes = wav_buffer.read()

            # Gemini에 오디오 전송
            lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
            lang_name = lang_map.get(language, "한국어")

            prompt = f"""이 오디오 파일에서 사람이 말하는 음성을 {lang_name}로 받아쓰기 해주세요.

중요 규칙:
1. 음성이 없거나 무음이면 정확히 "SILENCE"만 출력
2. 음성이 있으면 받아쓴 텍스트만 출력 (따옴표 없이)
3. 다른 설명이나 주석 없이 결과만 출력"""

            # 파일 업로드
            audio_file = self.client.files.upload(
                file=io.BytesIO(audio_bytes),
                config={"mime_type": "audio/wav"}
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, audio_file]
            )

            text = response.text.strip()
            # 따옴표 제거
            text = text.strip('"\'')

            # 무음 감지
            if text.upper() == "SILENCE" or "silence" in text.lower():
                return ""

            return text

        except Exception as e:
            print(f"Gemini 음성 인식 오류: {e}")
            return ""


if __name__ == "__main__":
    # 테스트
    import sounddevice as sd

    print("Gemini 음성 인식 테스트")
    print("3초 동안 말해주세요...")

    duration = 3
    sample_rate = 16000

    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()

    audio = audio.flatten()
    print(f"녹음 완료: {len(audio)} 샘플")

    recognizer = GeminiSpeechRecognizer()
    text = recognizer.transcribe(audio, sample_rate, "ko")
    print(f"인식 결과: {text}")
