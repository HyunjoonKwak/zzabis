"""
OpenAI Whisper API 기반 음성 인식
"""

import io
import wave
import numpy as np
from openai import OpenAI
from config import get_openai_api_key


class OpenAISpeechRecognizer:
    """OpenAI Whisper를 사용한 음성 인식"""

    def __init__(self):
        api_key = get_openai_api_key()
        if not api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다")

        self.client = OpenAI(api_key=api_key)

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
            wav_buffer.name = "audio.wav"  # OpenAI API requires filename

            # OpenAI Whisper API 호출
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_buffer,
                language=language,
                response_format="text"
            )

            text = response.strip()
            return text

        except Exception as e:
            print(f"OpenAI 음성 인식 오류: {e}")
            return ""


if __name__ == "__main__":
    # 테스트
    import sounddevice as sd

    print("OpenAI Whisper 음성 인식 테스트")
    print("3초 동안 말해주세요...")

    duration = 3
    sample_rate = 16000

    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()

    audio = audio.flatten()
    print(f"녹음 완료: {len(audio)} 샘플")

    recognizer = OpenAISpeechRecognizer()
    text = recognizer.transcribe(audio, sample_rate, "ko")
    print(f"인식 결과: {text}")
