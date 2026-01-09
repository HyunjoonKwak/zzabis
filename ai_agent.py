"""
MacVoice AI Agent - OpenAI GPT-4o-mini 기반 스타일 변환
타이핑 전용 모드
"""

from openai import OpenAI
from config import get_openai_api_key

# OpenAI 설정
MODEL = "gpt-4o-mini"


class AIAgent:
    """OpenAI GPT-4o-mini 기반 스타일 변환 에이전트"""

    def __init__(self):
        api_key = get_openai_api_key()
        if not api_key:
            print("⚠️  OpenAI API 키가 설정되지 않았습니다!")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def transform_style(self, text: str, style: str) -> str:
        """텍스트 스타일 변환"""
        if not self.client:
            return text

        # 그대로 입력이면 맞춤법만 수정
        if style == "normal":
            return self._correct_spelling_only(text)

        style_prompts = {
            "formal": "격식체 존댓말로 바꿔줘. (예: ~습니다, ~합니다)",
            "polite": "공손한 존댓말로 바꿔줘. (예: ~해요, ~세요)",
            "casual": "친구한테 하는 반말로 바꿔줘. (예: ~야, ~어, ~지)",
            "cute": "귀여운 말투로 바꿔줘. (예: ~요, ~용, ~당, ~해용)",
            "aegyo": "애교 섞인 말투로 바꿔줘. (예: ~잉, ~쪄, ~행, 응응)",
            "romantic": "다정하고 따뜻한 말투로 바꿔줘. (예: ~해줄게, ~고 싶어)",
            "cold": "쿨하고 담담한 말투로 바꿔줘. (예: ~임, ~ㅇㅇ, 짧게)",
            "humor": "재미있고 유머러스하게 바꿔줘. 약간의 드립이나 재치 추가.",
            "pro": "비즈니스 전문가 말투로 바꿔줘. (예: ~드립니다, ~하겠습니다)",
        }

        style_instruction = style_prompts.get(style, "")
        if not style_instruction:
            return self._correct_spelling_only(text)

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"텍스트의 말투만 바꿔줘. 내용은 절대 바꾸지 마. {style_instruction} 맞춤법도 수정해. 변환된 텍스트만 출력하고 다른 설명은 하지 마."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )
            result = response.choices[0].message.content.strip()
            # 따옴표 제거
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            if result.startswith("'") and result.endswith("'"):
                result = result[1:-1]
            return result
        except Exception as e:
            print(f"스타일 변환 오류: {e}")
            return text

    def _correct_spelling_only(self, text: str) -> str:
        """맞춤법만 수정 (내부용)"""
        if not self.client:
            return text

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "다음 한국어 텍스트의 맞춤법과 띄어쓰기를 수정해줘. 원래 의미를 유지하면서 올바른 맞춤법으로 수정해. 수정된 텍스트만 출력하고 다른 설명은 하지 마."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            corrected = response.choices[0].message.content.strip()
            # 따옴표 제거
            if corrected.startswith('"') and corrected.endswith('"'):
                corrected = corrected[1:-1]
            if corrected.startswith("'") and corrected.endswith("'"):
                corrected = corrected[1:-1]
            return corrected
        except Exception as e:
            print(f"맞춤법 수정 오류: {e}")
            return text

    def correct_spelling(self, text: str) -> str:
        """맞춤법 수정 (하위 호환용)"""
        return self._correct_spelling_only(text)


if __name__ == "__main__":
    agent = AIAgent()
    test_text = "안녕하세요 오늘 날씨가 좋네요"

    print(f"원본: {test_text}")
    print(f"그대로: {agent.transform_style(test_text, 'normal')}")
    print(f"공적: {agent.transform_style(test_text, 'formal')}")
    print(f"귀엽게: {agent.transform_style(test_text, 'cute')}")
    print(f"정중: {agent.transform_style(test_text, 'polite')}")
