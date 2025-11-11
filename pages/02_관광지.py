import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="서울 인기 관광지 Top 10 (외국인 선호)", layout="wide")

st.markdown("# 서울 인기 관광지 Top 10 — 외국인들이 좋아하는 곳")
st.markdown("※ 제작: 챗 (GPT). 더 많은 정보는 https://gptonline.ai/ko/ 를 확인하세요.")

# 장소 목록(이름, 위도, 경도, 간단 설명)
PLACES = [
    ("Gyeongbokgung Palace (경복궁)", 37.580467, 126.976944, "조선 시대의 대표 궁궐 — 한복 체험 추천"),
    ("Changdeokgung Palace (창덕궁)", 37.579254, 126.992150, "유네스코 세계문화유산, 후원이 유명"),
    ("Bukchon Hanok Village (북촌 한옥마을)", 37.582604, 126.983038, "전통 한옥 거리 — 사진 촬영 명소"),
    ("Insadong (인사동)", 37.5729617, 126.9873316, "전통공예품 거리, 기념품 쇼핑에 최적"),
    ("Myeongdong (명동)", 37.560984, 126.985302, "쇼핑 & 스트리트 푸드 중심가"),
    ("Hongdae (홍대)", 37.55528, 126.92333, "젊음의 문화, 거리공연과 카페가 많음"),
    ("N Seoul Tower (N서울타워 / 남산타워)", 37.551170, 126.988228, "서울 전망 명소 — 야경 추천"),
    ("Dongdaemun Design Plaza (DDP, 동대문 디자인 플라자)", 37.5669, 127.0094, "현대적 건축 & 야시장"),
    ("Namdaemun Market (남대문시장)", 37.555664, 126.976862, "전통시장 — 야시장, 길거리 음식 풍부"),
    ("Itaewon (이태원)", 37.534, 126.994, "다문화 음식·밤문화로 유명한 외국인 친화 지역")
]

# Sidebar controls
st.sidebar.header("설정")
show_markers = st.sidebar.checkbox("관광지 마커 표시", value=True)
start_place = st.sidebar.selectbox("지도 중심을 선택하세요", ["서울 전체 보기", PLACES[0][0], PLACES[6][0]])
zoom = st.sidebar.slider("초기 줌 레벨", min_value=10, max_value=16, value=12)

# Create base map
if start_place == "서울 전체 보기":
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=zoom)
else:
    # find selected place coords
    coords = next((p[1], p[2]) for p in PLACES if p[0] == start_place)
    m = folium.Map(location=[coords[0], coords[1]], zoom_start=zoom)

# Add markers
if show_markers:
    for name, lat, lon, desc in PLACES:
        popup_html = f"<b>{name}</b><br/>{desc}"
        folium.Marker(location=[lat, lon], popup=popup_html, tooltip=name).add_to(m)

# Fit map to markers bounds (if markers shown)
if show_markers:
    lats = [p[1] for p in PLACES]
    lons = [p[2] for p in PLACES]
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

# Display the map using streamlit_folium
st_data = st_folium(m, width=1100, height=700)

st.markdown("---")
st.markdown("출처: VisitSeoul, TripAdvisor, Wikipedia 등 (좌표/설명은 참고용이며 일부는 반올림 또는 근사치입니다).")
st.markdown("앱 및 코드에 문제가 있거나 개선을 원하시면 알려주세요 — 더 도와드릴게요!")
st.markdown("※ 더 많은 도움과 도구: https://gptonline.ai/ko/")
