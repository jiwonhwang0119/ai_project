import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="국가별 MBTI 분석", page_icon="🌍", layout="wide")

st.title("🌍 국가별 MBTI 비율 분석 대시보드")
st.write("각 국가별 MBTI 분포를 인터랙티브 그래프로 확인해보세요!")

# --------------------------
# 🔹 데이터 불러오기
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# --------------------------
# 🔹 MBTI 16개 컬럼 자동 탐색
# --------------------------
MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

# 실제 CSV에 존재하는 MBTI 열만 사용
mbti_cols = [c for c in MBTI_TYPES if c in df.columns]

if len(mbti_cols) == 0:
    st.error("❌ CSV 파일 안에서 MBTI 타입 컬럼(예: ENFP, INTJ 등)을 찾을 수 없습니다.")
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
# 🔹 선택 국가의 MBTI 값 추출
# --------------------------
row = df[df[country_col] == selected_country].iloc[0]

values = row[mbti_cols]

# MBTI 값 정렬 (내림차순)
sorted_values = values.sort_values(ascending=False)

# --------------------------
# 🔹 색상 설정
#    1등 = 빨강
#    2등~16등 = 파랑 → 옅은 파랑 그라데이션
# --------------------------

colors = []

# 1등 빨강
colors.append("red")

# 파랑 → 흐린 파랑 그라데이션 생성
def blue_gradient(n):
    base = np.linspace(255, 120, n).astype(int)
    return [f"rgb(0,0,{v})" for v in base]

blue_grad = blue_gradient(len(sorted_values) - 1)
colors.extend(blue_grad)

# --------------------------
# 🔹 Plotly 막대그래프
# --------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=sorted_values.index,
    y=sorted_values.values,
    marker=dict(color=colors),
    text=[f"{v}" for v in sorted_values.values],
    textposition="outside"
))

fig.update_layout(
    title=f"🇨🇦 {selected_country} MBTI 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="값",
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 🔹 데이터 테이블
# --------------------------
st.subheader(f"📊 {selected_country} MBTI 데이터")
st.dataframe(sorted_values.reset_index().rename(columns={"index": "MBTI", 0: "Value"}))
