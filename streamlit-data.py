# streamlit_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# 1. 제목과 설명
# -------------------------------
st.title("데이터 시각화 대시보드")
st.markdown("CSV 파일을 업로드하고, 데이터를 시각화해보세요!")

# -------------------------------
# 2. 데이터 업로드
# -------------------------------
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("데이터 미리보기:")
    st.dataframe(df)

    # -------------------------------
    # 3. 시각화 옵션 선택
    # -------------------------------
    st.sidebar.header("시각화 옵션")
    chart_type = st.sidebar.selectbox("차트 유형 선택", ["막대 그래프", "선 그래프", "산점도"])
    x_axis = st.sidebar.selectbox("X축 변수 선택", df.columns)
    y_axis = st.sidebar.selectbox("Y축 변수 선택", df.columns)

    # -------------------------------
    # 4. 시각화 출력
    # -------------------------------
    if chart_type == "막대 그래프":
        fig = px.bar(df, x=x_axis, y=y_axis)
    elif chart_type == "선 그래프":
        fig = px.line(df, x=x_axis, y=y_axis)
    elif chart_type == "산점도":
        fig = px.scatter(df, x=x_axis, y=y_axis)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("CSV 파일을 업로드하면 시각화 옵션이 표시됩니다.")
