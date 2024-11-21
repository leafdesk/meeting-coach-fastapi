from fastapi import FastAPI, UploadFile, File
from module_export.change2wav import mp4_to_wav
from module_export.diarization_cpu import diarize_audio
from module_export.speaker_divide import (
    split_audio_by_speaker,
    load_diarization_results,
)
from module_export.speech2text import transcribe_audio
import os
import platform
from pydantic import BaseModel

app = FastAPI()


@app.get("/fastapi")
async def root():
    """
    FastAPI 애플리케이션 Health Check.
    """

    return {"message": "Hello from FastAPI"}


@app.post("/fastapi/extract-wav")
async def extract_wav(file: UploadFile = File(...)):
    """
    MP4 파일에서 음성을 추출합니다.
    """

    # 환경에 따라 저장 디렉토리 결정
    if platform.system() == "Darwin":  # macOS
        storage_dir = "./res"
    else:  # AWS EC2 Ubuntu에서 실행 중으로 가정
        storage_dir = "/home/ubuntu/res"

    os.makedirs(storage_dir, exist_ok=True)

    # 원래 파일 이름으로 저장
    temp_file_path = os.path.join(storage_dir, file.filename)

    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    try:
        # mp4_to_wav 함수를 호출하여 WAV 파일로 변환
        wav_file_path = mp4_to_wav(temp_file_path)
        print("wav_file_path", wav_file_path)

        return {"message": "WAV file extracted", "wav_file_path": wav_file_path}
    except Exception as e:
        return {"error": str(e)}


class DiarizationRequest(BaseModel):
    """
    화자 분리 요청 모델. (엑셀 파일 생성)
    """

    wav_file_path: str
    num_speakers: int


@app.post("/fastapi/diarization")
async def diarization(request: DiarizationRequest):
    """
    WAV 파일에서 화자 분리를 수행합니다. (엑셀 파일 생성)
    """

    try:
        # 환경에 따라 저장 디렉토리 결정
        if platform.system() == "Darwin":  # macOS
            storage_dir = "./res"
        else:  # AWS EC2 Ubuntu에서 실행 중으로 가정
            storage_dir = "/home/ubuntu/res"

        os.makedirs(
            storage_dir, exist_ok=True
        )  # Create the directory if it doesn't exist

        # diarize_audio 함수 호출
        output_file = diarize_audio(
            request.num_speakers, request.wav_file_path, storage_dir
        )  # Pass storage_dir

        return {"message": "Speaker separation completed", "output_file": output_file}
    except Exception as e:
        return {"error": str(e)}


class SpeakerDivideRequest(BaseModel):
    """
    화자 분리 요청 모델. (화자별 음성 파일 생성)
    """

    diarization_excel: str
    wav_file_path: str


@app.post("/fastapi/speaker-divide")
async def speaker_divide(request: SpeakerDivideRequest):
    """
    화자별로 음성을 나누어 저장합니다. (화자별 음성 파일 생성)
    """

    # 환경에 따라 저장 디렉토리 결정
    if platform.system() == "Darwin":  # macOS
        storage_dir = "./res"
    else:  # AWS EC2 Ubuntu에서 실행 중으로 가정
        storage_dir = "/home/ubuntu/res"

    os.makedirs(storage_dir, exist_ok=True)

    # wav_file_path에서 파일을 읽어오기
    temp_file_path = request.wav_file_path

    try:
        # 다이어리제이션 결과를 엑셀에서 불러오기
        diarization_results = load_diarization_results(request.diarization_excel)

        # 화자별 음성 분리
        split_audio_by_speaker(temp_file_path, diarization_results, storage_dir)

        return {"message": "Speaker-specific audio files extracted"}
    except Exception as e:
        return {"error": str(e)}


class SpeechToTextRequest(BaseModel):
    """
    음성을 텍스트로 변환 요청 모델.
    """

    wav_file_path: str
    diarization_excel: str


@app.post("/fastapi/speech-to-text")
async def speech_to_text(request: SpeechToTextRequest):
    """
    WAV 파일을 텍스트로 변환합니다. (엑셀 파일에 텍스트 삽입)
    """
    
    try:
        # 환경에 따라 저장 디렉토리 결정
        if platform.system() == "Darwin":  # macOS
            storage_dir = "./res"
        else:  # AWS EC2 Ubuntu에서 실행 중으로 가정
            storage_dir = "/home/ubuntu/res"

        os.makedirs(storage_dir, exist_ok=True)  # 디렉토리 생성

        # 음성을 텍스트로 변환
        output_file = transcribe_audio(request.wav_file_path, request.diarization_excel)

        return {
            "message": "Speech to text conversion completed",
            "output_file": output_file,
        }
    except Exception as e:
        return {"error": str(e)}


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
