import streamlit as st
import pandas as pd
import plotly.express as px
import chardet
import io

st.set_page_config(page_title="대한민국 인구 변화 시각화", layout="wide")
st.title("👥 대한민국 지역별 연령대별 인구 변화 시각화 대시보드")

# ✅ 지역명 매핑 함수 (GeoJSON과 일치하도록 변환)
def simplify_region_name(region):
    replacements = {
        "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
        "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
        "울산광역시": "울산", "세종특별자치시": "세종",
        "경기도": "경기", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
        "전라북도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남",
        "제주특별자치도": "제주"
    }
    return replacements.get(region, region)

# ✅ 파일 업로드
uploaded_files = st.file_uploader("2010년과 2025년 인구 CSV 파일을 업로드하세요", type=["csv"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 2:
    dfs = []

    for file in uploaded_files:
        raw = file.read()
        encoding = chardet.detect(raw)['encoding']
        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
        df.columns = df.columns.str.strip()  # 컬럼명 공백 제거
        dfs.append(df)

    df_2010, df_2025 = dfs
    df_2010['연도'] = 2010
    df_2025['연도'] = 2025

    # 지역명 정리
    df_2010["지역"] = df_2010["지역"].apply(simplify_region_name)
    df_2025["지역"] = df_2025["지역"].apply(simplify_region_name)

    # 전체 병합
    df_all = pd.concat([df_2010, df_2025], ignore_index=True)

    # ✅ 탭 구성
    tab1, tab2, tab3 = st.tabs(["🗺 대한민국 지도", "📊 연령대별 인구 비교", "📈 인구 변화 상관관계"])

    # -------------------------------
    # 🗺 대한민국 지도 (지역별 총인구)
    # -------------------------------
    with tab1:
        st.subheader("🗺 지역별 총인구 지도 (2025 기준)")

        # 지도용 GeoJSON
        geojson_url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json"

        df_map = df_2025.groupby("지역")["인구수"].sum().reset_index()

        fig_map = px.choropleth(
            df_map,
            geojson=geojson_url,
            locations="지역",
            featureidkey="properties.name",
            color="인구수",
            color_continuous_scale="YlOrRd",
            scope="asia",
            title="2025년 지역별 총 인구수"
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_map, use_container_width=True)

    # -------------------------------
    # 📊 연령대별 인구 비교
    # -------------------------------
    with tab2:
        st.subheader("📊 연령대별 인구 비교 (2010 vs 2025)")
        selected_region = st.selectbox("비교할 지역 선택", df_all["지역"].unique())

        region_df = df_all[df_all["지역"] == selected_region]
        fig = px.bar(region_df, x="연령대", y="인구수", color="연도", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # 📈 상관관계 분석 (연령대별 인구 변화)
    # -------------------------------
    with tab3:
        st.subheader("📈 연령대별 인구 변화 상관관계 (2010 vs 2025)")

        # 연령대 기준 pivot
        pivot_2010 = df_2010.groupby("연령대")["인구수"].sum().reset_index()
        pivot_2025 = df_2025.groupby("연령대")["인구수"].sum().reset_index()

        pivot_df = pd.merge(pivot_2010, pivot_2025, on="연령대", suffixes=("_2010", "_2025"))

        fig = px.scatter(
            pivot_df,
            x="인구수_2010",
            y="인구수_2025",
            text="연령대",
            trendline="ols",
            title="연령대별 인구수 상관관계 (2010 vs 2025)"
        )
        st.plotly_chart(fig, use_container_width=True)

        corr = pivot_df["인구수_2010"].corr(pivot_df["인구수_2025"])
        st.info(f"📌 Pearson 상관계수: **{corr:.3f}**")

else:
    st.warning("❗ 2010년과 2025년 데이터를 각각 업로드해야 시각화가 가능합니다.")

