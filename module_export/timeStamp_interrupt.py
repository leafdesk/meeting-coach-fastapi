import pandas as pd
from collections import defaultdict

def detect_interruptions(df):
    """
    대화 데이터프레임을 받아서 화자별 끼어들기 횟수를 카운트하는 순수 함수.

    Args:
        df (pd.DataFrame): 대화 데이터를 포함한 DataFrame. 
                           컬럼: ['start_time', 'end_time', 'speaker', 'dialogue']

    Returns:
        dict: 화자별 끼어들기 횟수를 담은 딕셔너리.
              예: {"Speaker 1": 3, "Speaker 2": 5}
    """
    
    # 화자별 끼어들기 횟수 저장용 딕셔너리
    interrupter_count = defaultdict(int)

    # 끼어들기 검출
    for i in range(1, len(df)):
        # 현재 발화의 'dialogue'가 비어있는 경우 건너뛰기
        if pd.isna(df.loc[i, 'dialogue']) or df.loc[i, 'dialogue'].strip() == '':
            continue

        # 현재 발화 화자와 이전 발화 화자가 다른 경우 끼어들기 검토
        if df.loc[i, 'speaker'] != df.loc[i - 1, 'speaker']:
            # 이전 발화 종료 시간과 현재 발화 시작 시간 비교
            prev_end = df.loc[i - 1, 'end_time']
            curr_start = df.loc[i, 'start_time']

            # 발화 시작 시간이 이전 발화 종료 시간보다 0.3초 이내인 경우 끼어들기로 간주
            if curr_start - prev_end <= 0.3:
                interrupter_count[df.loc[i, 'speaker']] += 1

    return dict(interrupter_count)
