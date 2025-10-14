import streamlit as st
import pandas as pd
import numpy as np

st.write("Streamlit supports a wide range of data visualizations, including [Plotly, Altair, and Bokeh charts](https://docs.streamlit.io/develop/api-reference/charts). 📊 And with over 20 input widgets, you can easily make your data interactive!")

all_users = ["Alice", "Bob", "Charly"]
with st.container(border=True):
    users = st.multiselect("Users", all_users, default=all_users)
    rolling_average = st.toggle("Rolling average")

np.random.seed(42)
data = pd.DataFrame(np.random.randn(20, len(users)), columns=users)
if rolling_average:
    data = data.rolling(7).mean().dropna()

tab1, tab2 = st.tabs(["Chart", "Dataframe"])
tab1.line_chart(data, height=250)
tab2.dataframe(data, height=250, width='stretch')

tab3, tab4 = st.tabs(["Bar chart", "Area chart"])
tab3.bar_chart(data, height=250)
tab4.area_chart(data, height=250)

tab5, tab6 = st.tabs(["Map", "Metrics"])
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=["lat", "lon"],
)
tab5.map(map_data, height=250)
col1, col2, col3 = tab6.columns(3)
col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")


sale, profit = st.columns(2)
sale.metric("Total sales", "1,000,000원", "+ 20%")
profit.metric("Profit", "100,000원", "+ 10,000원")

st.caption("This is a caption that can be used to add context to a chart or metric.")
st.text("This is a text element that can be used to add context to a chart or metric.")
st.markdown("""### This is a markdown element that can be used to add context to a chart or metric." \
## You can use **bold**, *italic*, and other markdown features.
# 1. First item
# 2. Second item
- Third item
- Fourth item
* 4번째 아이템
* 5번째 아이템
* 6번째 아이템
* **7번째 아이템**        
""")
st.code("import streamlit as st\nimport pandas as pd\nimport numpy as np")
st.json({"name": "Streamlit", "type": "library", "stars": 35000})


with st.expander("See code"):
    st.code(
'''import streamlit as st
import pandas as pd
import numpy as np
''')
st.warning("This is a warning message.")
st.error("This is an error message.")
st.success("This is a success message.")
st.info("This is an info message.")
st.sidebar.title("This is a title in the sidebar")
st.sidebar.header("This is a header in the sidebar")
st.sidebar.subheader("This is a subheader in the sidebar")
st.sidebar.text("This is a text in the sidebar")
st.sidebar.markdown("### This is a markdown in the sidebar")