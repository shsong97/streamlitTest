# streamlit_app_page_title: 차트 검색
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from util.plotfont import apply_nanumgothic_font

apply_nanumgothic_font()

# 네이버 주식 목록 예시 (실제 네이버 종목코드로 교체 필요)
DEFAULT_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "LG씨엔에스": "064400.KS",
    "엠케이전자": "033160.KS",
    "네패스": "033640.KS",
    "심텍": "222800.KS",
    "원익IPS": "240810.KS",
    "명인제약": "317450.KS",
}

st.title("종목 1개월 차트")

# 세션 상태에 종목 목록 저장 및 관리
if "naver_stocks" not in st.session_state:
    st.session_state.naver_stocks = DEFAULT_STOCKS.copy()

add_stock = st.text_input("종목명과 코드 추가 (예: 'LG화학,051910.KS')")

if add_stock:
    try:
        name, code = add_stock.split(",")
        st.session_state.naver_stocks[name.strip()] = code.strip()
        st.success(f"{name.strip()} 종목이 추가되었습니다.")
    except Exception:
        st.error("입력 형식이 올바르지 않습니다. 예: 'LG화학,051910.KS'")

selected_stock = st.selectbox("종목 선택 또는 검색", list(st.session_state.naver_stocks.keys()))

# 차트 그리기
if selected_stock:
    code = st.session_state.naver_stocks[selected_stock]
    end = datetime.today()
    start = end - timedelta(days=30)
    df = yf.download(code, start=start, end=end, auto_adjust=True)
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(df.index, df['Close'], marker='o')
        ax.set_title(f"{selected_stock} 1개월 종가 차트")
        ax.set_xlabel("날짜")
        ax.set_ylabel("종가")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("데이터를 불러올 수 없습니다.")