import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib

# 한글 폰트 설정
matplotlib.rc('font', family=['AppleGothic', 'DejaVu Sans'])
plt.rcParams['axes.unicode_minus'] = False

# KOSIS OpenAPI 인증키와 URL (예시)
API_KEY = '여기에_본인_API_KEY_입력'
url = f'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey={API_KEY}&format=json&jsonVD=Y&userStatsId=your_userStatsId'

# 실제 userStatsId, 통계코드 등은 KOSIS에서 확인 필요
response = requests.get(url)
data_json = response.json()

# 데이터 파싱 (예시: 연도별 인구수 추출)
years = []
population = []
for item in data_json:
    years.append(int(item['PRD_DE']))  # 연도
    population.append(int(item['DT'])) # 인구수

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