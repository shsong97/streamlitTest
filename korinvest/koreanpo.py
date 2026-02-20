import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from util.plotfont import apply_nanumgothic_font

apply_nanumgothic_font()

# .env 파일이 있으면 로드 (개발 환경)
load_dotenv()

# 환경변수에서 KOSIS API 키와 통계 ID 읽기
API_KEY = os.environ.get('KOSIS_API_KEY')
USER_STATS_ID = os.environ.get('KOSIS_USER_STATS_ID')

if not API_KEY or not USER_STATS_ID:
    st.error('환경변수 KOSIS_API_KEY 또는 KOSIS_USER_STATS_ID가 설정되어 있지 않습니다.')
else:
    url = (
        'https://kosis.kr/openapi/statisticsData.do?'
        f'method=getList&apiKey={API_KEY}&format=json&jsonVD=Y&userStatsId={USER_STATS_ID}'
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data_json = response.json()
    except Exception as e:
        st.error(f'KOSIS API 호출 오류: {e}')
        data_json = None

    if data_json:
        # 데이터 파싱 (예시: 연도별 인구수 추출)
        years = []
        population = []
        for item in data_json:
            try:
                years.append(int(item.get('PRD_DE')))
                population.append(int(item.get('DT')))
            except Exception:
                continue

        if years and population:
            # 최근 3년만 추출
            df = pd.DataFrame({'연도': years, '인구수': population})
            df = df.sort_values('연도').tail(3)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(df['연도'], df['인구수'], marker='o')
            ax.set_title('한국 최근 3년 인구 변화 (KOSIS API)')
            ax.set_xlabel('연도')
            ax.set_ylabel('인구수')
            ax.grid(True)

            st.pyplot(fig)
        else:
            st.warning('KOSIS로부터 유효한 인구 데이터를 찾을 수 없습니다.')