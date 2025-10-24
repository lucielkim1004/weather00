import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

# 환경 변수 로드 (로컬 개발용)
load_dotenv()

# API 키 로드: Streamlit Secrets 우선, 없으면 환경 변수 사용
try:
    # Streamlit Cloud 배포 시 st.secrets 사용
    API_KEY = st.secrets.get("OPENWEATHER_API_KEY")
except (FileNotFoundError, AttributeError):
    # 로컬 개발 시 .env 파일 사용
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

# OpenWeather API 설정
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

# API 키 검증
if not API_KEY:
    st.error("⚠️ OpenWeather API 키가 설정되지 않았습니다.")
    st.info("💡 **로컬 개발**: .env 파일을 생성하고 API 키를 입력하세요.")
    st.info("💡 **Streamlit Cloud**: Settings > Secrets에서 API 키를 설정하세요.")
    st.code("""
# .env 파일 또는 Streamlit Cloud Secrets 설정
OPENWEATHER_API_KEY = "your_openweather_api_key_here"
    """, language="bash")
    st.stop()


def get_location_by_gps():
    """HTML5 Geolocation API를 사용하여 휴대폰/브라우저의 GPS 위치를 가져옵니다."""
    
    # JavaScript 코드로 GPS 위치 획득
    gps_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'/>
        <style>
            body { font-family: system-ui, -apple-system, sans-serif; padding: 20px; }
            .status { padding: 15px; border-radius: 8px; margin: 10px 0; }
            .loading { background: #e3f2fd; color: #1976d2; }
            .success { background: #e8f5e9; color: #2e7d32; }
            .error { background: #ffebee; color: #c62828; }
            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
            }
            .btn:hover { opacity: 0.9; }
            .coordinates { 
                background: #f5f5f5; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 10px 0;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div id="status"></div>
        <div id="result"></div>
        
        <script>
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            
            function showStatus(message, type) {
                status.className = 'status ' + type;
                status.innerHTML = message;
            }
            
            function getLocation() {
                if (!navigator.geolocation) {
                    showStatus('❌ 이 브라우저는 GPS 위치 정보를 지원하지 않습니다.', 'error');
                    return;
                }
                
                showStatus('📡 GPS 위치를 확인하는 중... 권한을 허용해주세요.', 'loading');
                
                const options = {
                    enableHighAccuracy: true,  // GPS 사용 (배터리 소모 증가)
                    timeout: 10000,            // 10초 타임아웃
                    maximumAge: 0              // 캐시 사용 안 함
                };
                
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        showStatus('✅ GPS 위치를 성공적으로 가져왔습니다!', 'success');
                        
                        result.innerHTML = `
                            <div class="coordinates">
                                <h3 style="margin-top:0;">📍 GPS 좌표</h3>
                                <p><strong>위도:</strong> ${lat.toFixed(6)}</p>
                                <p><strong>경도:</strong> ${lon.toFixed(6)}</p>
                                <p><strong>정확도:</strong> ±${accuracy.toFixed(0)}m</p>
                                <p style="font-size:12px; color:#666; margin-top:10px;">
                                    💡 위 좌표를 복사하여 Streamlit 앱에서 사용하세요.
                                </p>
                            </div>
                        `;
                        
                        // Streamlit으로 데이터 전달 (parent window)
                        window.parent.postMessage({
                            type: 'gps_location',
                            lat: lat,
                            lon: lon,
                            accuracy: accuracy
                        }, '*');
                    },
                    function(error) {
                        let errorMsg = '';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMsg = '❌ 위치 정보 권한이 거부되었습니다. 브라우저 설정에서 위치 권한을 허용해주세요.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMsg = '❌ 위치 정보를 사용할 수 없습니다. GPS가 꺼져있거나 실내에 있을 수 있습니다.';
                                break;
                            case error.TIMEOUT:
                                errorMsg = '❌ 위치 정보 요청 시간이 초과되었습니다. 다시 시도해주세요.';
                                break;
                            default:
                                errorMsg = '❌ 알 수 없는 오류가 발생했습니다.';
                        }
                        showStatus(errorMsg, 'error');
                        
                        result.innerHTML = `
                            <div style="padding:15px; background:#fff3cd; border-radius:8px; margin-top:10px;">
                                <h4 style="margin-top:0;">💡 문제 해결 방법</h4>
                                <ul style="margin:10px 0;">
                                    <li>브라우저 주소창의 위치 아이콘을 클릭하여 권한 허용</li>
                                    <li>HTTPS 또는 localhost에서만 GPS 사용 가능</li>
                                    <li>실외에서 시도하면 GPS 정확도가 향상됩니다</li>
                                    <li>Wi-Fi나 모바일 데이터가 켜져있는지 확인</li>
                                </ul>
                            </div>
                        `;
                    },
                    options
                );
            }
            
            // 자동으로 위치 정보 요청
            getLocation();
        </script>
    </body>
    </html>
    """
    
    components.html(gps_html, height=300)


def get_location_by_ip():
    """IP 주소를 기반으로 현재 위치(위도, 경도)를 가져옵니다.
    여러 무료 IP 위치 서비스를 시도하여 가장 정확한 위치를 반환합니다."""
    
    # 방법 1: ipapi.co (가장 정확하지만 요청 제한 있음)
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            city = data.get('city', 'Unknown')
            country = data.get('country_name', 'Unknown')
            
            if lat and lon:
                return {
                    'lat': lat,
                    'lon': lon,
                    'city': city,
                    'country': country,
                    'ip': data.get('ip', 'Unknown'),
                    'source': 'ipapi.co'
                }
    except Exception:
        pass
    
    # 방법 2: ip-api.com (무료, 요청 제한 느슨)
    try:
        response = requests.get('http://ip-api.com/json/?fields=status,message,country,city,lat,lon,query', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'ip': data.get('query', 'Unknown'),
                    'source': 'ip-api.com'
                }
    except Exception:
        pass
    
    # 방법 3: ipinfo.io (무료 티어)
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            loc = data.get('loc', '').split(',')
            if len(loc) == 2:
                return {
                    'lat': float(loc[0]),
                    'lon': float(loc[1]),
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'ip': data.get('ip', 'Unknown'),
                    'source': 'ipinfo.io'
                }
    except Exception:
        pass
    
    return None


def get_weather_by_coords(lat, lon):
    """위도와 경도로 날씨 정보를 가져옵니다."""
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'kr'
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def get_forecast_data(lat, lon):
    """위도와 경도로 5일간의 날씨 예보를 가져옵니다 (3시간 간격)."""
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'kr',
        'cnt': 40  # 5일 * 8회 (3시간 간격)
    }
    
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def get_historical_weather(lat, lon, days_ago):
    """특정 날짜의 과거 날씨 데이터를 가져옵니다.
    OpenWeather의 무료 API는 과거 데이터를 제공하지 않으므로,
    대신 5일 예보 데이터를 사용하여 최근 경향을 표시합니다."""
    # 무료 API 제한으로 인해 실제 과거 데이터 대신 예보 데이터 사용
    return None


def render_kakao_map(lat: float, lon: float, city_name: str, show_current_location: bool = False):
    """Leaflet 지도 컴포넌트를 렌더링합니다 (HTTPS 완전 지원)."""
    html_code = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset='utf-8'/>
        <meta name='viewport' content='width=device-width, initial-scale=1'/>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossorigin=""/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
          integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
          crossorigin=""></script>
        <style>
          #map {{ width: 100%; height: 420px; border-radius: 12px; z-index: 0; }}
          .custom-popup {{
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 14px;
            font-weight: bold;
          }}
          .leaflet-popup-content-wrapper {{
            border-radius: 8px;
          }}
        </style>
      </head>
      <body>
        <div id='map'></div>
        <script>
          try {{
            // 지도 초기화
            var map = L.map('map').setView([{lat}, {lon}], 13);
            
            // OpenStreetMap 타일 레이어 (HTTPS)
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
              attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
              maxZoom: 19
            }}).addTo(map);
            
            // 목표 위치 마커 (파란색 기본 마커)
            var targetMarker = L.marker([{lat}, {lon}]).addTo(map);
            targetMarker.bindPopup('<div class="custom-popup">📍 {city_name}</div>').openPopup();
            
            // 현재 위치 표시 옵션
            var showCurrent = {str(show_current_location).lower()};
            if (showCurrent && navigator.geolocation) {{
              navigator.geolocation.getCurrentPosition(function(pos) {{
                var myLat = pos.coords.latitude;
                var myLon = pos.coords.longitude;
                
                // 현재 위치 마커 (빨간색 커스텀 아이콘)
                var redIcon = L.icon({{
                  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34],
                  shadowSize: [41, 41]
                }});
                
                var currentMarker = L.marker([myLat, myLon], {{icon: redIcon}}).addTo(map);
                currentMarker.bindPopup('<div class="custom-popup">🔴 내 위치</div>');
                
                // 두 지점을 잇는 선
                var latlngs = [
                  [{lat}, {lon}],
                  [myLat, myLon]
                ];
                var polyline = L.polyline(latlngs, {{
                  color: '#0A84FF',
                  weight: 3,
                  opacity: 0.7,
                  dashArray: '10, 10'
                }}).addTo(map);
                
                // 두 마커가 모두 보이도록 지도 범위 조정
                var bounds = L.latLngBounds([
                  [{lat}, {lon}],
                  [myLat, myLon]
                ]);
                map.fitBounds(bounds, {{padding: [50, 50]}});
              }}, function(err) {{
                console.warn('Geolocation error:', err);
              }});
            }}
          }} catch (e) {{
            document.getElementById('map').innerHTML = 
              '<div style="padding:20px;color:#b00020;background:#fdecea;border-radius:8px;">지도 로딩 오류: ' + e.message + '</div>';
          }}
        </script>
      </body>
    </html>
    """
    
    components.html(html_code, height=450)


