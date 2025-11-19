# Streamlit page: 지진 대피소 비율 시각화 (pages/earthquake_shelters.py)
# ---------------------------------------------------------------
# 이 파일은 Streamlit Cloud의 `pages` 폴더 아래에 위치하도록 만들어졌습니다.
# 아래의 주석 블록은 requirements.txt 내용과 간단한 사용법을 포함합니다.
# ----------------- requirements.txt (copy this into requirements.txt) -----------------
# streamlit
# pandas
# plotly
# numpy
# ----------------- end requirements.txt ---------------------------------------------

# 사용법:
# 1) 프로젝트 루트: CSV 파일은 루트에 'earthquake shelter.csv'로 둡니다. (업로드된 경우 '/mnt/data/earthquake shelter.csv' 경로도 자동으로 감지)
# 2) Streamlit Cloud에 배포하면 이 파일은 pages/ 아래에 있으므로 자동으로 사이드바에서 페이지로 표시됩니다.
# 3) 필요시 컬럼명이 다르면 앱의 자동 컬럼 감지 로직이 시도합니다.

import os
import math
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="지진 대피소 비율", layout="wide")

st.title("자치구별 지진 대피소 비율")
st.markdown("데이터 파일: `earthquake shelter.csv` (루트 폴더) — 업로드된 환경에서는 `/mnt/data/earthquake shelter.csv` 도 자동 감지됩니다.")

# CSV 경로 탐색: 우선 루트에 있는 파일명, 그렇지 않으면 업로드된 경로를 사용
candidate_paths = [
    "earthquake shelter.csv",
    "earthquake_shelter.csv",
    "./earthquake shelter.csv",
    "/mnt/data/earthquake shelter.csv",
    "/mnt/data/earthquake_shelter.csv"
]

csv_path = None
for p in candidate_paths:
    if os.path.exists(p):
        csv_path = p
        break

if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다. 루트 폴더에 'earthquake shelter.csv' 파일을 올려주세요.")
    st.stop()

# 데이터 읽기
try:
    df = pd.read_csv(csv_path)
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

st.sidebar.header("설정")
# 자동 컬럼 감지: 자치구 이름이 담긴 컬럼 후보
district_candidates = [
    '자치구', '구', 'SIG_KOR_NM', '도시', 'district', 'district_name', '지역', 'GU', 'gu'
]

found_district_col = None
for c in district_candidates:
    if c in df.columns:
        found_district_col = c
        break

# 만약 자동으로 못찾으면 사용자가 선택하게 함
if found_district_col is None:
    st.sidebar.warning("자치구(구) 컬럼을 자동으로 찾지 못했습니다. 아래에서 컬럼을 선택하세요.")
    found_district_col = st.sidebar.selectbox("자치구 컬럼 선택", options=df.columns)
else:
    st.sidebar.info(f"자치구 컬럼 자동 선택: `{found_district_col}`")

# 선택 가능한 상호작용: 상위 N개 보기, 정렬 방식
top_n = st.sidebar.number_input("상위 N개 표시 (0 = 전체)", min_value=0, max_value=1000, value=0, step=1)
show_percent = st.sidebar.checkbox("비율(%) 표시", value=True)

# 전처리: 결측값 제거 및 문자열 정리
df = df.copy()
# 문자열로 변환 및 strip
df[found_district_col] = df[found_district_col].astype(str).str.strip()
# 그룹 집계
group = df.groupby(found_district_col).size().reset_index(name='count')
# total shelters
total = group['count'].sum()
if total == 0:
    st.error("데이터에 대피소 수가 0입니다. 데이터 내용을 확인해주세요.")
    st.stop()

group['percent'] = group['count'] / total * 100
# 정렬(내림차순)
group = group.sort_values(by='count', ascending=False).reset_index(drop=True)
# 순위
group['rank'] = group.index + 1

# top_n 처리
if top_n > 0 and top_n < len(group):
    display_df = group.head(top_n).copy()
else:
    display_df = group.copy()

