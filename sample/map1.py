import streamlit as st
import numpy as np
import pandas as pd

# 랜덤 위도,경도 데이터 생성
map_data = pd.DataFrame(
    np.random.randn(100, 2) / [50, 50] + [37.57, 127],
    columns=['lat', 'lon'])

# 지도 그리기
st.map(map_data)