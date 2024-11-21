from fastapi import FastAPI, UploadFile, File
from module_export.change2wav import mp4_to_wav
import os

app = FastAPI()


@app.get("/fastapi")
async def root():
    return {"message": "Hello from FastAPI"}


# MP4 파일에서 음성만 추출하여 WAV 파일로 변환
@app.post("/fastapi/extract-wav")
async def extract_wav(file: UploadFile = File(...)):
    # 특정 디렉토리에 저장
    storage_dir = "/var/tmp/vmc"
    os.makedirs(storage_dir, exist_ok=True)
    
    temp_file_path = os.path.join(storage_dir, file.filename)
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        wav_file_path = mp4_to_wav(temp_file_path)
        return {"message": "WAV file extracted", "wav_file_path": wav_file_path}
    except Exception as e:
        return {"error": str(e)}


# 화자 분리 및 타임스탬프 반환
@app.post("/fastapi/dialization")
async def dialization(file: str):
    return {
        "message": "Speaker separation completed",
        "data": [],
    }  # starttime, endtime, speaker, dialog


# 화자별 WAV 파일 추출
@app.post("/fastapi/speaker-divide")
async def speaker_divide(file: str):
    return {"message": "Speaker-specific WAV files extracted"}


# 화자 분리된 음성을 텍스트로 변환
@app.post("/fastapi/speech-to-text")
async def speech_to_text(file: str):
    return {"message": "Speech to text conversion completed", "dialog": ""}


# 전체 회의 음성을 텍스트로 변환
@app.post("/fastapi/speech-to-text/full")
async def speech_to_text_full(file: str):
    return {"message": "Full text conversion completed", "summary": ""}


# LLM을 이용한 텍스트 요약
@app.post("/fastapi/summarize")
async def llm_summarize(text: str):
    return {"message": "Text summarized", "summary": ""}


# LLM을 이용한 퀴즈 생성
@app.post("/fastapi/generate-quiz")
async def llm_generate_quiz(text: str):
    return {"message": "Quiz generated", "quiz": []}


# 화자 검증
@app.post("/fastapi/speaker-verification")
async def speaker_verification(file: str, db_file: str):
    return {"message": "Speaker verification completed", "similarity": 0.0}


# 감정 분석
@app.post("/fastapi/emotion-analysis")
async def emotion_analysis(file: str):
    return {"message": "Emotion analysis completed", "emotions": {}}  # 각 감정의 퍼센트


# 화자별 끼어들기 횟수 반환
@app.post("/fastapi/timestamp-interrupt")
async def timestamp_interrupt(file: str):
    return {"message": "Interrupt count calculated", "interrupt_count": 0}


# 피드백 생성
@app.post("/fastapi/generate-feedback")
async def generate_feedback(text: str):
    return {"message": "Feedback generated", "feedback": ""}
