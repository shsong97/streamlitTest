import streamlit as st

create_page = st.Page("pages/chartsearch.py", title="종목검색(1개월)", icon=":material/add_circle:")
delete_page = st.Page("pages/chart6mo.py", title="6개월 차트 리스트", icon=":material/delete:")

pg = st.navigation([create_page, delete_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()

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

fontRegistered()