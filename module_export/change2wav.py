import os
from moviepy.editor import AudioFileClip


def mp4_to_wav(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    if not file_path.endswith(".mp4"):
        raise ValueError("The provided file is not an MP4 file.")

    # WAV 파일 경로 생성
    wav_file = file_path.replace(".mp4", ".wav")

    # MP4에서 WAV로 변환
    audio = AudioFileClip(file_path)
    audio.write_audiofile(wav_file)
    audio.close()  # 리소스 해제

    return wav_file