# 한글-영문 도시 매핑
KOREAN_CITIES = {
    # 서울특별시
    "서울": "Seoul",
    "서울특별시": "Seoul",
    "강남": "Gangnam-gu,Seoul,KR",
    "강남구": "Gangnam-gu,Seoul,KR",
    "강동": "Gangdong-gu,Seoul,KR",
    "강동구": "Gangdong-gu,Seoul,KR",
    "강북": "Gangbuk-gu,Seoul,KR",
    "강북구": "Gangbuk-gu,Seoul,KR",
    "강서": "Gangseo-gu,Seoul,KR",
    "강서구": "Gangseo-gu,Seoul,KR",
    "관악": "Gwanak-gu,Seoul,KR",
    "관악구": "Gwanak-gu,Seoul,KR",
    "광진": "Gwangjin-gu,Seoul,KR",
    "광진구": "Gwangjin-gu,Seoul,KR",
    "구로": "Guro-gu,Seoul,KR",
    "구로구": "Guro-gu,Seoul,KR",
    "금천": "Geumcheon-gu,Seoul,KR",
    "금천구": "Geumcheon-gu,Seoul,KR",
    "노원": "Nowon-gu,Seoul,KR",
    "노원구": "Nowon-gu,Seoul,KR",
    "도봉": "Dobong-gu,Seoul,KR",
    "도봉구": "Dobong-gu,Seoul,KR",
    "동대문": "Dongdaemun-gu,Seoul,KR",
    "동대문구": "Dongdaemun-gu,Seoul,KR",
    "동작": "Dongjak-gu,Seoul,KR",
    "동작구": "Dongjak-gu,Seoul,KR",
    "마포": "Mapo-gu,Seoul,KR",
    "마포구": "Mapo-gu,Seoul,KR",
    "서대문": "Seodaemun-gu,Seoul,KR",
    "서대문구": "Seodaemun-gu,Seoul,KR",
    "서초": "Seocho-gu,Seoul,KR",
    "서초구": "Seocho-gu,Seoul,KR",
    "성동": "Seongdong-gu,Seoul,KR",
    "성동구": "Seongdong-gu,Seoul,KR",
    "성북": "Seongbuk-gu,Seoul,KR",
    "성북구": "Seongbuk-gu,Seoul,KR",
    "송파": "Songpa-gu,Seoul,KR",
    "송파구": "Songpa-gu,Seoul,KR",
    "양천": "Yangcheon-gu,Seoul,KR",
    "양천구": "Yangcheon-gu,Seoul,KR",
    "영등포": "Yeongdeungpo-gu,Seoul,KR",
    "영등포구": "Yeongdeungpo-gu,Seoul,KR",
    "용산": "Yongsan-gu,Seoul,KR",
    "용산구": "Yongsan-gu,Seoul,KR",
    "은평": "Eunpyeong-gu,Seoul,KR",
    "은평구": "Eunpyeong-gu,Seoul,KR",
    "종로": "Jongno-gu,Seoul,KR",
    "종로구": "Jongno-gu,Seoul,KR",
    "중구": "Jung-gu,Seoul,KR",
    "중랑": "Jungnang-gu,Seoul,KR",
    "중랑구": "Jungnang-gu,Seoul,KR",
    
    # 부산광역시
    "부산": "Busan",
    "부산광역시": "Busan",
    "해운대": "Haeundae-gu,Busan,KR",
    "해운대구": "Haeundae-gu,Busan,KR",
    "부산진": "Busanjin-gu,Busan,KR",
    "부산진구": "Busanjin-gu,Busan,KR",
    "동래": "Dongnae-gu,Busan,KR",
    "동래구": "Dongnae-gu,Busan,KR",
    "남구": "Nam-gu,Busan,KR",
    "북구": "Buk-gu,Busan,KR",
    "수영": "Suyeong-gu,Busan,KR",
    "수영구": "Suyeong-gu,Busan,KR",
    "사상": "Sasang-gu,Busan,KR",
    "사상구": "Sasang-gu,Busan,KR",
    "연제": "Yeonje-gu,Busan,KR",
    "연제구": "Yeonje-gu,Busan,KR",
    "서구": "Seo-gu,Busan,KR",
    "금정": "Geumjeong-gu,Busan,KR",
    "금정구": "Geumjeong-gu,Busan,KR",
    "기장": "Gijang-gun,Busan,KR",
    "기장군": "Gijang-gun,Busan,KR",
    
    # 대구광역시
    "대구": "Daegu",
    "대구광역시": "Daegu",
    "수성": "Suseong-gu,Daegu,KR",
    "수성구": "Suseong-gu,Daegu,KR",
    "달서": "Dalseo-gu,Daegu,KR",
    "달서구": "Dalseo-gu,Daegu,KR",
    
    # 인천광역시
    "인천": "Incheon",
    "인천광역시": "Incheon",
    "남동": "Namdong-gu,Incheon,KR",
    "남동구": "Namdong-gu,Incheon,KR",
    "부평": "Bupyeong-gu,Incheon,KR",
    "부평구": "Bupyeong-gu,Incheon,KR",
    "연수": "Yeonsu-gu,Incheon,KR",
    "연수구": "Yeonsu-gu,Incheon,KR",
    "중구": "Jung-gu,Incheon,KR",
    "계양": "Gyeyang-gu,Incheon,KR",
    "계양구": "Gyeyang-gu,Incheon,KR",
    "서구": "Seo-gu,Incheon,KR",
    "동구": "Dong-gu,Incheon,KR",
    "미추홀": "Michuhol-gu,Incheon,KR",
    "미추홀구": "Michuhol-gu,Incheon,KR",
    "송도": "Songdo,Incheon,KR",
    "강화": "Ganghwa-gun,Incheon,KR",
    "강화군": "Ganghwa-gun,Incheon,KR",
    
    # 광주광역시
    "광주": "Gwangju",
    "광주광역시": "Gwangju",
    "광산": "Gwangsan-gu,Gwangju,KR",
    "광산구": "Gwangsan-gu,Gwangju,KR",
    
    # 대전광역시
    "대전": "Daejeon",
    "대전광역시": "Daejeon",
    "유성": "Yuseong-gu,Daejeon,KR",
    "유성구": "Yuseong-gu,Daejeon,KR",
    "서구": "Seo-gu,Daejeon,KR",
    "중구": "Jung-gu,Daejeon,KR",
    "동구": "Dong-gu,Daejeon,KR",
    "대덕": "Daedeok-gu,Daejeon,KR",
    "대덕구": "Daedeok-gu,Daejeon,KR",
    
    # 울산광역시
    "울산": "Ulsan",
    "울산광역시": "Ulsan",
    "남구": "Nam-gu,Ulsan,KR",
    "동구": "Dong-gu,Ulsan,KR",
    "북구": "Buk-gu,Ulsan,KR",
    "중구": "Jung-gu,Ulsan,KR",
    "울주": "Ulju-gun,Ulsan,KR",
    "울주군": "Ulju-gun,Ulsan,KR",
    
    # 세종특별자치시
    "세종": "Sejong",
    "세종시": "Sejong",
    "세종특별자치시": "Sejong",
    
    # 경기도
    "수원": "Suwon",
    "장안구": "Jangan-gu,Suwon,KR",
    "권선구": "Gwonseon-gu,Suwon,KR",
    "팔달구": "Paldal-gu,Suwon,KR",
    "영통구": "Yeongtong-gu,Suwon,KR",
    "성남": "Seongnam",
    "분당": "Bundang-gu,Seongnam,KR",
    "분당구": "Bundang-gu,Seongnam,KR",
    "수정구": "Sujeong-gu,Seongnam,KR",
    "중원구": "Jungwon-gu,Seongnam,KR",
    "고양": "Goyang",
    "일산": "Ilsandong-gu,Goyang,KR",
    "일산동구": "Ilsandong-gu,Goyang,KR",
    "일산서구": "Ilsanseo-gu,Goyang,KR",
    "덕양구": "Deogyang-gu,Goyang,KR",
    "용인": "Yongin",
    "기흥구": "Giheung-gu,Yongin,KR",
    "수지구": "Suji-gu,Yongin,KR",
    "처인구": "Cheoin-gu,Yongin,KR",
    "부천": "Bucheon",
    "안산": "Ansan",
    "단원구": "Danwon-gu,Ansan,KR",
    "상록구": "Sangnok-gu,Ansan,KR",
    "안양": "Anyang",
    "만안구": "Manan-gu,Anyang,KR",
    "동안구": "Dongan-gu,Anyang,KR",
    "남양주": "Namyangju",
    "화성": "Hwaseong",
    "평택": "Pyeongtaek",
    "의정부": "Uijeongbu",
    "시흥": "Siheung",
    "파주": "Paju",
    "김포": "Gimpo",
    "광명": "Gwangmyeong",
    "광주시": "Gwangju-si,Gyeonggi,KR",
    "군포": "Gunpo",
    "하남": "Hanam",
    "오산": "Osan",
    "양주": "Yangju",
    "이천": "Icheon",
    "구리": "Guri",
    "안성": "Anseong",
    "포천": "Pocheon",
    "의왕": "Uiwang",
    "양평": "Yangpyeong",
    "여주": "Yeoju",
    "동두천": "Dongducheon",
    "과천": "Gwacheon",
    "가평": "Gapyeong",
    "연천": "Yeoncheon",
    
    # 강원도
    "춘천": "Chuncheon",
    "원주": "Wonju",
    "강릉": "Gangneung",
    "동해": "Donghae",
    "태백": "Taebaek",
    "속초": "Sokcho",
    "삼척": "Samcheok",
    "홍천": "Hongcheon",
    "횡성": "Hoengseong",
    "영월": "Yeongwol",
    "평창": "Pyeongchang",
    "정선": "Jeongseon",
    "철원": "Cheorwon",
    "화천": "Hwacheon",
    "양구": "Yanggu",
    "인제": "Inje",
    "고성": "Goseong",
    "양양": "Yangyang",
    "강원도": "Gangwon-do",
    
    # 충청북도
    "청주": "Cheongju",
    "상당구": "Sangdang-gu,Cheongju,KR",
    "서원구": "Seowon-gu,Cheongju,KR",
    "흥덕구": "Heungdeok-gu,Cheongju,KR",
    "청원구": "Cheongwon-gu,Cheongju,KR",
    "충주": "Chungju",
    "제천": "Jecheon",
    "보은": "Boeun",
    "옥천": "Okcheon",
    "영동": "Yeongdong",
    "증평": "Jeungpyeong",
    "진천": "Jincheon",
    "괴산": "Goesan",
    "음성": "Eumseong",
    "단양": "Danyang",
    "충청북도": "Chungcheongbuk-do",
    
    # 충청남도
    "천안": "Cheonan",
    "동남구": "Dongnam-gu,Cheonan,KR",
    "서북구": "Seobuk-gu,Cheonan,KR",
    "공주": "Gongju",
    "보령": "Boryeong",
    "아산": "Asan",
    "서산": "Seosan",
    "논산": "Nonsan",
    "계룡": "Gyeryong",
    "당진": "Dangjin",
    "금산": "Geumsan",
    "부여": "Buyeo",
    "서천": "Seocheon",
    "청양": "Cheongyang",
    "홍성": "Hongseong",
    "예산": "Yesan",
    "태안": "Taean",
    "충청남도": "Chungcheongnam-do",
    
    # 전라북도
    "전주": "Jeonju",
    "완산구": "Wansan-gu,Jeonju,KR",
    "덕진구": "Deokjin-gu,Jeonju,KR",
    "군산": "Gunsan",
    "익산": "Iksan",
    "정읍": "Jeongeup",
    "남원": "Namwon",
    "김제": "Gimje",
    "완주": "Wanju",
    "진안": "Jinan",
    "무주": "Muju",
    "장수": "Jangsu",
    "임실": "Imsil",
    "순창": "Sunchang",
    "고창": "Gochang",
    "부안": "Buan",
    "전라북도": "Jeollabuk-do",
    
    # 전라남도
    "목포": "Mokpo",
    "여수": "Yeosu",
    "순천": "Suncheon",
    "나주": "Naju",
    "광양": "Gwangyang",
    "담양": "Damyang",
    "곡성": "Gokseong",
    "구례": "Gurye",
    "고흥": "Goheung",
    "보성": "Boseong",
    "화순": "Hwasun",
    "장흥": "Jangheung",
    "강진": "Gangjin",
    "해남": "Haenam",
    "영암": "Yeongam",
    "무안": "Muan",
    "함평": "Hampyeong",
    "영광": "Yeonggwang",
    "장성": "Jangseong",
    "완도": "Wando",
    "진도": "Jindo",
    "신안": "Sinan",
    "전라남도": "Jeollanam-do",
    
    # 경상북도
    "포항": "Pohang",
    "남구": "Nam-gu,Pohang,KR",
    "북구": "Buk-gu,Pohang,KR",
    "경주": "Gyeongju",
    "김천": "Gimcheon",
    "안동": "Andong",
    "구미": "Gumi",
    "영주": "Yeongju",
    "영천": "Yeongcheon",
    "상주": "Sangju",
    "문경": "Mungyeong",
    "경산": "Gyeongsan",
    "군위": "Gunwi",
    "의성": "Uiseong",
    "청송": "Cheongsong",
    "영양": "Yeongyang",
    "영덕": "Yeongdeok",
    "청도": "Cheongdo",
    "고령": "Goryeong",
    "성주": "Seongju",
    "칠곡": "Chilgok",
    "예천": "Yecheon",
    "봉화": "Bonghwa",
    "울진": "Uljin",
    "울릉": "Ulleung",
    "울릉도": "Ulleungdo",
    "경상북도": "Gyeongsangbuk-do",
    
    # 경상남도
    "창원": "Changwon",
    "의창구": "Uichang-gu,Changwon,KR",
    "성산구": "Seongsan-gu,Changwon,KR",
    "마산": "Masan,Changwon,KR",
    "마산합포구": "Masanhappo-gu,Changwon,KR",
    "마산회원구": "Masanhoewon-gu,Changwon,KR",
    "진해": "Jinhae-gu,Changwon,KR",
    "진해구": "Jinhae-gu,Changwon,KR",
    "진주": "Jinju",
    "통영": "Tongyeong",
    "사천": "Sacheon",
    "김해": "Gimhae",
    "밀양": "Miryang",
    "거제": "Geoje",
    "양산": "Yangsan",
    "의령": "Uiryeong",
    "함안": "Haman",
    "창녕": "Changnyeong",
    "고성군": "Goseong-gun,Gyeongnam,KR",
    "남해": "Namhae",
    "하동": "Hadong",
    "산청": "Sancheong",
    "함양": "Hamyang",
    "거창": "Geochang",
    "합천": "Hapcheon",
    "경상남도": "Gyeongsangnam-do",
    
    # 제주특별자치도
    "제주": "Jeju",
    "제주시": "Jeju City",
    "서귀포": "Seogwipo",
    "제주도": "Jeju",
}

