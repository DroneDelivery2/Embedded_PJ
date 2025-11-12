# 🚁 Drone Delivery System - Next.js PWA

Parrot Anafi 드론을 이용한 실시간 배송 시스템 (Progressive Web App)

## ⚠️ Windows 사용자 필독!

Olympe SDK는 Linux 전용입니다. Windows에서는 **WSL2 필수**

**→ [WSL2 빠른 시작 가이드](QUICKSTART_WINDOWS.md)**
**→ [WSL2 네트워크 문제 해결](FIX_WSL_NETWORK.md)**

## 🚀 빠른 시작

### 프론트엔드 (Next.js)

```bash
# 1. 의존성 설치
npm install

# 2. 환경 변수 설정
cp .env.example .env.local

# 3. 개발 서버 실행
npm run dev

# 4. 브라우저에서 접속
# http://localhost:3000
```

### 백엔드 (Python Flask + Olympe SDK)

#### Linux/Mac 사용자

```bash
# 1. backend 디렉토리로 이동
cd backend

# 2. Python 가상환경 생성
python3 -m venv venv

# 3. 가상환경 활성화
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 서버 실행
python server.py
```

#### Windows 사용자 (WSL2)

```bash
# WSL Ubuntu에서
cd /mnt/c/Users/[사용자명]/git/Embedded_PJ/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

**상세 가이드**: `backend/INSTALL_WSL.md`

서버는 http://localhost:5000 에서 실행됩니다.

## 📦 기술 스택

### 프론트엔드
- **Next.js 14** - React 프레임워크
- **TypeScript** - 타입 안정성
- **React 18** - UI 라이브러리

### 백엔드
- **Python 3.8+** - 백엔드 언어
- **Flask** - REST API 서버
- **Parrot Olympe SDK** - 드론 제어 SDK

## 📱 주요 기능

- ✅ **실제 드론 연결** - Parrot Anafi WiFi 연결
- ✅ **실시간 상태 모니터링** - 배터리, GPS 위치, 비행 상태
- ✅ **드론 제어** - 이륙, 착륙, 위치 이동
- ✅ **자동 배송 미션** - 웨이포인트 기반 자동 비행
- ✅ **배송 요청 및 경로 설정** - GPS 좌표 기반 경로 설정
- ✅ **모바일 최적화** - PWA 지원
- ✅ **반응형 디자인** - 모든 디바이스 지원

## 🎯 사용 방법

### 1단계: 드론 준비
1. Parrot Anafi 드론 전원 ON
2. 컴퓨터/스마트폰을 드론 WiFi에 연결 (ANAFI-XXXXXX)
3. 드론 IP 확인 (기본값: 192.168.42.1)

### 2단계: 서버 실행
1. 백엔드 서버 실행 (Python Flask)
2. 프론트엔드 서버 실행 (Next.js)

### 3단계: 드론 연결
1. 브라우저에서 http://localhost:3000 접속
2. "드론 연결" 버튼 클릭
3. 연결 성공 확인 (배터리 상태 표시)

### 4단계: 배송 시작
1. "배송 시작" 메뉴 선택
2. 출발지와 도착지 선택
3. "배송 시작" 버튼 클릭
4. 드론이 자동으로 이륙하여 목적지로 이동

## 📂 프로젝트 구조

```
drone-delivery-pwa/
├── app/                    # Next.js 앱 디렉토리
│   ├── layout.tsx          # 루트 레이아웃
│   ├── page.tsx            # 홈 페이지 (드론 연결)
│   ├── globals.css         # 전역 스타일
│   ├── status/             # 배송 현황 페이지
│   │   ├── page.tsx
│   │   └── status.module.css
│   └── request/            # 배송 요청 페이지
│       ├── page.tsx
│       └── request.module.css
├── backend/                # Python 백엔드
│   ├── server.py           # Flask REST API 서버
│   ├── drone_controller.py # 드론 제어 모듈
│   ├── requirements.txt    # Python 의존성
│   └── README.md           # 백엔드 문서
├── lib/
│   └── droneApi.ts         # 드론 API 클라이언트
├── public/
│   └── manifest.json       # PWA 매니페스트
├── .env.local              # 환경 변수
├── package.json
├── next.config.js
└── tsconfig.json
```

## 🔧 개발 명령어

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start

# 린트 검사
npm run lint
```

## 🌐 페이지 구조

- `/` - 홈 (드론 연결 및 상태 확인)
- `/request` - 배송 요청 (출발지/도착지 설정)
- `/status` - 배송 현황 (실시간 위치, 제어)

## 🔌 API 엔드포인트

### 드론 연결
- `POST /api/drone/connect` - 드론 연결
- `POST /api/drone/disconnect` - 드론 연결 해제
- `GET /api/drone/status` - 드론 상태 조회

### 드론 제어
- `POST /api/drone/takeoff` - 이륙
- `POST /api/drone/land` - 착륙
- `POST /api/drone/move` - 지정 위치로 이동
- `POST /api/drone/mission` - 미션 시작 (자동 배송)

## ⚠️ 주의사항

1. **Parrot Olympe SDK 설치 필요** - Linux/Mac 권장 (Windows는 WSL 사용)
2. **드론 WiFi 연결 필수** - 드론과 같은 네트워크에 있어야 함
3. **GPS 좌표 설정** - `app/request/page.tsx`에서 실제 좌표로 변경 필요
4. **안전 거리 유지** - 실제 비행 시 안전에 주의
5. **배터리 확인** - 비행 전 충분한 배터리 확인

## 🛠️ 트러블슈팅

### 드론 연결 실패
- 드론 WiFi 연결 확인
- 드론 IP 주소 확인 (기본값: 192.168.42.1)
- 백엔드 서버 실행 확인

### Olympe SDK 설치 오류
- Python 3.8+ 사용 확인
- Linux/Mac 환경 권장
- Windows는 WSL2 사용

## 📄 라이선스

MIT
