# Docker를 사용한 설치 가이드

## 1단계: Docker Desktop 설치

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드
2. 설치 및 실행
3. WSL2 백엔드 활성화 (설치 중 자동으로 설정됨)
4. **Docker Desktop이 완전히 시작될 때까지 대기** (트레이 아이콘 확인)

## 2단계: Docker Desktop 실행 확인

```bash
# PowerShell에서 Docker 상태 확인
docker --version
docker ps

# Docker Desktop이 실행 중이어야 합니다
```

만약 에러가 발생하면:
- Docker Desktop 앱을 수동으로 실행
- 시스템 트레이에서 Docker 아이콘이 초록색인지 확인
- "Docker Desktop is running" 메시지 확인

## 3단계: Docker 이미지 빌드

```bash
# backend 디렉토리에서
cd backend

# Docker 이미지 빌드
docker-compose build
```

## 3단계: 컨테이너 실행

```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

서버가 http://localhost:5000 에서 실행됩니다.

## 4단계: 프론트엔드 실행

```bash
# 프로젝트 루트에서
npm run dev
```

## 드론 연결

1. Windows에서 드론 WiFi (ANAFI-XXXXXX) 연결
2. Docker 컨테이너가 host 네트워크를 사용하므로 자동으로 드론 접근 가능

## 유용한 명령어

```bash
# 컨테이너 중지
docker-compose down

# 컨테이너 재시작
docker-compose restart

# 컨테이너 로그 확인
docker-compose logs -f

# 컨테이너 내부 접속
docker-compose exec drone-backend bash
```

## 문제 해결

### 포트 충돌
```bash
# 다른 프로세스가 5000 포트 사용 중인 경우
# docker-compose.yml에서 포트 변경
ports:
  - "5001:5000"
```

### 네트워크 연결 문제
```bash
# Docker Desktop 재시작
# 또는 WSL2 재시작
wsl --shutdown
```
