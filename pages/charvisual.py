import streamlit as st

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

st.title("Visualize 종목 차트")

st.session_state.naver_stocks = DEFAULT_STOCKS.copy()
selected_stock = st.selectbox("종목 선택 또는 검색", list(st.session_state.naver_stocks.keys()))

import streamlit as st
from sample.korbacktest import _prepare_indicator_df, run_backtest_and_visualize, buy_combos, sell_combos

if selected_stock:
    code = st.session_state.naver_stocks[selected_stock]
    st.write(f"선택된 종목: {selected_stock} ({code})")
    df = _prepare_indicator_df(code)
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(df.index, df['Close'])
    st.pyplot(plt.gcf())

    st.write("백테스트 결과 및 시각화:")
    result = run_backtest_and_visualize(code, buy_combos=buy_combos, sell_combos=sell_combos, hold_days=5)
    st.write(result)