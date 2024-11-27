from fastapi import FastAPI, UploadFile, File
from module_export.change2wav import mp4_to_wav
from module_export.diarization_cpu import diarize_audio
from module_export.speaker_divide import (
    split_audio_by_speaker,
    load_diarization_results,
)
from module_export.speech2text import transcribe_audio
from module_export.speech2text_fullText import transcribe_audio_file
import os
import platform
from pydantic import BaseModel
from module_export.LLMsumurize import summarize_text  # 추가된 함수 임포트
from module_export.LLMgenerate import generate_quiz  # 추가된 함수 임포트
# from module_export.speechBrain_voiceEmotion import (
#     analyze_audio_emotion,
# )  # 추가된 함수 임포트
# from module_export.openCV_deepFace_faceAnalysis import analyze_emotions_from_video
import uvicorn  # 추가된 import

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


class SpeechToTextFullRequest(BaseModel):
    """
    전체 음성을 텍스트로 변환 요청 모델.
    """

    wav_file_path: str  # 파일 경로를 문자열로 받음


@app.post("/fastapi/speech-to-text/full")
async def speech_to_text_full(request: SpeechToTextFullRequest):
    """
    전체 WAV 파일을 텍스트로 변환합니다.
    """

    try:
        # 환경에 따라 저장 디렉토리 결정
        if platform.system() == "Darwin":  # macOS
            storage_dir = "./res"
        else:  # AWS EC2 Ubuntu에서 실행 중으로 가정
            storage_dir = "/home/ubuntu/res"

        os.makedirs(storage_dir, exist_ok=True)  # 디렉토리 생성

        # 음성을 텍스트로 변환
        transcripts = transcribe_audio_file(request.wav_file_path)

        # 전체 텍스트를 fullText.txt 파일에 저장
        output_file_path = os.path.join(storage_dir, "fullText.txt")
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(transcripts))

        return {
            "message": "Full text conversion completed",
            "output_file": output_file_path,
        }
    except Exception as e:
        return {"error": str(e)}


class SummarizeRequest(BaseModel):
    """
    텍스트 요약 요청 모델.
    """

    file_path: str  # 요약할 텍스트 파일 경로


# LLM을 이용한 텍스트 요약
@app.post("/fastapi/summarize")
async def llm_summarize(request: SummarizeRequest):
    """
    텍스트 파일을 요약합니다.
    """

    try:
        # 텍스트 요약 생성
        summary = summarize_text(request.file_path)

        return {
            "message": "Text summarized",
            "summary": summary,
        }
    except Exception as e:
        return {"error": str(e)}


class QuizRequest(BaseModel):
    """
    퀴즈 생성을 위한 요청 모델.
    """

    summary_text: str  # 요약된 텍스트


# LLM을 이용한 퀴즈 생성
@app.post("/fastapi/generate-quiz")
async def llm_generate_quiz(request: QuizRequest):
    """
    요약된 텍스트를 기반으로 퀴즈를 생성합니다.
    """

    try:
        # 퀴즈 생성
        quiz = generate_quiz(request.summary_text)

        return {
            "message": "Quiz generated",
            "quiz": quiz,
        }
    except Exception as e:
        return {"error": str(e)}


# 화자 검증
@app.post("/fastapi/speaker-verification")
async def speaker_verification(file: str, db_file: str):
    return {"message": "Speaker verification completed", "similarity": 0.0}


# # 새로운 요청 모델 클래스 생성
# class AudioEmotionRequest(BaseModel):
#     """
#     음성 감정 분석 요청 모델.
#     """

#     wav_file_path: str  # WAV 파일 경로를 문자열로 받음


# # 음성 감정 분석
# @app.post("/fastapi/audio-emotion-analysis")
# async def audio_emotion_analysis(request: AudioEmotionRequest):
#     """
#     음성 감정 분석을 수행합니다.
#     """

#     # 환경에 따라 저장 디렉토리 결정
#     if platform.system() == "Darwin":  # macOS
#         storage_dir = "./res"
#     else:  # AWS EC2 Ubuntu에서 실행 중으로 가정
#         storage_dir = "/home/ubuntu/res"

#     os.makedirs(storage_dir, exist_ok=True)  # 디렉토리 생성

#     # 요청에서 WAV 파일 경로 가져오기
#     temp_file_path = request.wav_file_path

#     try:
#         # 감정 분석 수행
#         analysis_results = analyze_audio_emotion(temp_file_path)

#         return {
#             "message": "Audio emotion analysis completed",
#             "results": analysis_results,
#         }
#     except Exception as e:
#         return {"error": str(e)}


# # Define the request model for video emotion analysis
# class VideoEmotionRequest(BaseModel):
#     video_file_path: str  # 비디오 파일 경로를 문자열로 받음


# # 영상 감정 분석
# @app.post("/fastapi/video-emotion-analysis")
# async def video_emotion_analysis(request: VideoEmotionRequest):
#     """
#     Analyze emotions from the uploaded video file.
#     """
#     # 환경에 따라 저장 디렉토리 결정
#     storage_dir = "./res"  # Adjust as necessary
#     os.makedirs(storage_dir, exist_ok=True)

#     # 비디오 파일 저장
#     video_file_path = request.video_file_path  # Use the path from the request
#     with open(video_file_path, "rb") as f:
#         video_data = f.read()

#     # Save the video file to the storage directory
#     saved_video_path = os.path.join(storage_dir, os.path.basename(video_file_path))
#     with open(saved_video_path, "wb") as f:
#         f.write(video_data)

#     # 감정 분석 수행
#     emotions = analyze_emotions_from_video(saved_video_path)

#     return {
#         "message": "Video emotion analysis completed",
#         "emotions": emotions,
#     }


# 화자별 끼어들기 횟수 반환
@app.post("/fastapi/timestamp-interrupt")
async def timestamp_interrupt(file: str):
    return {"message": "Interrupt count calculated", "interrupt_count": 0}


# 피드백 생성
@app.post("/fastapi/generate-feedback")
async def generate_feedback(text: str):
    return {"message": "Feedback generated", "feedback": ""}


if __name__ == "__main__":  # main 함수 추가
    uvicorn.run(app, host="0.0.0.0", port=4000, log_level="info")  # FastAPI 서버 실행
