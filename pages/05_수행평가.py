# 파일 1 — pages/mbti_analysis.py

```python
# pages/mbti_analysis.py
# Streamlit page that inspects the provided CSV (located at project root)
# and draws a Plotly bar chart of MBTI-like distributions by country (or a chosen categorical column).

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MBTI / 카테고리 분포 분석", layout="wide")

st.title("MBTI 비율 분석 — (혹은 대체 카테고리)")
st.write("이 페이지는 루트 폴더의 CSV 파일을 읽어 국가(혹은 시도/국가 수준)별로 MBTI 분포(또는 사용자가 고른 범주)의 비율을 막대그래프로 보여줍니다.")

# 기본 파일 경로: pages 폴더 아래에서 실행되므로 ../ 로 루트로 올라갑니다.
default_path = Path(__file__).parent.parent / "earthquake shelter.csv"

uploaded = st.file_uploader("원본 CSV 파일 업로드 (선택) — 업로드하면 기본 파일 대신 사용됩니다", type=['csv'])
use_default = False = False
if uploaded is None:
    if default_path.exists():
        try:
            df = pd.read_csv(default_path, encoding='cp949')
            use_default = True
        except Exception:
            df = pd.read_csv(default_path, encoding='utf-8', errors='replace')
    else:
        st.error("기본 CSV 파일을 찾을 수 없습니다. 왼쪽의 업로더로 CSV 파일을 업로드해주세요.")
        st.stop()
else:
    df = pd.read_csv(uploaded)

st.subheader("데이터 샘플")
st.dataframe(df.head(10))

# Detect candidate country-like and categorical columns
cand_country = []
for c in df.columns:
    cl = c.lower()
    if any(k in cl for k in ['country','nation','국가','시도','도','시도명','country_name']):
        cand_country.append(c)

# fallback: columns with small number of unique values and object dtype
if not cand_country:
    for c in df.columns:
        if df[c].dtype == object and df[c].nunique() < 500:
            cand_country.append(c)

st.sidebar.header("설정")
country_col = st.sidebar.selectbox("국가/지역(또는 집계 단위) 컬럼 선택", options=cand_country if cand_country else list(df.columns), index=0 if cand_country else 0)

# Detect MBTI-like column
mbti_candidates = [c for c in df.columns if c.lower() in ('mbti','mbti_type','mbti type','personality','type')]
# heuristic: find columns with many 4-letter MBTI codes
if not mbti_candidates:
    for c in df.select_dtypes(include=['object']).columns:
        sample = df[c].dropna().astype(str).head(500)
        if len(sample) > 0:
            score = sample.str.match(r'^[EI][NS][TF][JP]$').mean()
            if score > 0.15:
                mbti_candidates.append(c)

st.sidebar.subheader("MBTI(혹은 분류) 컬럼 설정")
if mbti_candidates:
    mbti_col = st.sidebar.selectbox("MBTI(또는 항목) 컬럼 선택", options=mbti_candidates, index=0)
else:
    st.sidebar.write("MBTI 유사 컬럼을 자동으로 찾지 못했습니다.")
    mbti_col = st.sidebar.selectbox("대체로 사용할 범주형 컬럼을 직접 선택하세요", options=[c for c in df.columns if df[c].nunique() < 200])

st.sidebar.write("")

# group and compute percentages
if mbti_col not in df.columns or country_col not in df.columns:
    st.error("선택한 컬럼을 데이터에서 찾을 수 없습니다. 설정을 확인하세요.")
    st.stop()

agg = pd.crosstab(df[country_col], df[mbti_col])
agg_pct = (agg.div(agg.sum(axis=1), axis=0) * 100).round(2)

# country selector
country_list = agg_pct.index.tolist()
sel_country = st.selectbox("국가/지역 선택", options=country_list)

# prepare data for plotting
plot_df = agg_pct.loc[sel_country].reset_index()
plot_df.columns = [mbti_col, 'percent']
plot_df = plot_df.sort_values('percent', ascending=False).reset_index(drop=True)

# build colors: top = red, others = gradient
n = len(plot_df)
# get a sequential colorscale for others
colorscale = px.colors.sequential.Plasma
# generate gradient (avoid specifying exact color map name if you want to tweak)
# map others to a gradient, but ensure top is red
other_colors = []
if n > 1:
    # sample colors from the colorscale
    steps = max(n-1, 1)
    palette = px.colors.sample_colorscale(colorscale, [i/(steps-1) if steps>1 else 0.5 for i in range(steps)])
    other_colors = palette
else:
    other_colors = []

colors = []
for i in range(n):
    if i == 0:
        colors.append('red')
    else:
        colors.append(other_colors[i-1])

# Plotly bar
fig = go.Figure(go.Bar(
    x=plot_df['percent'],
    y=plot_df[mbti_col].astype(str),
    orientation='h',
    marker=dict(color=colors),
    hovertemplate='%{y}: %{x}%<extra></extra>'
))
fig.update_layout(title=f"{sel_country} — {mbti_col} 비율 (상위: 빨간색)", xaxis_title='Percent (%)', yaxis={'categoryorder':'total ascending'}, height=600)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("데이터 요약(자동 생성)")
col1, col2 = st.columns(2)
with col1:
    st.write(f"행 개수: {df.shape[0]}")
    st.write(f"열 개수: {df.shape[1]}")
    st.write("결측값 요약:")
    st.dataframe(df.isna().sum().to_frame('missing_count'))
with col2:
    st.write("각 컬럼의 고유값 개수 (상위 20) :")
    st.dataframe(pd.Series({c: df[c].nunique(dropna=False) for c in df.columns}).sort_values(ascending=False).head(20).to_frame('n_unique'))

st.caption("참고: 업로드된 데이터에 실제 MBTI 컬럼이 없으면, 사용자가 선택한 범주형 컬럼을 MBTI처럼 사용해 시각화합니다.")
```

---

# 파일 2 — requirements.txt

```
streamlit>=1.22
pandas>=1.5
plotly>=5.0
```

---

# 사용 방법 (간단 안내)

1. 프로젝트 루트에 `earthquake shelter.csv` 파일을 둡니다. (사용자가 이미 업로드한 경우 문제없음)
2. `pages/mbti_analysis.py` 파일을 그대로 `pages` 폴더에 넣습니다.
3. `requirements.txt` 를 루트에 넣고 Streamlit Cloud에 배포하세요.

**참고**: 업로드된 CSV에 실제 MBTI 컬럼이 없을 경우(예: 현재 제공된 파일은 재난대피소 관련 데이터로 보입니다), 페이지는 자동으로 범주형 컬럼을 선택해 시각화할 수 있도록 설계되어 있습니다. 원하시면 MBTI가 포함된 CSV를 새로 업로드하거나, 어떤 컬럼을 MBTI 대체로 사용하고 싶은지 알려주시면 그에 맞춰 코드 수정해드릴게요.
