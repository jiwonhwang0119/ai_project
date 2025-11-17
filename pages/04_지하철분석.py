import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# 기본 설정
# --------------------------
st.set_page_config(
    page_title="지하철 승하차 분석",
    layout="wide"
)

st.title("🚇 2025년 지하철 승·하차 데이터 분석 대시보드")
st.write("날짜와 노선을 선택하면 승차+하차 승객 수 상위 10개 역을 그래프로 보여줘요!")

# --------------------------
# 데이터 불러오기
# --------------------------
@st.cache_data
def load_data():
    return pd.read_csv("subway.csv", encoding="cp949")

df = load_data()

# 날짜 datetime 형식으로 변환
df["사용일자"] = pd.to_datetime(df["사용일자"].astype(str))

# 2025년 10월 데이터만 필터
df_oct = df[df["사용일자"].dt.month == 10]

# --------------------------
# 사이드바 선택
# --------------------------
st.sidebar.header("🔎 옵션 선택")

date_list = sorted(df_oct["사용일자"].dt.date.unique())
selected_date = st.sidebar.selectbox("📅 날짜 선택", date_list)

line_list = sorted(df_oct["노선명"].unique())
selected_line = st.sidebar.selectbox("🚇 노선 선택", line_list)

# --------------------------
# 데이터 필터링
# --------------------------
filtered = df_oct[
    (df_oct["사용일자"].dt.date == selected_date) &
    (df_oct["노선명"] == selected_line)
].copy()

# 승하차 합계 컬럼 추가
filtered["총승하차"] = filtered["승차총승객수"] + filtered["하차총승객수"]

# TOP 10 계산
top10 = filtered.sort_values("총승하차", ascending=False).head(10)

# --------------------------
# 색상 스타일: 1등 빨강 + 나머지 파란색 → 점점 밝아지는 그라데이션
# --------------------------
colors = ["red"] + [
    f"rgba(30, 144, 255, {0.9 - i*0.08})" for i in range(1, 10)
]

# --------------------------
# Plotly 그래프 생성
# --------------------------
fig = px.bar(
    top10,
    x="역명",
    y="총승하차",
    title=f"📊 {selected_date} · {selected_line} 승하차 총합 TOP 10",
)

# 색상을 막대별로 개별 적용
fig.update_traces(marker_color=colors)

fig.update_layout(
    xaxis_title="역명",
    yaxis_title="승하차 총합",
    title_font_size=22,
    plot_bgcolor="white"
)

# --------------------------
# 출력
# --------------------------
st.plotly_chart(fig, use_container_width=True)

st.write("📌 **Tip:** 사이드바에서 날짜와 노선을 바꿔보세요!")
