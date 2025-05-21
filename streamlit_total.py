import streamlit as st
import pandas as pd
import plotly.express as px
import chardet
import io

st.set_page_config(page_title="한국 연령대별 인구 시간 변화", layout="wide")
st.title(":earth_asia: 대한민국 연령대별 인구 변화 시간 시각화")

# 지역명 간소화
REGION_MAP = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
    "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
    "울산광역시": "울산", "세종특별자치시": "세종",
    "경기도": "경기", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전라북도": "전라북", "전라남도": "전라남", "경상북도": "경북", "경상남도": "경남",
    "제주특별자치도": "제주"
}

# 파일 업로드
uploaded_files = st.file_uploader("2010년과 2025년 CSV 파일 2개를 업로드해주세요.", type=["csv"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 2:
    dfs = []
    for i, file in enumerate(uploaded_files):
        raw = file.read()
        encoding = chardet.detect(raw)['encoding']
        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
        df.columns = df.columns.str.strip()

        # 경우에 따라 '행정구역'이 없을 때 체크
        region_col = [col for col in df.columns if "행정구역" in col][0]
        population_col = [col for col in df.columns if "연령구간인구수" in col][0]

        df = df.rename(columns={region_col: "지역", population_col: "인구수"})
        df = df[["\uc9c0\uc5ed", "\uc778\uad6c\uc218"]]
        df["\uc5f0\ub144"] = 2010 if i == 0 else 2025
        df["\uc9c0\uc5ed"] = df["\uc9c0\uc5ed"].apply(lambda x: REGION_MAP.get(x.strip(), x.strip()))
        dfs.append(df)

    df_2010, df_2025 = dfs
    df_all = pd.concat([df_2010, df_2025], ignore_index=True)

    tab1, tab2 = st.tabs(["\ud55c\uad6d \uc9c0\ubc29 \uc778\uad6c\uc218 \uc9c0\ub3c4", "\uc5f0\ub839\uad6c\uac04 \ube44\uad50 "])

    with tab1:
        st.subheader("2025\ub144 \uc9c0\uc5ed\ubcc4 \ucd1d \uc778\uad6c\uc218 \uc9c0\ub3c4")
        df_map = df_2025.groupby("\uc9c0\uc5ed")["\uc778\uad6c\uc218"].sum().reset_index()

        geojson_url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json"
        fig_map = px.choropleth(
            df_map,
            geojson=geojson_url,
            locations="\uc9c0\uc5ed",
            featureidkey="properties.name",
            color="\uc778\uad6c\uc218",
            color_continuous_scale="YlOrRd",
            title="2025\ub144 \uc9c0\uc5ed\ubcc4 \uc778\uad6c\uc218"
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_map, use_container_width=True)

    with tab2:
        st.subheader("\uc9c0\uc5ed \ubcf4\uae30 \ubc0f \ub3d9\uae30\ubcc0\ud654 \ube44\uad50")
        selected_region = st.selectbox("\uc9c0\uc5ed \uc120\ud0dd", sorted(df_all["\uc9c0\uc5ed"].unique()))
        region_data = df_all[df_all["\uc9c0\uc5ed"] == selected_region]
        fig_line = px.line(region_data, x="\uc5f0\ub144", y="\uc778\uad6c\uc218", title=f"'{selected_region}' \uc5f0\ub144\ubcc4 \uc778\uad6c\uc218 \ubcc0\ud654")
        st.plotly_chart(fig_line, use_container_width=True)
else:
    st.warning("2010\ub144\uacfc 2025\ub144 \ud30c\uc77c 2\uac1c\ub97c \eb%b0\uade0 \uc5c5\ub85c\ub4dc\ud574\uc8fc\uc138\uc694.")
