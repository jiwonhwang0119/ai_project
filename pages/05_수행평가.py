import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="지진 대피소 시각화", layout="wide")
st.title("📍 서울시 지진 대피소 시각화 대시보드")

# CSV 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    # --------------------------
    #  색상 규칙 적용
    # --------------------------
    def color_rule(region):
        if region == "강북구":
            return "red"
        elif region == "성북구":
            return "blue"
        else:
            return None   # 나머지는 plotly의 자동 colormap(그라데이션)

    df["color"] = df["자치구"].apply(color_rule)

    # --------------------------
    #  Plotly 그래프 (인터랙티브)
    # --------------------------
    st.subheader("📊 자치구별 대피소 수 시각화")

    # 자치구별 개수 집계
    grouped = df.groupby("자치구").size().reset_index(name="count")

    fig = px.bar(
        grouped,
        x="자치구",
        y="count",
        color="자치구",
        color_discrete_map={
            "강북구": "red",
            "성북구": "blue",
        },
        title="자치구별 지진 대피소 개수",
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("CSV 파일을 업로드하면 시각화를 시작할 수 있어요 🙂")
