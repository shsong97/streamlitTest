import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 한글 폰트 설정 (macOS: AppleGothic, 기타: DejaVu Sans)
matplotlib.rc('font', family=['AppleGothic', 'DejaVu Sans'])
plt.rcParams['axes.unicode_minus'] = False

# 최근 3년 인구 데이터 예시 (단위: 천 명)
years = [2022, 2023, 2024]
population = [51780, 51600, 51400]  # 실제 데이터는 최신 통계 참고

df = pd.DataFrame({'연도': years, '인구수': population})

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df['연도'], df['인구수'], marker='o')
ax.set_title('한국 최근 3년 인구 변화')
ax.set_xlabel('연도')
ax.set_ylabel('인구수 (천 명)')
ax.grid(True)

st.pyplot(fig)