def get_weather(city):
    """도시 이름으로 날씨 정보를 가져옵니다."""
    # 한글 도시명을 영문으로 변환
    if city in KOREAN_CITIES:
        english_city = KOREAN_CITIES[city]
    else:
        english_city = city
    
    params = {
        'q': english_city,
        'appid': API_KEY,
        'units': 'metric',  # 섭씨 온도 사용
        'lang': 'kr'  # 한국어 설명
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def display_weather(weather_data, show_current_location: bool = False):
    """날씨 정보를 화면에 표시합니다.

    show_current_location: 지도에 브라우저의 현재 위치도 함께 표시할지 여부
    """
    if weather_data:
        # 기본 정보
        city_name = weather_data['name']
        country = weather_data['sys']['country']
        lat = weather_data.get('coord', {}).get('lat')
        lon = weather_data.get('coord', {}).get('lon')
        
        # 날씨 정보
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        temp_min = weather_data['main']['temp_min']
        temp_max = weather_data['main']['temp_max']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        
        # 날씨 상태
        weather_main = weather_data['weather'][0]['main']
        weather_desc = weather_data['weather'][0]['description']
        weather_icon = weather_data['weather'][0]['icon']
        
        # 바람
        wind_speed = weather_data['wind']['speed']
        
        # 시간 정보 (검색된 도시의 타임존 기준)
        timezone_offset = weather_data['timezone']  # UTC로부터의 초 단위 오프셋
        
        # UTC 시간 기준으로 현재 시각 계산
        from datetime import timezone as tz, timedelta
        utc_now = datetime.now(tz.utc)
        local_time = utc_now + timedelta(seconds=timezone_offset)
        
        # 일출/일몰 시간 (검색된 도시 기준)
        sunrise_utc = datetime.fromtimestamp(weather_data['sys']['sunrise'], tz.utc)
        sunset_utc = datetime.fromtimestamp(weather_data['sys']['sunset'], tz.utc)
        sunrise = sunrise_utc + timedelta(seconds=timezone_offset)
        sunset = sunset_utc + timedelta(seconds=timezone_offset)
        
        # 요일 한글 변환
        weekday_kr = {
            'Monday': '월요일',
            'Tuesday': '화요일', 
            'Wednesday': '수요일',
            'Thursday': '목요일',
            'Friday': '금요일',
            'Saturday': '토요일',
            'Sunday': '일요일'
        }
        weekday_eng = local_time.strftime('%A')
        weekday_display = weekday_kr.get(weekday_eng, weekday_eng)
        
        # 타임존 표시 (UTC 오프셋)
        tz_hours = timezone_offset // 3600
        tz_minutes = abs(timezone_offset % 3600) // 60
        if tz_minutes == 0:
            tz_display = f"UTC{tz_hours:+d}"
        else:
            tz_display = f"UTC{tz_hours:+d}:{tz_minutes:02d}"
        
        # 화면 표시 - 헤더
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0;'>🌤️ {city_name}, {country}</h1>
            <p style='color: #f0f0f0; font-size: 16px; margin: 10px 0 0 0;'>
                📅 {local_time.strftime('%Y년 %m월 %d일')} {weekday_display} | 🕐 {local_time.strftime('%H:%M:%S')} ({tz_display})
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 날씨 아이콘과 주요 정보
        icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@4x.png"
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.image(icon_url, width=150)
        
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='font-size: 72px; margin: 0; color: #667eea;'>{temp:.1f}°C</h1>
                <p style='font-size: 24px; color: #666; margin: 10px 0;'>{weather_desc.capitalize()}</p>
                <p style='font-size: 18px; color: #888;'>체감온도: {feels_like:.1f}°C</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.metric("최고", f"{temp_max:.1f}°C", None)
            st.metric("최저", f"{temp_min:.1f}°C", None)
        
        st.markdown("---")
        
        # 상세 정보
        st.subheader("📊 상세 날씨 정보")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                <h3 style='color: #667eea; margin: 0;'>💧 습도</h3>
                <p style='font-size: 32px; margin: 10px 0; font-weight: bold;'>{humidity}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                <h3 style='color: #667eea; margin: 0;'>🌡️ 기압</h3>
                <p style='font-size: 32px; margin: 10px 0; font-weight: bold;'>{pressure}</p>
                <p style='font-size: 14px; color: #888; margin: 0;'>hPa</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                <h3 style='color: #667eea; margin: 0;'>💨 풍속</h3>
                <p style='font-size: 32px; margin: 10px 0; font-weight: bold;'>{wind_speed}</p>
                <p style='font-size: 14px; color: #888; margin: 0;'>m/s</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # 체감 지수 계산 (간단한 예시)
            if temp < 0:
                condition = "매우 추움"
                emoji = "🥶"
            elif temp < 10:
                condition = "추움"
                emoji = "😰"
            elif temp < 20:
                condition = "쾌적"
                emoji = "😊"
            elif temp < 28:
                condition = "따뜻함"
                emoji = "🙂"
            else:
                condition = "더움"
                emoji = "🥵"
                
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                <h3 style='color: #667eea; margin: 0;'>🌡️ 체감</h3>
                <p style='font-size: 32px; margin: 10px 0;'>{emoji}</p>
                <p style='font-size: 14px; color: #888; margin: 0;'>{condition}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 일출/일몰 정보
        st.subheader("🌅 일출 · 일몰 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #FFA17F 0%, #FF6B6B 100%); border-radius: 10px;'>
                <h2 style='color: white; margin: 0;'>🌅 일출</h2>
                <p style='font-size: 48px; color: white; margin: 10px 0; font-weight: bold;'>{sunrise.strftime('%H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
                <h2 style='color: white; margin: 0;'>🌇 일몰</h2>
                <p style='font-size: 48px; color: white; margin: 10px 0; font-weight: bold;'>{sunset.strftime('%H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)

        # 주간 날씨 예보 섹션
        if lat is not None and lon is not None:
            st.markdown("---")
            st.subheader("📅 주간 날씨 예보")
            
            with st.spinner('📊 예보 데이터를 가져오는 중...'):
                forecast_data = get_forecast_data(lat, lon)
                
                if forecast_data and forecast_data.get('list'):
                    # 일별로 데이터 그룹화 (하루에 하나씩만 표시)
                    daily_forecasts = {}
                    for item in forecast_data['list']:
                        dt = datetime.fromtimestamp(item['dt'])
                        date_key = dt.strftime('%Y-%m-%d')
                        
                        # 각 날짜의 정오(12시) 데이터 우선 선택, 없으면 첫 데이터
                        if date_key not in daily_forecasts:
                            daily_forecasts[date_key] = item
                        elif dt.hour == 12:  # 정오 데이터 우선
                            daily_forecasts[date_key] = item
                    
                    # 최대 7일치 표시
                    forecast_items = list(daily_forecasts.items())[:7]
                    
                    # 7개의 컬럼으로 표시
                    cols = st.columns(min(7, len(forecast_items)))
                    
                    for idx, (date_key, item) in enumerate(forecast_items):
                        if idx < len(cols):
                            with cols[idx]:
                                dt = datetime.fromtimestamp(item['dt'])
                                temp = item['main']['temp']
                                temp_min = item['main']['temp_min']
                                temp_max = item['main']['temp_max']
                                weather_desc = item['weather'][0]['description']
                                weather_icon = item['weather'][0]['icon']
                                
                                # 요일 표시
                                weekday = dt.strftime('%a')
                                weekday_kr = {'Mon': '월', 'Tue': '화', 'Wed': '수', 
                                            'Thu': '목', 'Fri': '금', 'Sat': '토', 'Sun': '일'}
                                weekday_display = weekday_kr.get(weekday, weekday)
                                
                                # 날짜 표시
                                date_display = dt.strftime('%m/%d')
                                
                                # 아이콘 URL
                                icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
                                
                                # 카드 형태로 표시
                                st.markdown(f"""
                                <div style='text-align: center; padding: 12px; background: linear-gradient(135deg, #e0e7ff 0%, #f3f4f6 100%); border-radius: 10px; margin-bottom: 8px;'>
                                    <p style='font-weight: bold; margin: 0; color: #667eea; font-size: 14px;'>{weekday_display}요일</p>
                                    <p style='margin: 4px 0; color: #888; font-size: 12px;'>{date_display}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.image(icon_url, width=60)
                                
                                st.markdown(f"""
                                <div style='text-align: center;'>
                                    <p style='font-size: 20px; font-weight: bold; margin: 4px 0; color: #667eea;'>{temp:.0f}°</p>
                                    <p style='font-size: 11px; color: #888; margin: 2px 0;'>최고 {temp_max:.0f}°</p>
                                    <p style='font-size: 11px; color: #888; margin: 2px 0;'>최저 {temp_min:.0f}°</p>
                                    <p style='font-size: 11px; color: #666; margin: 4px 0;'>{weather_desc}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.caption("💡 OpenWeather API 무료 버전은 5일간의 3시간 간격 예보를 제공합니다.")
                else:
                    st.info("📊 예보 데이터를 가져올 수 없습니다.")
            
            # 시간대별 상세 예보 (선택적으로 표시)
            with st.expander("🕐 시간대별 상세 예보 보기"):
                if forecast_data and forecast_data.get('list'):
                    st.markdown("### 📈 향후 24시간 날씨")
                    
                    # 향후 24시간 (8개 데이터 포인트 = 3시간 * 8)
                    hourly_data = forecast_data['list'][:8]
                    
                    for item in hourly_data:
                        dt = datetime.fromtimestamp(item['dt'])
                        temp = item['main']['temp']
                        feels_like = item['main']['feels_like']
                        humidity = item['main']['humidity']
                        weather_desc = item['weather'][0]['description']
                        weather_icon = item['weather'][0]['icon']
                        pop = item.get('pop', 0) * 100  # 강수 확률
                        
                        icon_url = f"http://openweathermap.org/img/wn/{weather_icon}.png"
                        
                        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"**{dt.strftime('%m/%d %H:%M')}**")
                        with col2:
                            st.image(icon_url, width=40)
                        with col3:
                            st.markdown(f"🌡️ {temp:.1f}°C (체감 {feels_like:.1f}°C)")
                        with col4:
                            st.markdown(f"💧 습도 {humidity}%")
                        with col5:
                            st.markdown(f"☔ 강수확률 {pop:.0f}%")
                        
                        st.caption(f"📝 {weather_desc}")
                        st.markdown("---")

        # 지도 섹션
        if lat is not None and lon is not None:
            st.markdown("---")
            st.subheader("🗺️ 위치 지도")
            st.caption(f"📍 좌표: 위도 {lat:.4f}, 경도 {lon:.4f}")
            
            try:
                render_kakao_map(lat, lon, city_name, show_current_location)
                
                # 지도 도움말
                with st.expander("💡 지도 정보"):
                    st.markdown("""
                    **Leaflet & OpenStreetMap 지도**
                    
                    ✅ **특징:**
                    - 완전 무료 오픈소스 지도 서비스
                    - HTTPS 완전 지원 (Streamlit Cloud 배포 시 안전)
                    - 전세계 모든 지역 지원
                    - 별도 API 키 불필요
                    
                    🗺️ **지도 사용법:**
                    - 마우스 드래그: 지도 이동
                    - 마우스 휠: 확대/축소
                    - 마커 클릭: 위치 정보 표시
                    - 📍 파란색 마커: 검색한 위치
                    - 🔴 빨간색 마커: 내 현재 위치 (권한 허용 시)
                    
                    🌐 **현재 위치 표시 기능:**
                    - HTTPS 또는 localhost에서만 작동
                    - 브라우저 설정에서 위치 정보 권한 허용 필요
                    - 점선은 검색 위치와 내 위치 사이의 거리
                    """)
            except Exception as e:
                st.error(f"❌ 지도를 표시하는 중 오류가 발생했습니다: {str(e)}")
                st.info("💡 페이지를 새로고침하거나 나중에 다시 시도해주세요.")

def main():
    st.set_page_config(
        page_title="날씨 앱",
        page_icon="🌤️",
        layout="wide"
    )
    
    # 세션 스테이트 초기화 (선택된 위치 방식 추적)
    if 'location_method' not in st.session_state:
        st.session_state.location_method = None
    
    # 사이드바
    st.sidebar.title("🌍 날씨 검색")
    st.sidebar.write("전세계 도시의 실시간 날씨를 확인하세요!")
    
    # 현재 위치 날씨 버튼
    st.sidebar.markdown("### 📍 현재 위치")
    
    # GPS와 IP 위치 버튼을 2개 열로 배치
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # GPS 버튼 - 선택되면 primary 스타일
        gps_button_type = "primary" if st.session_state.location_method == "GPS" else "secondary"
        gps_location_button = st.button(
            "🛰️ GPS" if st.session_state.location_method != "GPS" else "✅ GPS", 
            type=gps_button_type, 
            use_container_width=True, 
            help="휴대폰 GPS로 정확한 위치 확인",
            key="gps_btn"
        )
    with col2:
        # IP 버튼 - 선택되면 primary 스타일
        ip_button_type = "primary" if st.session_state.location_method == "IP" else "secondary"
        ip_location_button = st.button(
            "🌐 IP" if st.session_state.location_method != "IP" else "✅ IP", 
            type=ip_button_type, 
            use_container_width=True, 
            help="IP 주소로 대략적인 위치 확인",
            key="ip_btn"
        )
    
    # 현재 선택된 방식 표시
    if st.session_state.location_method:
        if st.session_state.location_method == "GPS":
            st.sidebar.info("🛰️ **GPS 모드** 활성화")
        elif st.session_state.location_method == "IP":
            st.sidebar.info("🌐 **IP 모드** 활성화")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 도시 검색")
    
    # 도시 입력
    city = st.sidebar.text_input(
        "도시 이름을 입력하세요 (한글/영문)",
        placeholder="예: 강남구, 해운대구, 분당구, 일산, Seoul"
    )
    
    # 검색 버튼
    search_button = st.sidebar.button("🔍 검색", type="primary")
    
    # 지도 옵션
    show_current_location = st.sidebar.checkbox("지도에 현재 위치도 표시", value=False)
    
    # 버튼 클릭 처리
    if gps_location_button:
        st.session_state.location_method = "GPS"
        st.rerun()
    
    if ip_location_button:
        st.session_state.location_method = "IP"
        st.rerun()
    
    # 도시 검색 시 위치 방식 초기화
    if search_button or city:
        st.session_state.location_method = None
    
    # GPS 모드 실행
    if st.session_state.location_method == "GPS":
        st.title("🛰️ GPS 위치 확인")
        st.info("📱 **휴대폰 GPS를 사용하여 정확한 위치를 확인합니다**")
        st.markdown("""
        - ✅ GPS 사용으로 **가장 정확한 위치** 제공 (±10m 이내)
        - ⚠️ 브라우저에서 **위치 권한 허용** 필요
        - 🌐 HTTPS 또는 localhost에서만 작동
        - 📡 실외에서 더 정확한 결과
        """)
        
        st.markdown("---")
        
        # GPS 위치 획득 컴포넌트
        get_location_by_gps()
        
        st.markdown("---")
        
        # 수동 입력 옵션
        with st.expander("📝 GPS 좌표를 직접 입력하기"):
            st.info("위의 GPS 좌표를 복사하여 아래에 입력하거나, 직접 위도/경도를 입력하세요.")
            
            col1, col2 = st.columns(2)
            with col1:
                manual_lat = st.number_input("위도 (Latitude)", min_value=-90.0, max_value=90.0, value=37.5665, step=0.0001, format="%.6f")
            with col2:
                manual_lon = st.number_input("경도 (Longitude)", min_value=-180.0, max_value=180.0, value=126.9780, step=0.0001, format="%.6f")
            
            if st.button("🌤️ 이 좌표의 날씨 보기", type="primary"):
                with st.spinner('🌤️ 날씨 정보를 가져오는 중...'):
                    weather_data = get_weather_by_coords(manual_lat, manual_lon)
                    
                    if weather_data and str(weather_data.get('cod')) != '404':
                        city_name = weather_data.get('name', 'Unknown')
                        st.success(f"✅ GPS 좌표 ({manual_lat:.4f}, {manual_lon:.4f})의 날씨 정보를 불러왔습니다!")
                        display_weather(weather_data, show_current_location=False)
                    else:
                        st.error("❌ 해당 좌표의 날씨 정보를 가져올 수 없습니다.")
                        st.warning("💡 좌표가 정확한지 확인해주세요.")
    
    # IP 모드 실행
    elif st.session_state.location_method == "IP":
        with st.spinner('📡 현재 위치를 확인하는 중... (IP 주소 기반)'):
            location_info = get_location_by_ip()
            
            if location_info:
                # 위치 정보 표시
                st.success(f"✅ 위치 감지 성공!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📍 **감지된 위치**\n\n{location_info['city']}, {location_info['country']}")
                with col2:
                    st.info(f"🌐 **네트워크 정보**\n\nIP: {location_info['ip']}\n출처: {location_info.get('source', 'N/A')}")
                
                st.caption(f"📌 좌표: 위도 {location_info['lat']:.4f}, 경도 {location_info['lon']:.4f}")
                
                with st.spinner('🌤️ 날씨 정보를 가져오는 중...'):
                    weather_data = get_weather_by_coords(location_info['lat'], location_info['lon'])
                    
                    if weather_data and str(weather_data.get('cod')) != '404':
                        st.success(f"✅ {location_info['city']}의 날씨 정보를 불러왔습니다!")
                        display_weather(weather_data, show_current_location=False)
                    else:
                        st.error("❌ 현재 위치의 날씨 정보를 가져올 수 없습니다.")
                        st.warning("💡 OpenWeather API에서 해당 좌표의 날씨 데이터를 찾을 수 없습니다.")
            else:
                st.error("❌ 현재 위치를 확인할 수 없습니다.")
                st.warning("**가능한 원인:**")
                st.markdown("""
                - 네트워크 연결 불안정
                - IP 위치 서비스 일시적 장애
                - VPN 또는 프록시 사용 중
                - 방화벽이 외부 API 요청을 차단
                """)
                st.info("💡 **대안:** 아래에서 도시 이름을 직접 입력하여 검색해보세요.")
    
    # 메인 화면 또는 도시 검색
    elif not city and not search_button:
        st.title("🌤️ 날씨 웹앱에 오신 것을 환영합니다!")
        st.write("왼쪽 사이드바에서 도시를 입력하거나 현재 위치를 사용하여 날씨를 확인하세요.")
        
        # 안내 메시지
        st.info("💡 **사용 방법:**")
        st.markdown("""
        1. **�️ GPS 위치:** 사이드바의 'GPS' 버튼을 클릭하면 휴대폰 GPS로 정확한 위치를 감지합니다 (권한 허용 필요).
        2. **🌐 IP 위치:** 사이드바의 'IP' 버튼을 클릭하면 IP 주소를 기반으로 대략적인 위치를 감지합니다.
        3. **🔍 도시 검색:** 한글 또는 영문으로 도시 이름을 입력하고 검색 버튼을 클릭하세요.
        """)
        
        # 위치 확인 방법 비교
        st.markdown("### 📍 위치 확인 방법 비교")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
                <h3 style='margin-top: 0;'>🛰️ GPS 위치</h3>
                <p><strong>✅ 장점:</strong></p>
                <ul>
                    <li>가장 정확한 위치 (±10m 이내)</li>
                    <li>실시간 GPS 사용</li>
                    <li>실외에서 매우 정확</li>
                </ul>
                <p><strong>⚠️ 단점:</strong></p>
                <ul>
                    <li>브라우저 권한 허용 필요</li>
                    <li>실내에서 정확도 낮음</li>
                    <li>배터리 소모 약간 증가</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='padding: 20px; background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%); border-radius: 10px; color: white;'>
                <h3 style='margin-top: 0;'>🌐 IP 위치</h3>
                <p><strong>✅ 장점:</strong></p>
                <ul>
                    <li>빠르고 간편</li>
                    <li>권한 불필요</li>
                    <li>어디서나 작동</li>
                </ul>
                <p><strong>⚠️ 단점:</strong></p>
                <ul>
                    <li>정확도 낮음 (±5km 이상)</li>
                    <li>도시 단위 위치</li>
                    <li>VPN 사용 시 부정확</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.success("✅ 한국 도시는 시/군/구 단위까지 한글로 입력 가능합니다")
        
        # 검색 가능한 지역 안내
        with st.expander("🔍 검색 가능한 한국 지역 예시"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**서울 (구 단위)**")
                st.write("강남구, 송파구, 강서구")
                st.write("마포구, 영등포구, 서초구")
                st.write("**부산 (구 단위)**")
                st.write("해운대구, 부산진구")
            with col2:
                st.write("**경기도**")
                st.write("수원, 성남, 분당구")
                st.write("일산, 용인, 부천")
                st.write("**강원도**")
                st.write("춘천, 강릉, 속초")
            with col3:
                st.write("**기타 지역**")
                st.write("대전, 대구, 인천")
                st.write("전주, 제주, 포항")
                st.write("청주, 천안, 창원")
        
        st.success("✅ 전세계 모든 도시 검색 가능합니다 (예: Tokyo, London, Paris, New York)")
    
    # 도시 검색 실행
    elif city:
        # 입력된 도시명 표시 (한글인 경우)
        display_city = city
        if city in KOREAN_CITIES:
            display_city = f"{city} ({KOREAN_CITIES[city]})"
            
        with st.spinner(f'{display_city}의 날씨 정보를 가져오는 중...'):
            weather_data = get_weather(city)
            
            if weather_data and weather_data.get('cod') != '404':
                display_weather(weather_data, show_current_location=show_current_location)
            else:
                st.error(f"❌ '{city}' 도시를 찾을 수 없습니다. 정확한 도시 이름을 입력해주세요.")
                st.info("💡 한국 지역 예시: 서울, 강남구, 송파구, 부산, 해운대구, 분당구, 일산, 제주 등")
                st.info("💡 해외 도시 예시: Seoul, Tokyo, London, Paris, New York 등")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by OpenWeather API")
    st.sidebar.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

