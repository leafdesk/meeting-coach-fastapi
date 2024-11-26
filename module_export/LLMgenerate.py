import pandas as pd
from openai import OpenAI
import json  # 추가: JSON 파싱을 위한 모듈 임포트

# API 키를 파일에서 읽어오기
def get_api_key(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()  # API 키를 반환하고, 불필요한 공백 제거

# OpenAI 클라이언트 설정
api_key = get_api_key("./apiKey/gptKey.txt")  # 파일에서 API 키 읽어오기
client = OpenAI(api_key=api_key)

# 퀴즈 생성 함수
def generate_quiz(summary_text):
    # 퀴즈 생성 요청
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"다음 요약 내용을 기반으로 객관식 퀴즈 3~5개를 생성하고, 각 문제의 정답을 포함한 JSON.stringify 형식의 응답을 만들어주세요."
                       f"요약 내용: {summary_text}"
                       f"JSON 응답 형식은 다음과 같습니다:"
                       f'{{"questions":[{{"question":"<문제 내용>","options":["<선택지1>","<선택지2>","<선택지3>","<선택지4>"],"answer":{{<정답의 index>}}}},...]}}'
        }],
        model="gpt-3.5-turbo",
        max_tokens=1000,
        temperature=0.5,
    )

    # 퀴즈 및 정답 추출
    quiz_content = chat_completion.choices[0].message.content
    return json.loads(quiz_content)  # 수정: JSON 문자열을 파싱하여 반환