# 색상 지정: 1등은 빨간색, 나머지는 그라데이션
# 1등: 강한 빨강
first_color = '#e63946'  # red
# 나머지를 위한 블루-그라데이션 사용 (연속형) — 2등부터 끝까지
num_other = len(display_df) - 1
# gradient 색상 리스트 생성 (viridis나 blues 계열을 사용)
if num_other > 0:
    # px.colors.sequential 등에서 중간색들을 뽑아 사용
    palette = px.colors.sequential.Blues
    # palette 길이와 필요 길이가 다를 수 있으므로 보간
    def interpolate_palette(palette, n):
        # palette: list of hex
        # return n colors interpolated evenly from palette
        import colorsys
        # convert hex to rgb
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb
        base_rgbs = [hex_to_rgb(h) for h in palette]
        # linear interpolate across base_rgbs
        result = []
        for i in range(n):
            t = i / max(n-1, 1)
            # find position in base palette
            pos = t * (len(base_rgbs)-1)
            i0 = int(math.floor(pos))
            i1 = int(math.ceil(pos))
            local_t = pos - i0
            r = round((1-local_t)*base_rgbs[i0][0] + local_t*base_rgbs[i1][0])
            g = round((1-local_t)*base_rgbs[i0][1] + local_t*base_rgbs[i1][1])
            b = round((1-local_t)*base_rgbs[i0][2] + local_t*base_rgbs[i1][2])
            result.append(rgb_to_hex((r,g,b)))
        return result

    other_colors = interpolate_palette(palette, num_other)
    colors = [first_color] + other_colors
else:
    colors = [first_color]

# display_df에 대해 colors만들기 — 만약 top_n < 전체이고 1등이 잘려나갔으면 순위 기준으로 색 적용
# Map colors by rank position in display_df
colors_mapped = []
for idx, row in display_df.reset_index().iterrows():
    if row['rank'] == 1:
        colors_mapped.append(first_color)
    else:
        # pick color according to position among others
        # position among others: (rank-2) -> 0-based
        if num_other > 0:
            pos = min(max(int(idx-1), 0), max(num_other-1,0))
            colors_mapped.append(other_colors[pos])
        else:
            colors_mapped.append('#bbbbbb')

# 그래프 그리기
fig = go.Figure()
fig.add_trace(go.Bar(
    x=display_df[found_district_col],
    y=display_df['percent'] if show_percent else display_df['count'],
    marker_color=colors_mapped,
    text=[f"{c:.1f}%" if show_percent else str(int(c)) for c in display_df['percent'] if show_percent] if show_percent else None,
    hovertemplate=(
        f"<b>%{{x}}</b><br>"
        + ("대피소 수: %{customdata[0]}<br>비율: %{customdata[1]:.2f}%<extra></extra>" if show_percent else "대피소 수: %{customdata[0]}<extra></extra>")
    ),
    customdata=np.stack((display_df['count'], display_df['percent']), axis=-1),
))

y_title = '비율 (%)' if show_percent else '대피소 수'
fig.update_layout(
    title={'text': '자치구별 지진 대피소 비율', 'x':0.5},
    xaxis_title='자치구',
    yaxis_title=y_title,
    template='plotly_white',
    hovermode='closest',
    margin=dict(l=40, r=40, t=80, b=120)
)

# x축 라벨 각도를 자동으로 조정
fig.update_xaxes(tickangle=-45, tickfont=dict(size=11))

st.plotly_chart(fig, use_container_width=True)

# 표 형태로 결과 보기
with st.expander("상세 데이터 보기"):
    show_table = display_df.copy()
    show_table['percent'] = show_table['percent'].round(2)
    show_table = show_table.rename(columns={found_district_col: '자치구', 'count': '대피소 수', 'percent': '비율(%)', 'rank':'순위'})
    st.dataframe(show_table.reset_index(drop=True))

st.markdown("---")
st.caption(f"데이터 소스: `{csv_path}` — 총 대피소 수: {total}")

# 끝
