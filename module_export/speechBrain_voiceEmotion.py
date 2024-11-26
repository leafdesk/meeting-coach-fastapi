import json
from pydub import AudioSegment
from speechbrain.inference.diarization import Speech_Emotion_Diarization
from collections import Counter

model = Speech_Emotion_Diarization.from_hparams(
    source="speechbrain/emotion-diarization-wavlm-large",
    savedir="speechbrain_models/emotion-diarization-wavlm-large",
)

classifier = Speech_Emotion_Diarization.from_hparams(
    source="speechbrain_models/emotion-diarization-wavlm-large",
    savedir="speechbrain_models/emotion-diarization-wavlm-large",
)


def analyze_emotion_segments(audio: AudioSegment, segment_duration=30):
    """
    주어진 오디오를 세그먼트로 나누고 감정 분석을 수행합니다.

    :param audio: AudioSegment 객체
    :param segment_duration: 세그먼트 길이 (초)
    :return: 감정 분석 결과 리스트
    """
    results = []

    # 30초 단위로 오디오 분할 및 감정 분석
    for i in range(0, len(audio), segment_duration * 1000):  # pydub은 ms 단위 사용
        segment = audio[i : i + segment_duration * 1000]

        # 각 세그먼트의 시간 보정
        base_time = i / 1000  # ms를 초로 변환

        # 세그먼트를 분석에 사용 (임시 파일을 현재 작업 디렉토리에 저장)
        temp_segment_path = "../resource/temp_segment.wav"
        segment.export(temp_segment_path, format="wav")
        diary = classifier.diarize_file(temp_segment_path)

        # 분석 결과에 시간 보정을 적용하여 저장
        for entry in diary[temp_segment_path]:
            adjusted_entry = {
                "start": entry["start"] + base_time,
                "end": entry["end"] + base_time,
                "emotion": entry["emotion"],
            }
            results.append(adjusted_entry)

    return results


def calculate_emotion_time_percentage(results, total_duration):
    """
    감정별 시간과 퍼센티지를 계산합니다.

    :param results: 감정 분석 결과 리스트
    :param total_duration: 전체 오디오 길이 (초)
    :return: 감정 비율과 시간
    """
    emotion_time = {
        emotion: 0 for emotion in set(entry["emotion"] for entry in results)
    }

    # 각 세그먼트에서 감정에 해당하는 시간 누적
    for entry in results:
        emotion_time[entry["emotion"]] += entry["end"] - entry["start"]

    # 전체 시간에 대한 퍼센티지 계산
    emotion_percentage = {
        emotion: (time / total_duration) * 100 for emotion, time in emotion_time.items()
    }

    return emotion_percentage, emotion_time


def analyze_audio_emotion(audio_path):
    """
    주어진 오디오 파일 경로에서 감정 분석을 수행합니다.

    :param audio_path: 오디오 파일 경로 (WAV 형식)
    :return: 감정 분석 결과 딕셔너리
    """
    # 오디오 파일 로드
    audio = AudioSegment.from_wav(audio_path)
    total_duration = len(audio) / 1000  # 전체 시간 (초 단위)

    # 감정 분석 수행
    results = analyze_emotion_segments(audio)

    # 감정별 시간과 퍼센티지 계산
    emotion_percentage, emotion_time = calculate_emotion_time_percentage(
        results, total_duration
    )

    # 전체 분석 결과 저장할 딕셔너리
    emotion_analysis_results = {
        "audio_path": audio_path,
        "emotion_percentage": emotion_percentage,
        "emotion_time": emotion_time,
        "segments": results,
    }

    return emotion_analysis_results


def save_results_to_json(results, result_path="emotion_analysis_results.json"):
    """
    분석 결과를 JSON 파일로 저장합니다.

    :param results: 분석 결과 딕셔너리
    :param result_path: 저장할 JSON 파일 경로
    """
    with open(result_path, "w") as json_file:
        json.dump(results, json_file, indent=4)
