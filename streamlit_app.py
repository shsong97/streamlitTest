import streamlit as st
# 한글폰트 적용
# 폰트 적용
import os
import matplotlib.font_manager as fm  # 폰트 관련 용도 as fm

@st.cache_data
def fontRegistered():
    font_dirs = [os.getcwd() + '/static/']  # 폰트가 저장된 경로
    font_files = fm.findSystemFonts(fontpaths=font_dirs)

    for font_file in font_files:
        fm.fontManager.addfont(font_file)
    fm._load_fontmanager(try_read_cache=False)

# fontRegistered()

chartsearch = st.Page("pages/chartsearch.py", title="종목검색(1개월)", icon="➕")
chart6mo = st.Page("pages/chart6mo.py", title="6개월 차트 리스트", icon="🗑️")
irisdata = st.Page("sample/irisdata.py", title="아이리스 데이터", icon="🌸")
streamlistteest = st.Page("sample/streamlittest.py", title="스트림리트 테스트", icon="📋")
pdsample = st.Page("sample/pdsample.py", title="판다스 샘플", icon="📊")
loginauth = st.Page("pages/loginauth.py", title="로그인 인증", icon="🔒")
chartvisual = st.Page("pages/charvisual.py", title="Visualize 종목 차트", icon="📈")

pg = st.navigation([loginauth, chartsearch, chart6mo, chartvisual,
                    irisdata, streamlistteest, pdsample, ])
st.set_page_config(page_title="Streamlit을 이용한 데이터 분석", page_icon="🐳")
pg.run()
