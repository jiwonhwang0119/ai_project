import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="지진 대피소 시각화 (인코딩 처리 포함)", layout="wide")
st.title("📍 지진 대피소 시각화 (CSV 인코딩 자동 감지 시도)")

uploaded_file = st.file_uploader("CSV 파일 업로드 (.csv)", type=["csv"])

ENCODINGS = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"]

def try_read_csv(buffer):
    for enc in ENCODINGS:
        try:
            buffer.seek(0)
            df = pd.read_csv(buffer, encoding=enc)
            return df, enc
        except:
            continue
    return None, None

if uploaded_file:
    file_buffer = io.BytesIO(uploaded_file.getvalue())
    df, used_enc = try_read_csv(file_buffer)

    if df is None:
        st.error("CSV 인코딩을 자동으로 읽을 수 없습니다.")
    else:
        st.success(f"파일을 성공적으로 읽었습니다. 사용된 인코딩: **{used_enc}**")
        st.subheader("데이터 미리보기")
        st.dataframe(df.head())

        # 🔥 여기 수정됨: 시군구명을 자치구로 인식하도록 추가함
        possible_gu_cols = ["자치구", "구", "시군구명", "district", "gu"]

        gu_col = None
        for c in possible_gu_cols:
            if c in df.columns:
                gu_col = c
                break

        if gu_col is None:
            st.error("데이터에 자치구(구) 컬럼이 없습니다. (예: '자치구', '구', '시군구명')")
        else:
            # 집계
            grouped = df.groupby(gu_col).size().reset_index(name="count")
            grouped = grouped.sort_values("count", ascending=False).reset_index(drop=True)

            # 색상 설정
            import plotly.colors as pc
            seq = pc.sequential.OrRd

            counts = grouped["count"].values
            norm = (counts - counts.min()) / (counts.max() - counts.min() + 1e-9)

            def make_color(name, val_norm):
                if str(name) == "강북구":
                    return "red"
                if str(name) == "성북구":
                    return "blue"
                idx = int(val_norm * (len(seq) - 1))
                return seq[idx]

            grouped["color"] = [make_color(n, v) for n, v in zip(grouped[gu_col], norm)]

            fig = px.bar(
                grouped,
                x=gu_col,
                y="count",
                title="자치구별 지진 대피소 개수",
                text="count",
            )
            fig.update_traces(marker_color=grouped["color"], textposition="outside")

            st.plotly_chart(fig, use_container_width=True)
