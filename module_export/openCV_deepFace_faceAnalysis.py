import cv2
from deepface import DeepFace
from collections import Counter

def analyze_emotions_from_video(video_file: str):
    """
    비디오 파일에서 감정을 분석하고 감정 백분율을 반환합니다.
    """
    
    # 비디오 캡처 객체 생성
    cap = cv2.VideoCapture(video_file)

    # 감정 빈도 카운터 초기화
    emotion_counts = Counter()
    total_faces_detected = 0  # 감정을 분석한 얼굴의 총 수

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # OpenCV를 사용하여 얼굴 인식
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        detected_faces = faces.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

        # 각 얼굴에 대해 감정 분석 수행
        for (x, y, w, h) in detected_faces:
            face = frame[y:y+h, x:x+w]
            
            try:
                result = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)
                # 감정 결과 추출
                emotion = result[0]['dominant_emotion']
                emotion_counts[emotion] += 1
                total_faces_detected += 1
            
            except Exception as e:
                print(f"Error analyzing face: {e}")
                continue

    # 비디오 캡처 해제
    cap.release()

    # 감정 퍼센티지 계산 및 반환
    if total_faces_detected > 0:
        emotion_percentages = {emotion: (count / total_faces_detected) * 100 for emotion, count in emotion_counts.items()}
        return emotion_percentages
    else:
        return {}
