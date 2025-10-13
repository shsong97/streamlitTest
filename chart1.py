import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from matplotlib import font_manager, rc

# 폰트 경로 지정
font_path = 'static/NanumGothic.ttf'
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

# 한글 폰트 설정 (macOS 기준)
matplotlib.rc('font', family=['NanumGothic'])
plt.rcParams['axes.unicode_minus'] = False

st.sidebar.title("주가 데이터셋")


# 두 종목 데이터 다운로드
symbols = ['005930.KS', '000660.KS','033160.KS','033640.KS','222800.KS','240810.KS','317450.KS','064400.KS']
lables = ['삼성전자', 'SK하이닉스', '엠케이전자', '네패스', '심텍', '원익IPS','명인제약','LG씨엔에스']

data = yf.download(symbols, period='6mo', auto_adjust=True)["Close"]

# 각 종목별로 개별 차트 그리기
for code, label in zip(symbols, lables):
    st.sidebar.link_button(label, f"https://finance.naver.com/item/sise.naver?code={code.split('.')[0]}")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data.index, data[code], label=label, color=np.random.rand(3,))
    ax.set_title(f'{label} 종가 차트')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (KRW)')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

