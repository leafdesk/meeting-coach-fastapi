import os
from openai import OpenAI

# API 키를 파일에서 읽어오기
def get_api_key(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()  # API 키를 반환하고, 불필요한 공백 제거

# OpenAI 클라이언트 설정
api_key = get_api_key("./apiKey/gptKey.txt")  # 파일에서 API 키 읽어오기
client = OpenAI(api_key=api_key)

# 텍스트 파일을 요약하는 함수
def summarize_text(file_path):
    # 텍스트 파일 읽기
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # OpenAI API를 사용하여 텍스트 요약하기
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"한국어 회의 내용을 주요 안건별로 요약해서 삼성 개발팀의 팀장 수준의 회의록을 만들어 주세요.:\n\n{text}"
        }],
        model="gpt-3.5-turbo",
        max_tokens=1500,  # 요약의 최대 토큰 수
        temperature=0.5,  # 창의성 조절
    )

    # 요약 결과 추출
    summary = chat_completion.choices[0].message.content
    return summary
