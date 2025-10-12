import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 한글 폰트 설정 (macOS 기준)
matplotlib.rc('font', family=['AppleGothic','DejaVu Sans'])
plt.rcParams['axes.unicode_minus'] = False

st.sidebar.title("대표 IT주 주가 데이터셋")
st.sidebar.link_button("삼성전자", "https://finance.naver.com/item/sise.naver?code=005930")
st.sidebar.link_button("SK하이닉스", "https://finance.naver.com/item/sise.naver?code=000660")

# 두 종목 데이터 다운로드
symbols = ['005930.KS', '000660.KS']
data = yf.download(symbols, period='5y', auto_adjust=True)["Close"]

# 차트 그리기
fig, ax = plt.subplots(figsize=(12, 6))
for code, label in zip(symbols, ["삼성전자", "SK하이닉스"]):
    ax.plot(data.index, data[code], label=label)
ax.set_title('삼성전자 vs SK하이닉스 5년치 종가 비교')
ax.set_xlabel('Date')
ax.set_ylabel('Price (KRW)')
ax.legend()
ax.grid(True)

st.pyplot(fig)

# --------------------------------------------------
st.sidebar.title("대표 바이오주 주가 데이터셋") 
st.sidebar.link_button("삼성바이오로직스", "https://finance.naver.com/item/sise.naver?code=207940")
st.sidebar.link_button("셀트리온", "https://finance.naver.com/item/sise.naver?code=068270")
st.sidebar.link_button("유한양행", "https://finance.naver.com/item/sise.naver?code=000100")

# 대표 바이오주 종목코드 및 이름
symbols = ['207940.KS', '068270.KS', '000100.KS']
labels = ['삼성바이오로직스', '셀트리온', '유한양행']

# 데이터 다운로드
data = yf.download(symbols, period='5y')["Close"]

# 차트 그리기
fig, ax = plt.subplots(figsize=(12, 6))
for code, label in zip(symbols, labels):
    ax.plot(data.index, data[code], label=label)
ax.set_title('대표 바이오주 5년치 종가 비교')
ax.set_xlabel('Date')
ax.set_ylabel('Price (KRW)')
ax.legend()
ax.grid(True)

st.pyplot(fig)

# 상관관계 분석 및 시각화
corr = data.corr()
fig_corr, ax_corr = plt.subplots(figsize=(6, 5))
cax = ax_corr.matshow(corr, cmap='coolwarm')
fig_corr.colorbar(cax)
ax_corr.set_xticks(range(len(labels)))
ax_corr.set_yticks(range(len(labels)))
ax_corr.set_xticklabels(labels, rotation=45, ha='left')
ax_corr.set_yticklabels(labels)
ax_corr.set_title('대표 바이오주 종가 상관관계')

for (i, j), val in np.ndenumerate(corr.values):
    ax_corr.text(j, i, f'{val:.2f}', ha='center', va='center', color='black')

st.pyplot(fig_corr)

# 삼성바이오로직스 단일 종목 데이터 다운로드
symbol = '207940.KS'
data_bio = yf.download(symbol, period='5y')

# 종가와 다른 컬럼(시가, 고가, 저가, 거래량 등) 간 상관관계 분석
cols = ['Open', 'High', 'Low', 'Close', 'Volume']
data_bio_selected = data_bio[cols]
corr_bio = data_bio_selected.corr()

fig_bio, ax_bio = plt.subplots(figsize=(6, 5))
cax = ax_bio.matshow(corr_bio, cmap='coolwarm')
fig_bio.colorbar(cax)
ax_bio.set_xticks(range(len(cols)))
ax_bio.set_yticks(range(len(cols)))
ax_bio.set_xticklabels(cols, rotation=45, ha='left')
ax_bio.set_yticklabels(cols)
ax_bio.set_title('삼성바이오로직스 주가 데이터 상관관계')

for (i, j), val in np.ndenumerate(corr_bio.values):
    ax_bio.text(j, i, f'{val:.2f}', ha='center', va='center', color='black')

st.pyplot(fig_bio)