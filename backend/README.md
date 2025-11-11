# 드론 제어 백엔드 서버

Parrot Anafi 드론을 제어하기 위한 Python Flask 서버

## 설치

```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 실행

```bash
python server.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 드론 연결
- `POST /api/drone/connect` - 드론 연결
- `POST /api/drone/disconnect` - 드론 연결 해제
- `GET /api/drone/status` - 드론 상태 조회

### 드론 제어
- `POST /api/drone/takeoff` - 이륙
- `POST /api/drone/land` - 착륙
- `POST /api/drone/move` - 지정 위치로 이동
- `POST /api/drone/mission` - 미션 시작

## 드론 연결 방법

1. Parrot Anafi 드론 전원 ON
2. WiFi에서 ANAFI-XXXXXX 네트워크 연결
3. 서버 실행
4. 프론트엔드에서 연결 버튼 클릭
