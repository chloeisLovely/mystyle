import streamlit as st
import pandas as pd
import plotly.express as px
import chardet
import io

st.set_page_config(page_title="Data Explorer Dashboard", layout="wide")

# 타이틀
st.title("범용 CSV 데이터 시각화 대시보드")
st.markdown("업로드한 어떤 CSV 데이터든 3개의 탭으로 시각화해보세요!")

# 파일 업로드
uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드", type=["csv"])

if uploaded_file is not None:
    raw = uploaded_file.read()
    encoding = chardet.detect(raw)['encoding']
    df = pd.read_csv(io.BytesIO(raw), encoding=encoding)

    st.sidebar.success(f"✅ 감지된 인코딩: {encoding}")
    st.dataframe(df.head())

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🌍 지도 시각화", "🏆 상위 항목 그래프", "📈 상관관계 분석"])

    # 🌍 지도 시각화
    with tab1:
        st.subheader("지도 시각화")
        geo_columns = [col for col in df.columns if 'country' in col.lower() or 'location' in col.lower()]
        if geo_columns:
            geo_col = st.selectbox("지도에 표시할 위치 컬럼", geo_columns)
            value_col = st.selectbox("지도 색상값 컬럼", df.select_dtypes('number').columns)

            fig = px.choropleth(df, locations=geo_col, locationmode='country names',
                                color=value_col, color_continuous_scale='YlGnBu')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("❗ 국가명(Country 등)을 포함한 컬럼이 없어서 지도를 생성할 수 없습니다.")

    # 🏆 상위 항목 그래프
    with tab2:
        st.subheader("상위 값 그래프")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        if num_cols:
            target_col = st.selectbox("정렬 기준 숫자 컬럼 선택", num_cols)
            sort_col = st.selectbox("표시할 범주 컬럼 선택", df.columns)
            top_n = st.slider("상위 N개 항목 선택", 5, 20, 10)
            top_df = df.sort_values(by=target_col, ascending=False).head(top_n)
            fig_bar = px.bar(top_df, x=sort_col, y=target_col, color=target_col, color_continuous_scale='Blues')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("숫자 컬럼이 없어 그래프를 생성할 수 없습니다.")

    # 📈 상관관계 분석
    with tab3:
        st.subheader("상관관계 히트맵")
        corr_cols = st.multiselect("분석할 숫자 컬럼 선택", df.select_dtypes('number').columns.tolist())
        if len(corr_cols) >= 2:
            st.dataframe(df[corr_cols].corr())
            fig_corr = px.imshow(df[corr_cols].corr(), text_auto=True, color_continuous_scale='RdBu_r')
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("두 개 이상의 숫자 컬럼을 선택해주세요.")
else:
    st.info("CSV 파일을 업로드하면 대시보드가 활성화됩니다.")
