import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI Country Dashboard", layout="wide")

st.title("🌏 국가별 MBTI 대시보드")
st.write("CSV 데이터를 기반으로 국가별 MBTI 비율을 시각화합니다.")

uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    # MBTI 컬럼 자동 탐색
    mbti_cols = [c for c in df.columns if c.upper() in [
        "INTJ","INTP","ENTJ","ENTP",
        "INFJ","INFP","ENFJ","ENFP",
        "ISTJ","ISFJ","ESTJ","ESFJ",
        "ISTP","ISFP","ESTP","ESFP"
    ]]

    if not mbti_cols:
        st.error("❌ MBTI 컬럼을 찾을 수 없습니다. CSV 파일의 컬럼명을 확인해주세요.")
        st.stop()

    tab1, tab2 = st.tabs(["📌 국가별 MBTI 비율", "📌 MBTI 유형별 상위 10개 국가"])

    # ----------------------------------------------------------
    # 📌 TAB 1 — 국가 선택 → 해당 국가 MBTI 비율 시각화
    # ----------------------------------------------------------
    with tab1:
        st.subheader("국가별 MBTI 비율")

        selected_country = st.selectbox("국가 선택", df["Country"].unique())

        row = df[df["Country"] == selected_country].iloc[0]
        mbti_data = row[mbti_cols].astype(float)

        # 정렬
        mbti_sorted = mbti_data.sort_values(ascending=False)
        order = mbti_sorted.index.tolist()

        # 색상 지정 (1등 빨강, 이후 파랑 → 연한 파랑 그라데이션)
        colors = ["red"] + px.colors.sequential.Blues[len(mbti_cols)-1:]

        fig = px.bar(
            x=mbti_sorted.values,
            y=mbti_sorted.index,
            orientation="h",
            color=range(len(mbti_sorted)),
            color_continuous_scale=["red"] + px.colors.sequential.Blues,
        )

        fig.update_layout(
            xaxis_title="비율",
            yaxis_title="MBTI 유형",
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------
    # 📌 TAB 2 — MBTI 유형 선택 → 비율 높은 국가 Top 10
    # ----------------------------------------------------------
    with tab2:
        st.subheader("MBTI 유형별 상위 10개 국가")

        selected_mbti = st.selectbox("MBTI 유형 선택", mbti_cols)

        top10 = df[["Country", selected_mbti]].copy()
        top10 = top10.sort_values(selected_mbti, ascending=False).head(10)

        # 색상: 대한민국 = 보라색, 나머지 파랑
        bar_colors = []
        for country in top10["Country"]:
            if isinstance(country, str) and "korea" in country.lower():
                bar_colors.append("purple")   # 대한민국만 보라색
            else:
                bar_colors.append("steelblue")

        fig2 = px.bar(
            top10,
            x="Country",
            y=selected_mbti,
            color=bar_colors,
            color_discrete_sequence=bar_colors
        )

        fig2.update_layout(
            xaxis_title="국가",
            yaxis_title=f"{selected_mbti} 비율",
            showlegend=False
        )

        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("CSV 파일을 업로드해주세요!")
