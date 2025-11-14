import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="국가별 MBTI 분석", page_icon="🌍", layout="wide")

st.title("🌍 국가별 MBTI 데이터 분석 대시보드")
st.write("Plotly 기반 인터랙티브 시각화 + 국가 / MBTI 기준 분석 제공")

# --------------------------
# 🔹 데이터 불러오기
# --------------------------
@st.cache_data
def load_data():
    return pd.read_csv("countriesMBTI_16types.csv")

df = load_data()

# --------------------------
# 🔹 MBTI 컬럼 자동 탐색
# --------------------------
MBTI_LIST = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

mbti_cols = [c for c in MBTI_LIST if c in df.columns]

# --------------------------
# 🔹 국가 컬럼 자동 탐색
# --------------------------
candidate_country_cols = ["Country", "country", "COUNTRY", "국가", "나라"]
country_col = next((c for c in candidate_country_cols if c in df.columns), None)

if country_col is None:
    st.error("❌ CSV에서 국가 컬럼을 찾을 수 없습니다.")
    st.stop()

# =========================================================
#                      📌 탭 구성
# =========================================================
tab1, tab2 = st.tabs(["국가별 MBTI", "MBTI별 국가 순위"])

# =========================================================
# 🔹 TAB 1 : 국가 선택 → MBTI 분포 그래프
# =========================================================
with tab1:
    st.subheader("🌎 국가를 선택하면 MBTI 비율을 확인할 수 있어요.")

    country = st.selectbox("국가 선택", sorted(df[country_col].unique()))

    selected_row = df[df[country_col] == country].iloc[0]
    values = selected_row[mbti_cols].sort_values(ascending=False)

    # Plotly 바차트
    fig = px.bar(
        values,
        x=values.index,
        y=values.values,
        text=values.values,
        color=values.values,
        color_continuous_scale="Blues",
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=f"📊 {country}의 MBTI 분포",
        xaxis_title="MBTI 유형",
        yaxis_title="값",
        template="plotly_white",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(values.reset_index().rename(columns={"index": "MBTI", 0: "Value"}))

# =========================================================
# 🔹 TAB 2 : MBTI 선택 → 상위 10개 국가 그래프
# =========================================================
with tab2:
    st.subheader("📌 MBTI 유형을 선택하면 상위 10개 국가를 보여줍니다")
    selected_mbti = st.selectbox("MBTI 선택", mbti_cols)

    # MBTI 기준 상위 10개 국가
    ranking = df[[country_col, selected_mbti]].sort_values(selected_mbti, ascending=False).head(10)

    # 색상 지정 (한국은 보라색)
    colors = []
    for c in ranking[country_col]:
        if c in ["South Korea", "Korea", "Republic of Korea", "대한민국"]:
            colors.append("purple")
        else:
            colors.append("rgba(0, 80, 255, 0.7)")

    # Plotly 그래프
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=ranking[country_col],
        y=ranking[selected_mbti],
        marker=dict(color=colors),
        text=ranking[selected_mbti],
        textposition="outside"
    ))

    fig2.update_layout(
        title=f"🏆 {selected_mbti} 비율이 높은 국가 Top 10",
        xaxis_title="국가",
        yaxis_title="값",
        template="plotly_white",
        height=600
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(ranking.reset_index(drop=True))
