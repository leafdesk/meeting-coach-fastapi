import io
import os
import wave
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
import platform

def get_sample_rate(file_path):
    """WAV 파일의 샘플 레이트를 확인합니다."""
    with wave.open(file_path, "rb") as wf:
        sample_rate = wf.getframerate()
    return sample_rate


def convert_to_mono(audio):
    """오디오 파일을 모노로 변환합니다."""
    if audio.channels != 1:
        audio = audio.set_channels(1)
    return audio


def resample_audio(audio, target_sample_rate=48000):
    """오디오 파일을 리샘플링합니다."""
    if audio.frame_rate != target_sample_rate:
        audio = audio.set_frame_rate(target_sample_rate)
    return audio


def convert_to_16bit(audio):
    """WAV 파일을 16비트 샘플로 변환합니다."""
    return audio.set_sample_width(2)  # 16비트 샘플


def transcribe_audio_chunk(audio_chunk, sample_rate, client):
    """Google Cloud Speech-to-Text API를 사용하여 음성을 텍스트로 변환합니다."""
    with io.BytesIO() as audio_file:
        audio_chunk.export(audio_file, format="wav")
        audio_file.seek(0)
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code="ko-KR",
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)

    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)

    return transcripts


def transcribe_audio_file(file_path):
    """오디오 파일을 텍스트로 변환합니다."""
    
    if platform.system() == "Darwin":  # macOS
        api_key_path = "./apiKey/myKey.json"
    else:  # AWS EC2 Ubuntu
        api_key_path = "/home/ubuntu/meeting-coach-fastapi/apiKey/myKey.json"
    
    client = speech.SpeechClient.from_service_account_file(api_key_path)

    sample_rate = get_sample_rate(file_path)
    audio = AudioSegment.from_file(file_path)
    audio = convert_to_mono(audio)
    audio = resample_audio(audio, target_sample_rate=sample_rate)
    audio = convert_to_16bit(audio)

    chunk_length_ms = 30000  # 30초
    all_transcripts = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i : i + chunk_length_ms]
        transcripts = transcribe_audio_chunk(chunk, sample_rate, client)
        all_transcripts.extend(transcripts)

    return all_transcripts
