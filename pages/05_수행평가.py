import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="지진 대피소 시각화 (인코딩 처리 포함)", layout="wide")
st.title("📍 지진 대피소 시각화 (CSV 인코딩 자동 감지 시도)")

st.markdown(
    """
- 업로드한 CSV에서 인코딩 문제로 실패하면 자동으로 몇 가지 인코딩을 시도합니다.
- 그래프: 강북구 → 빨강, 성북구 → 파랑, 나머지는 개수 기반 그라데이션으로 표시됩니다.
"""
)

uploaded_file = st.file_uploader("CSV 파일 업로드 (.csv)", type=["csv"])

# 인코딩 시도 리스트
ENCODINGS = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"]

def try_read_csv(buffer):
    """여러 인코딩을 시도해 읽어본다. 성공하면 (df, encoding) 반환, 실패하면 (None, None)."""
    for enc in ENCODINGS:
        try:
            buffer.seek(0)
            df = pd.read_csv(buffer, encoding=enc)
            return df, enc
        except Exception as e:
            # 실패하면 다음 인코딩으로
            continue
    return None, None

def preview_bytes(buffer, n=2000):
    buffer.seek(0)
    raw = buffer.read(n)
    # 바이트 출력 (부분), 사용자에게 인코딩 확인 도움
    return raw

if uploaded_file:
    # uploaded_file은 UploadedFile 객체 → bytesIO로 변환
    file_buffer = io.BytesIO(uploaded_file.getvalue())

    st.info("파일을 읽어옵니다... (여러 인코딩을 자동으로 시도합니다)")
    df, used_enc = try_read_csv(file_buffer)

    if df is None:
        st.error("자동 인코딩 시도에서 모두 실패했습니다. 파일 앞부분(바이너리)을 보여드릴게요. 인코딩을 확인하거나 CSV를 UTF-8로 다시 저장해 주세요.")
        raw = preview_bytes(file_buffer, n=4000)
        st.code(raw[:1000], language="text")  # 처음 일부 출력
        st.write("가능한 해결 방법:")
        st.write("- CSV를 메모장/엑셀에서 '다른 이름으로 저장' → UTF-8로 저장")
        st.write("- 로컬에서 인코딩을 확인한 후 다시 업로드")
    else:
        st.success(f"파일을 성공적으로 읽었습니다. 사용된 인코딩: **{used_enc}**")
        st.subheader("데이터 미리보기")
        st.dataframe(df.head())

        # 컬럼명 한글/영문 상황 대비: '자치구' 컬럼이 없으면 대체 시도
        possible_gu_cols = ["자치구", "구", "행정구", "district", "gu"]
        gu_col = None
        for c in possible_gu_cols:
            if c in df.columns:
                gu_col = c
                break
        if gu_col is None:
            st.error("데이터에 '자치구' 정보를 찾을 수 없습니다. 컬럼명을 확인해주세요. (예: '자치구', '구', 'district')")
        else:
            # 집계
            grouped = df.groupby(gu_col).size().reset_index(name="count")
            grouped = grouped.sort_values("count", ascending=False).reset_index(drop=True)

            # 색상 생성: 강북구->red, 성북구->blue, 나머지 -> 그라데이션
            # 그라데이션은 count값을 0-1로 정규화하여 plotly sequential 색상에서 선택
            import plotly.colors as pc
            seq = pc.sequential.OrRd  # 연속 색상 팔레트 (원하면 바꿀 수 있음)
            # normalize counts to index into sequence
            counts = grouped["count"].values
            if len(counts) > 1:
                norm = (counts - counts.min()) / (counts.max() - counts.min() + 1e-9)
            else:
                norm = [0.5] * len(counts)

            def make_color(name, val_norm):
                if str(name) == "강북구":
                    return "red"
                if str(name) == "성북구":
                    return "blue"
                # pick from seq by normalized value
                # seq length might be small; scale index
                idx = int(val_norm * (len(seq) - 1))
                return seq[idx]

            grouped["color"] = [make_color(n, v) for n, v in zip(grouped[gu_col], norm)]

            # Plotly 막대그래프: 각 바에 색 적용
            fig = px.bar(
                grouped,
                x=gu_col,
                y="count",
                title="자치구별 지진 대피소 개수",
                text="count",
            )
            # 수동으로 색 지정
            fig.update_traces(marker_color=grouped["color"], textposition="outside")
            fig.update_layout(xaxis_tickangle=-45, yaxis_title="대피소 수", uniformtext_minsize=8, uniformtext_mode='hide')

            st.plotly_chart(fig, use_container_width=True)

            # 선택적으로 지도 표시(위도/경도 컬럼이 있으면)
            lat_cols = [c for c in df.columns if "위도" in c or "lat" in c.lower()]
            lon_cols = [c for c in df.columns if "경도" in c or "lon" in c.lower()]
            if lat_cols and lon_cols:
                lat_col = lat_cols[0]
                lon_col = lon_cols[0]
                st.subheader("지도 표시")
                # 간단한 scatter_mapbox 스타일 (Mapbox token 없이도 작동하는 기본 scatter_geo 대체)
                fig_map = px.scatter_geo(df, lat=lat_col, lon=lon_col, hover_name=gu_col, scope="asia")
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("위도/경도 컬럼이 없어 지도 표시를 건너뜁니다. (열 이름에 '위도','경도','lat','lon' 포함 여부 확인)")
