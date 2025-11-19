# ------------------------------
# ✔ PART 1 — 수정해야 하는 부분만 제공
# ------------------------------
# 아래 블록을 기존 코드의 "색상 지정" 부분에 그대로 교체하세요.

# 색상 지정: 1등은 빨간색, 나머지는 그라데이션
first_color = '#e63946'

num_other = len(display_df) - 1

if num_other > 0:
    # Blues colorscale에서 필요한 개수만큼 색 추출
    positions = [i / max(num_other - 1, 1) for i in range(num_other)]
    other_colors = px.colors.sample_colorscale('Blues', positions)
else:
    other_colors = []

# 순위 기반 색 매핑
colors_mapped = []
for _, row in display_df.iterrows():
    if row['rank'] == 1:
        colors_mapped.append(first_color)
    else:
        idx = max(min(row['rank'] - 2, len(other_colors) - 1), 0)
        colors_mapped.append(other_colors[idx])


# ------------------------------
# ✔ PART 2 — 전체 완성된 Streamlit 파일 제공
# ------------------------------
# 파일명: pages/earthquake_shelters.py
# ------------------------------

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="지진 대피소 비율", layout="wide")

st.title("자치구별 지진 대피소 비율")
st.markdown("데이터 파일: `earthquake shelter.csv` (루트 폴더) — 업로드된 환경에서는 `/mnt/data/earthquake shelter.csv` 도 자동 감지됩니다.")

# CSV 경로 자동 탐색
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
df = pd.read_csv(csv_path)

st.sidebar.header("설정")

# 자동 컬럼 감지
district_candidates = ['자치구', '구', 'SIG_KOR_NM', 'district', '지역', 'GU', 'gu']
found_district_col = None
for c in district_candidates:
    if c in df.columns:
        found_district_col = c
        break

if not found_district_col:
    found_district_col = st.sidebar.selectbox("자치구 컬럼 선택", df.columns)
else:
    st.sidebar.info(f"자치구 컬럼 자동 선택됨: {found_district_col}")

# 상호작용 옵션
top_n = st.sidebar.number_input("상위 N개 (0=전체)", min_value=0, max_value=999, value=0)
show_percent = st.sidebar.checkbox("비율(%) 표시", value=True)

# 전처리
df[found_district_col] = df[found_district_col].astype(str).str.strip()
group = df.groupby(found_district_col).size().reset_index(name='count')

total = group['count'].sum()
group['percent'] = group['count'] / total * 100
group = group.sort_values(by='count', ascending=False).reset_index()
group['rank'] = group.index + 1

# top_n 반영
if top_n > 0:
    display_df = group.head(top_n)
else:
    display_df = group.copy()

# ------------------------------
# 색상 로직 (오류 없는 버전)
# ------------------------------
first_color = '#e63946'
num_other = len(display_df) - 1

if num_other > 0:
    positions = [i / max(num_other - 1, 1) for i in range(num_other)]
    other_colors = px.colors.sample_colorscale('Blues', positions)
else:
    other_colors = []

colors_mapped = []
for _, row in display_df.iterrows():
    if row['rank'] == 1:
        colors_mapped.append(first_color)
    else:
        idx = max(min(row['rank'] - 2, len(other_colors) - 1), 0)
        colors_mapped.append(other_colors[idx])

# ------------------------------
# Plotly 그래프
# ------------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=display_df[found_district_col],
    y=display_df['percent'] if show_percent else display_df['count'],
    marker_color=colors_mapped,
    customdata=np.stack((display_df['count'], display_df['percent']), axis=-1),
    hovertemplate=(
        "<b>%{x}</b><br>" +
        ("대피소 수: %{customdata[0]}<br>비율: %{customdata[1]:.2f}%<extra></extra>"
        if show_percent else "대피소 수: %{customdata[0]}<extra></extra>")
    )
))

fig.update_layout(
    title={'text': '자치구별 지진 대피소 비율', 'x': 0.5},
    xaxis_title="자치구",
    yaxis_title='비율 (%)' if show_percent else '대피소 수',
    template='plotly_white',
    margin=dict(l=40, r=40, t=70, b=120)
)

fig.update_xaxes(tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# 상세 데이터
with st.expander("데이터 보기"):
    df_show = display_df.copy()
    df_show['percent'] = df_show['percent'].round(2)
    st.dataframe(df_show)

st.caption(f"총 대피소 수: {total}")
