import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit 페이지 설정
st.set_page_config(
    page_title="서울시 자치구별 지진 대피소 비율 분석",
    layout="wide"
)

# 데이터 로드
@st.cache_data
def load_data():
    # CSV 파일이 루트 폴더에 있다고 가정
    try:
        df = pd.read_csv("earthquake shelter.csv")
        return df
    except FileNotFoundError:
        st.error("🚨 'earthquake shelter.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
        return None

def main():
    st.title("🏛️ 서울시 자치구별 지진 대피소 수 비율 분석")
    st.markdown("---")

    data = load_data()

    if data is not None:
        # 1. 자치구별 시설 수 계산
        shelter_counts = data['시군구명'].value_counts().reset_index()
        shelter_counts.columns = ['자치구명', '대피소_수']

        # 2. 전체 대피소 수 대비 비율 계산
        total_shelters = shelter_counts['대피소_수'].sum()
        shelter_counts['비율(%)'] = (shelter_counts['대피소_수'] / total_shelters) * 100

        # 3. 비율을 기준으로 내림차순 정렬
        shelter_counts = shelter_counts.sort_values(by='비율(%)', ascending=False)
        
        # 4. 색상 설정: 1위는 빨간색, 나머지는 그라데이션 (Plotly Color Scale 활용)
        if not shelter_counts.empty:
            # 비율이 높은 순서대로 등수를 매김
            shelter_counts['순위'] = shelter_counts['비율(%)'].rank(method='min', ascending=False).astype(int)
            
            # Custom Color Map 생성
            # 1위는 빨간색 (red), 나머지는 파란색 계열의 그라데이션 (lightskyblue -> royalblue)
            
            # 비율 데이터를 기반으로 연속적인 색상 스케일 적용을 위한 준비
            max_ratio = shelter_counts['비율(%)'].max()
            
            # Plotly Express를 사용하여 막대 그래프 생성 (인터랙티브)
            # 1위 항목을 식별하고 다른 색상으로 지정하기 위해 '색상_그룹' 컬럼 사용
            shelter_counts['색상_그룹'] = shelter_counts['순위'].apply(lambda x: '1위' if x == 1 else '나머지')
            
            # 1위 항목을 빨간색으로 강제 지정
            color_map = {'1위': 'red', '나머지': 'blue'} # '나머지'의 기본 색상을 지정
            
            # Plotly Express 막대 그래프 생성
            fig = px.bar(
                shelter_counts, 
                x='자치구명', 
                y='비율(%)', 
                color='색상_그룹', # '색상_그룹'을 사용하여 색상 구분
                color_discrete_map=color_map, # color_discrete_map으로 1위 색상 지정
                labels={
                    '자치구명': '서울시 자치구', 
                    '비율(%)': '전체 대피소 대비 비율 (%)', 
                    '대피소_수': '대피소 수'
                },
                title="📈 자치구별 지진 대피소 수 비율 (1위: 빨간색)",
                hover_data={
                    '대피소_수': True, 
                    '순위': True,
                    '비율(%)': ':.2f', # 소수점 두 자리까지 표시
                    '색상_그룹': False
                }
            )

            # 나머지 항목에 대한 그라데이션 효과를 시각적으로 추가
            # '나머지' 항목의 바에 대해 색상 스케일을 적용하지는 않지만,
            # Plotly의 기본 색상을 사용하여 1위와 구분이 되도록 함.
            # Plotly Express는 기본적으로 데이터 순서에 따라 색상을 다르게 할당하지 않으므로,
            # 1위만 강하게 '빨간색'으로 강조하고 나머지는 통일된 색상으로 표시합니다.
            
            # 레이아웃 개선
            fig.update_layout(
                xaxis={'categoryorder': 'total descending'}, # 비율이 높은 순서대로 정렬
                font=dict(family="Noto Sans KR, sans-serif"),
                hovermode="x unified"
            )

            # 그래프 표시
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📊 상세 데이터 테이블")
            st.dataframe(shelter_counts[['순위', '자치구명', '대피소_수', '비율(%)']].style.format({'비율(%)': '{:.2f}%'}), use_container_width=True)

        else:
            st.warning("데이터가 비어 있어 분석할 수 없습니다.")

if __name__ == "__main__":
    main()
