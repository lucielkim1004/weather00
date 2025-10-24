# 🌤️ 날씨 웹앱

OpenWeather API와 Kakao Maps를 활용한 실시간 날씨 정보 제공 웹 애플리케이션

## ✨ 주요 기능

- 🌍 **전세계 도시 날씨 검색** - 한글 및 영문 도시명 지원
- 📍 **현재 위치 기반 날씨** - IP 주소를 이용한 자동 위치 감지
- 📊 **상세 날씨 정보** - 온도, 습도, 기압, 풍속, 일출/일몰 시간
- 📅 **주간 날씨 예보** - 5일간의 일별 날씨 예보
- 🕐 **시간대별 예보** - 향후 24시간 3시간 간격 상세 예보
- 🗺️ **Kakao 지도** - 검색한 도시의 위치 표시

## 🚀 시작하기

### 1. 필수 요구사항

- Python 3.7 이상
- pip (Python 패키지 관리자)

### 2. 설치

```bash
# 저장소 클론
git clone <your-repository-url>
cd weather00

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 3. API 키 설정

#### OpenWeather API 키 발급
1. [OpenWeather](https://openweathermap.org/api) 접속
2. 무료 계정 생성
3. API Keys 메뉴에서 API 키 복사

#### Kakao Maps API 키 발급
1. [Kakao Developers](https://developers.kakao.com) 접속
2. 애플리케이션 추가
3. 앱 설정 > 플랫폼 > Web 플랫폼 추가
4. 사이트 도메인에 `http://localhost:8501` 추가
5. JavaScript 키 복사

#### 환경 변수 파일 생성
```bash
# .env.example 파일을 .env로 복사
cp .env.example .env

# .env 파일을 열어 API 키 입력
# Windows: notepad .env
# Mac/Linux: nano .env
```

`.env` 파일 내용:
```
OPENWEATHER_API_KEY=your_openweather_api_key_here
KAKAO_JS_KEY=your_kakao_js_key_here
```

### 4. 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱이 실행됩니다.

## 📖 사용 방법

### 현재 위치 날씨
1. 사이드바의 "📍 현재 위치 날씨 보기" 버튼 클릭
2. IP 주소 기반으로 자동 위치 감지
3. 감지된 위치의 날씨 정보 표시

### 도시 검색
1. 사이드바의 검색창에 도시명 입력
   - 한글: 서울, 강남구, 부산, 제주 등
   - 영문: Seoul, Tokyo, London, New York 등
2. "🔍 검색" 버튼 클릭
3. 날씨 정보 및 지도 표시

### 주간 예보 보기
- 메인 화면 하단의 "📅 주간 날씨 예보" 섹션 확인
- 최대 5일간의 일별 날씨 요약 제공

### 시간대별 예보 보기
- "🕐 시간대별 상세 예보 보기" 확장 메뉴 클릭
- 향후 24시간 3시간 간격 상세 정보 확인

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **API**: 
  - OpenWeather API (날씨 데이터)
  - Kakao Maps API (지도)
  - IP Geolocation APIs (ipapi.co, ip-api.com, ipinfo.io)
- **Language**: Python 3.x

## 📦 의존성

- `streamlit>=1.28.0` - 웹 프레임워크
- `requests>=2.31.0` - HTTP 요청
- `python-dotenv>=1.0.0` - 환경 변수 관리

## 🔒 보안

- ⚠️ **중요**: `.env` 파일은 Git에 커밋하지 마세요
- `.gitignore`에 `.env` 파일이 포함되어 있습니다
- API 키는 절대 공개 저장소에 업로드하지 마세요
- `.env.example` 파일을 참고하여 다른 사용자가 설정할 수 있도록 합니다

## 🌏 지원 지역

### 한국 (구 단위까지 검색 가능)
- 서울: 강남구, 송파구, 강서구, 마포구 등 25개 구
- 부산: 해운대구, 부산진구 등
- 경기: 수원, 성남, 분당구, 일산, 용인 등
- 기타: 대전, 대구, 인천, 광주, 울산, 세종 등

### 전세계
- 모든 주요 도시 검색 가능 (영문명 사용)

## 📝 라이선스

이 프로젝트는 개인 학습 및 포트폴리오 목적으로 제작되었습니다.

## 🙋‍♂️ 문제 해결

### 지도가 표시되지 않는 경우
1. Kakao Developers 콘솔에서 도메인 허용 확인
2. 브라우저 콘솔(F12)에서 에러 메시지 확인
3. 네트워크 방화벽 설정 확인

### API 키 오류
1. `.env` 파일이 올바른 위치에 있는지 확인
2. API 키가 정확히 입력되었는지 확인
3. OpenWeather API 키가 활성화되었는지 확인 (발급 후 몇 시간 소요될 수 있음)

### 현재 위치 감지 실패
1. 네트워크 연결 확인
2. VPN 또는 프록시 사용 시 비활성화 시도
3. 방화벽이 IP 위치 서비스를 차단하는지 확인

## 📧 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
