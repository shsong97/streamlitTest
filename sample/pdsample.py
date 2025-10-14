import pandas as pd
import streamlit as st

# 예시 데이터 딕셔너리
data = {
    '이름': ['김철수', '박영희', '이민준', '최지영', '정수환'],
    '나이': [25, 30, 22, 35, 28],
    '도시': ['서울', '부산', '서울', '인천', '부산']
}

# DataFrame 생성
df = pd.DataFrame(data)

st.dataframe(df)  # DataFrame을 사용하여 데이터프레임 표시
st.json(df.to_dict(orient='records'))  # DataFrame을 JSON 형식으로 표시
st.write(df)  # DataFrame을 사용하여 일반 출력
st.metric("평균 나이", df['나이'].mean(), delta=1.5)  # DataFrame의 평균 나이를 메트릭으로 표시
st.caption("이것은 DataFrame을 사용한 예시입니다.")  # 캡션 추가
st.text("DataFrame을 사용하여 다양한 Streamlit 컴포넌트를 시연합니다.")  # 텍스트 추가
st.markdown("### DataFrame을 사용한 Streamlit 컴포넌트 시연")  # 마크다운 추가
st.code("import pandas as pd\nimport streamlit as st\n\n# DataFrame 생성\n...")  # 코드 블록 추가
st.json(df.to_dict())  # DataFrame을 JSON 형식으로 표시

# 숫자 100개를 임의로 생성하는 DataFrame 생성
import numpy as np
np.random.seed(0)
random_data = pd.DataFrame(np.random.randn(100, 3), columns=['A', 'B', 'C'])
st.line_chart(random_data)  # 라인 차트 표시
st.bar_chart(random_data)  # 바 차트 표시
st.area_chart(random_data)  # 영역 차트 표시
