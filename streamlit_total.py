import streamlit as st
import pandas as pd
import plotly.express as px
import chardet
import io

st.set_page_config(page_title="대한민국 인구 변화 시각화", layout="wide")
st.title("📊 대한민국 지역별 인구 변화 시각화 대시보드")

def extract_sido(region):
    return region.split()[0] if pd.notnull(region) else region

uploaded_files = st.file_uploader("📂 2010년과 2025년 CSV 파일을 업로드하세요", type=["csv"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 2:
    dfs = []
    for i, file in enumerate(uploaded_files):
        raw = file.read()
        encoding = chardet.detect(raw)['encoding']
        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
        df.columns = df.columns.str.strip()

        region_col = [col for col in df.columns if "행정구역" in col][0]
        age_group_col = [col for col in df.columns if "연령구간인구수" in col][0]

        df = df[[region_col, age_group_col]].copy()
        df.columns = ["행정구역", "연령구간인구수"]
        df["연도"] = 2010 if i == 0 else 2025
        df["시도"] = df["행정구역"].apply(extract_sido)

        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True)

    tab1, tab2, tab3 = st.tabs(["🗺 대한민국 지도", "📊 지역별 연도별 추이", "📈 상관관계 분석"])

    with tab1:
        st.subheader("🗺 2025년 시도별 총 인구수 지도")
        df_map = df_all[df_all["연도"] == 2025].groupby("시도")["연령구간인구수"].sum().reset_index()

        geojson_url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json"

        fig_map = px.choropleth(
            df_map,
            geojson=geojson_url,
            locations="시도",
            featureidkey="properties.name",
            color="연령구간인구수",
            color_continuous_scale="YlOrRd",
            title="2025년 시도별 총 인구수"
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_map, use_container_width=True)

    with tab2:
        st.subheader("📊 지역별 인구 변화 추이")
        selected_region = st.selectbox("시도 선택", sorted(df_all["시도"].unique()))
        region_df = df_all[df_all["시도"] == selected_region]
        fig_line = px.line(region_df, x="연도", y="연령구간인구수", color="행정구역",
                           title=f"{selected_region} 행정구역별 인구 변화")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("📈 연령구간인구수 상관관계 (2010 vs 2025)")

        df_2010 = df_all[df_all["연도"] == 2010].groupby("시도")["연령구간인구수"].sum().reset_index()
        df_2025 = df_all[df_all["연도"] == 2025].groupby("시도")["연령구간인구수"].sum().reset_index()
        df_corr = pd.merge(df_2010, df_2025, on="시도", suffixes=("_2010", "_2025"))

        fig_scatter = px.scatter(df_corr,
                                 x="연령구간인구수_2010",
                                 y="연령구간인구수_2025",
                                 text="시도",
                                 title="시도별 연령구간인구수 상관관계")
        st.plotly_chart(fig_scatter, use_container_width=True)

        corr = df_corr["연령구간인구수_2010"].corr(df_corr["연령구간인구수_2025"])
        st.info(f"📌 Pearson 상관계수: **{corr:.3f}**")

else:
    st.warning("⚠️ 반드시 2010년과 2025년 CSV 파일 2개를 업로드해주세요.")

