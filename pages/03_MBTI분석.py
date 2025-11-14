import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="국가별 MBTI 분석", page_icon="🌍", layout="wide")

st.title("🌍 국가별 MBTI 비율 분석 대시보드")
st.write("CSV 파일을 기반으로 국가별 MBTI 분포를 인터랙티브 그래프로 살펴보세요!")

# --------------------------
# 🔹 데이터 불러오기
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# MBTI 컬럼 자동 탐색
candidate_mbti_cols = ["MBTI", "mbti", "type", "Type", "Personality", "personality"]
mbti_col = None
for c in candidate_mbti_cols:
    if c in df.columns:
        mbti_col = c
        break

if mbti_col is None:
    st.error("❌ MBTI 컬럼을 찾을 수 없습니다. CSV 파일의 MBTI 컬럼명을 확인해주세요.")
    st.stop()

# 국가 컬럼 자동 탐색
candidate_country_cols = ["Country", "country", "나라", "국가"]
country_col = None
for c in candidate_country_cols:
    if c in df.columns:
        country_col = c
        break

if country_col is None:
    st.error("❌ 국가 컬럼을 찾을 수 없습니다. CSV 파일의 국가 컬럼명을 확인해주세요.")
    st.stop()

# --------------------------
# 🔹 국가 선택 UI
# --------------------------
country_list = sorted(df[country_col].dropna().unique())
selected_country = st.selectbox("국가 선택", country_list)

# --------------------------
# 🔹 선택된 국가 데이터 처리
# --------------------------
filtered = df[df[country_col] == selected_country]

mbti_counts = filtered[mbti_col].value_counts().sort_values(ascending=False)
mbti_percent = (mbti_counts / mbti_counts.sum() * 100).round(2)

# --------------------------
# 🔹 색상 만들기 (등수 기반)
#   1등 = 빨강
#   2~16등 = 파랑 → 옅은 파랑 그라데이션
# --------------------------
colors = []

# 1등 색
colors.append("red")

# 파랑계열 그라데이션 (Hex 조절)
def blue_gradient(n):
    base = np.linspace(255, 100, n).astype(int)
    return [f"rgb(0,0,{v})" for v in base]

grads = blue_gradient(len(mbti_percent) - 1)
colors.extend(grads)

# --------------------------
# 🔹 Plotly 그래프 그리기
# --------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=mbti_percent.index,
    y=mbti_percent.values,
    marker=dict(color=colors),
    text=[f"{v}%" for v in mbti_percent.values],
    textposition="outside"
))

fig.update_layout(
    title=f"🇨🇦 {selected_country} MBTI 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 🔹 데이터 테이블도 제공
# --------------------------
st.subheader(f"📊 {selected_country} MBTI 데이터")
st.dataframe(mbti_percent.reset_index().rename(columns={"index": "MBTI", 0: "Percent"}))
