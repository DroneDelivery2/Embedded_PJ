# 드론 배송 시스템 설치 가이드

## 📋 시스템 요구사항

### 하드웨어
- Parrot Anafi 드론
- WiFi 지원 컴퓨터 (드론 WiFi 연결용)
- 최소 4GB RAM

### 소프트웨어
- Node.js 18+ 
- Python 3.8+
- pip (Python 패키지 관리자)

## 🔧 설치 단계

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd drone-delivery-pwa
```

### 2. 프론트엔드 설정

```bash
# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env.local

# .env.local 파일 내용:
# NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 3. 백엔드 설정

```bash
# backend 디렉토리로 이동
cd backend

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4. Parrot Olympe SDK 설치 (중요!)

Olympe SDK는 Linux/Mac에서 가장 잘 작동합니다. Windows 사용자는 WSL2를 사용하세요.

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip

# Olympe 설치
pip install parrot-olympe
```

## 🚀 실행 방법

### 터미널 1: 백엔드 서버

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python server.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### 터미널 2: 프론트엔드 서버

```bash
npm run dev
```

앱이 http://localhost:3000 에서 실행됩니다.

## 🔌 드론 연결

### 1단계: 드론 준비
1. Parrot Anafi 드론 전원 켜기
2. 드론이 부팅될 때까지 대기 (약 30초)
3. 드론 LED가 녹색으로 깜빡이면 준비 완료

### 2단계: WiFi 연결
1. 컴퓨터 WiFi 설정 열기
2. "ANAFI-XXXXXX" 네트워크 찾기
3. 연결 (비밀번호는 드론 매뉴얼 참조)
4. 연결 성공 확인

### 3단계: 앱에서 연결
1. 브라우저에서 http://localhost:3000 접속
2. "드론 연결" 버튼 클릭
3. 연결 성공 시 배터리 상태 표시
4. "상태 확인" 버튼으로 드론 정보 확인

## 📍 GPS 좌표 설정

실제 사용을 위해 GPS 좌표를 수정해야 합니다.

`app/request/page.tsx` 파일에서:

```typescript
const sites: Site[] = [
  { name: 'site 1', lat: 37.5665, lng: 126.9780, alt: 10 },  // 실제 좌표로 변경
  { name: 'site 2', lat: 37.5675, lng: 126.9790, alt: 10 },
  // ... 나머지 좌표
]
```

좌표 확인 방법:
- Google Maps에서 위치 우클릭 → 좌표 복사
- 또는 GPS 앱 사용

## 🧪 테스트

### 1. 서버 헬스 체크

```bash
curl http://localhost:5000/health
# 응답: {"status": "ok"}
```

### 2. 드론 연결 테스트 (드론 WiFi 연결 후)

```bash
curl -X POST http://localhost:5000/api/drone/connect \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.168.42.1"}'
```

### 3. 드론 상태 조회

```bash
curl http://localhost:5000/api/drone/status
```

## ⚠️ 문제 해결

### 드론 연결 실패
- 드론 WiFi 연결 확인
- 드론 IP 주소 확인 (기본값: 192.168.42.1)
- 방화벽 설정 확인
- 백엔드 서버 실행 확인

### Olympe SDK 설치 오류
- Python 버전 확인 (3.8 이상)
- Linux/Mac 환경 권장
- Windows는 WSL2 사용 필수

### CORS 오류
- 백엔드 서버가 실행 중인지 확인
- .env.local의 API URL 확인
- 브라우저 콘솔에서 에러 메시지 확인

### 드론이 명령을 수행하지 않음
- 드론 배터리 확인 (최소 20% 이상)
- GPS 신호 확인 (실외에서 테스트)
- 드론 펌웨어 업데이트 확인

## 🛡️ 안전 수칙

1. **실외에서만 비행** - GPS 신호 필요
2. **충분한 공간 확보** - 최소 10m x 10m
3. **배터리 확인** - 비행 전 충분한 배터리 확인
4. **날씨 확인** - 바람이 강하거나 비가 오면 비행 금지
5. **비행 제한 구역 확인** - 공항, 군사 시설 근처 비행 금지
6. **시야 확보** - 항상 드론을 시야 내에 유지
7. **비상 착륙 준비** - 문제 발생 시 즉시 착륙

## 📞 지원

문제가 발생하면:
1. 백엔드 로그 확인 (`backend/server.py` 실행 터미널)
2. 브라우저 개발자 도구 콘솔 확인
3. 드론 상태 LED 확인
4. Parrot 공식 문서 참조: https://developer.parrot.com/
