import streamlit as st
import pandas as pd
import plotly.express as px
import chardet
import io

st.set_page_config(page_title="대한민국 인구 변화 시각화", layout="wide")
st.title("👥 대한민국 지역별 연령별 인구 변화 시각화 대시보드")

# 파일 업로드
uploaded_files = st.file_uploader("2010년과 2025년 인구 CSV 파일을 업로드하세요", type=["csv"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 2:
    dfs = []

    for file in uploaded_files:
        raw = file.read()
        encoding = chardet.detect(raw)['encoding']
        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
        dfs.append(df)

    df_2010, df_2025 = dfs
    df_2010['연도'] = 2010
    df_2025['연도'] = 2025

    # 하나로 합치기
    df_all = pd.concat([df_2010, df_2025], ignore_index=True)

    # ✅ 탭 구성
    tab1, tab2, tab3 = st.tabs(["🗺 대한민국 지도", "📊 연령대별 인구 비교", "📈 인구 변화 상관관계"])

    # ---------------------------------
    # 🗺 대한민국 지도 (지역별 총인구)
    # ---------------------------------
    with tab1:
        st.subheader("🗺 지역별 총인구 지도 (2025 기준)")

        df_map = df_2025.groupby("지역")["인구수"].sum().reset_index()

        fig_map = px.choropleth(
            df_map,
            locations="지역",
            locationmode="geojson-id",
            geojson="https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json",
            featureidkey="properties.name",
            color="인구수",
            color_continuous_scale="YlOrRd",
            scope="asia"
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_map, use_container_width=True)

    # ---------------------------------
    # 📊 연령대별 인구 비교
    # ---------------------------------
    with tab2:
        selected_region = st.selectbox("비교할 지역 선택", df_all["지역"].unique())
        region_data = df_all[df_all["지역"] == selected_region]

        fig = px.bar(region_data, x="연령대", y="인구수", color="연도", barmode="group",
                     title=f"{selected_region} 연령대별 인구 비교")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------
    # 📈 상관관계 분석 (연령대별 인구: 2010 vs 2025)
    # ---------------------------------
    with tab3:
        st.subheader("📈 연령대별 인구 변화 상관관계 분석")

        # 연령대별 인구수를 피벗 형태로 정리
        pivot_2010 = df_2010.pivot_table(index="연령대", values="인구수", aggfunc="sum")
        pivot_2025 = df_2025.pivot_table(index="연령대", values="인구수", aggfunc="sum")
        pivot_df = pd.merge(pivot_2010, pivot_2025, on="연령대", suffixes=("_2010", "_2025")).reset_index()

        # 산점도 + 추세선
        fig = px.scatter(pivot_df, x="인구수_2010", y="인구수_2025", text="연령대",
                         trendline="ols", title="연령대별 인구수 상관관계 (2010 vs 2025)")
        st.plotly_chart(fig, use_container_width=True)

        # 상관계수 표시
        corr = pivot_df["인구수_2010"].corr(pivot_df["인구수_2025"])
        st.info(f"📌 Pearson 상관계수: **{corr:.3f}**")
else:
    st.info("CSV 파일 두 개(2010, 2025)를 업로드해주세요.")
