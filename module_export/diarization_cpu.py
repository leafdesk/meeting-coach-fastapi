import torchaudio
import pandas as pd
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import os

# 여기에 본인의 액세스 토큰을 입력하세요
access_token = "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"


import logging  # 추가: logging 모듈 임포트

# 로거 설정
logging.basicConfig(level=logging.INFO)  # 추가: 로깅 레벨 설정
logger = logging.getLogger(__name__)  # 추가: 로거 인스턴스 생성


def diarize_audio(num_speakers: int, audio_file_path: str, storage_dir: str):
    logger.info("화자 분리 모델 로드 중...")  # 로그 추가
    # 사전 훈련된 화자 분리 모델 로드
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=access_token
    )

    logger.info("오디오 파일 로드 중...")  # 로그 추가
    # 오디오 파일 로드
    waveform, sample_rate = torchaudio.load(audio_file_path)

    # 진행 상황을 확인하기 위해 ProgressHook 사용
    with ProgressHook() as hook:
        logger.info("화자 분리 추론 실행 중...")  # 로그 추가
        # 전체 파일에 대해 추론 실행
        diarization = pipeline(
            {"waveform": waveform, "sample_rate": sample_rate},
            hook=hook,
            num_speakers=num_speakers,
        )

    # 결과를 저장할 리스트 초기화
    results = []

    # 화자 분리 결과를 리스트에 저장
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        result_line = {
            "start": turn.start,
            "stop": turn.end,
            "speaker": f"speaker_{speaker}",
        }
        results.append(result_line)

    # DataFrame 생성
    df = pd.DataFrame(results)

    logger.info("엑셀 파일로 저장 중...")  # 로그 추가
    # DataFrame을 엑셀 파일로 저장
    output_file = os.path.join(storage_dir, "fullText.xlsx")
    df.to_excel(output_file, index=False)  # 인덱스 없이 저장

    logger.info("작업 완료, 결과 파일 경로: %s", output_file)  # 로그 추가
    return output_file  # 결과 파일 경로 반환
