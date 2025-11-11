import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="서울 인기 관광지 Top 10 (외국인 선호)", layout="wide")

st.markdown("# 🌸 서울 인기 관광지 Top 10 — 외국인들이 사랑하는 명소")
st.markdown("※ 제작: 챗 (GPT). 더 많은 정보는 [https://gptonline.ai/ko/](https://gptonline.ai/ko/) 에서 확인하세요.")

# 장소 목록(이름, 위도, 경도, 설명, 지하철역, 맛집)
PLACES = [
    ("Gyeongbokgung Palace (경복궁)", 37.580467, 126.976944, "조선시대의 대표 궁궐, 한복 체험 명소", "경복궁역 (3호선)", "토속촌 삼계탕"),
    ("Changdeokgung Palace (창덕궁)", 37.579254, 126.992150, "유네스코 세계문화유산, 후원이 아름다운 궁궐", "안국역 (3호선)", "우정국"),
    ("Bukchon Hanok Village (북촌 한옥마을)", 37.582604, 126.983038, "전통 한옥이 모여 있는 아름다운 마을", "안국역 (3호선)", "카페 온"),
    ("Insadong (인사동)", 37.5729617, 126.9873316, "전통공예와 기념품 쇼핑 거리", "종각역 (1호선)", "쌈지길 맛집 진진바라"),
    ("Myeongdong (명동)", 37.560984, 126.985302, "서울 대표 쇼핑거리와 스트리트 푸드", "명동역 (4호선)", "명동교자"),
    ("Hongdae (홍대)", 37.55528, 126.92333, "젊음의 거리, 음악·패션·예술의 중심", "홍대입구역 (2호선, 공항철도)", "홍대 돈부리"),
    ("N Seoul Tower (남산타워)", 37.551170, 126.988228, "서울의 야경 명소이자 사랑의 자물쇠 명소", "명동역 (4호선)", "남산돈까스거리"),
    ("Dongdaemun Design Plaza (DDP)", 37.5669, 127.0094, "현대적 디자인과 야시장 문화가 공존", "동대문역사문화공원역 (2,4,5호선)", "진옥화할매닭한마리"),
    ("Namdaemun Market (남대문시장)", 37.555664, 126.976862, "서울 최대의 전통시장, 길거리 음식 천국", "회현역 (4호선)", "칼국수골목집"),
    ("Itaewon (이태원)", 37.534, 126.994, "다문화 거리와 외국인 친화적인 분위기", "이태원역 (6호선)", "보일링크랩")
]

# Sidebar controls
st.sidebar.header("설정")
show_markers = st.sidebar.checkbox("관광지 마커 표시", value=True)
map_type = st.sidebar.selectbox("지도 스타일 선택", ["cartodbpositron", "Stamen Toner", "OpenStreetMap"])
start_place = st.sidebar.selectbox("지도 중심을 선택하세요", ["서울 전체 보기", PLACES[0][0], PLACES[6][0]])
zoom = st.sidebar.slider("초기 줌 레벨", min_value=10, max_value=16, value=12)

# 지도 중심 설정
if start_place == "서울 전체 보기":
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=zoom, tiles=map_type)
else:
    coords = next((p[1], p[2]) for p in PLACES if p[0] == start_place)
    m = folium.Map(location=[coords[0], coords[1]], zoom_start=zoom, tiles=map_type)

# 마커 표시
if show_markers:
    for name, lat, lon, desc, station, restaurant in PLACES:
        popup_html = f"""
        <b>{name}</b><br/>
        🏛️ {desc}<br/>
        🚇 <b>가까운 지하철역:</b> {station}<br/>
        🍽️ <b>맛집 추천:</b> {restaurant}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip=name,
            icon=folium.Icon(color="purple", icon="info-sign")
        ).add_to(m)

# 경계 맞추기
if show_markers:
    lats = [p[1] for p in PLACES]
    lons = [p[2] for p in PLACES]
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

# 지도 표시 (80% 크기)
st_data = st_folium(m, width=880, height=560)

# 관광지 간단 소개
st.markdown("## ✨ 서울 주요 관광지 한눈에 보기")
for name, _, _, desc, station, restaurant in PLACES:
    st.markdown(f"**{name}** — {desc} (🚇 {station}, 🍽️ {restaurant})")

st.markdown("---")
st.markdown("출처: VisitSeoul, TripAdvisor, Wikipedia 등 (일부 내용은 참고용입니다).")
st.markdown("※ 더 많은 한국어 AI 도구는 [https://gptonline.ai/ko/](https://gptonline.ai/ko/) 에서 확인하세요.")
