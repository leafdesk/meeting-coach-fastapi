import os  # os 모듈 임포트
import torch
from speechbrain.pretrained import SpeakerRecognition

# 1. 모델 로드 (CPU 사용 설정)
device = "cpu"  # CPU 사용
model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="tmp_model").to(device)

def verify_audio_files(audio_file1, audio_file2):
    """두 음성 파일의 유사도를 계산하고 결과를 반환합니다."""
    # 결과를 저장할 디렉토리 생성
    result_dir = "./result"
    os.makedirs(result_dir, exist_ok=True)  # 디렉토리가 없으면 생성

    # 두 음성을 CPU에 맞게 로드
    score, prediction = model.verify_files(audio_file1, audio_file2)

    # 결과 출력
    result = f"Similarity Score: {score}"  # 점수를 변환하지 않고 사용

    # 결과를 ./result/similarity.txt 파일에 저장
    with open(os.path.join(result_dir, "similarity.txt"), "w") as file:
        file.write(result)

    return result
