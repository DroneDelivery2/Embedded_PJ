# 드론 연결 문제 해결 가이드

## 현재 문제: 연결 타임아웃

```
ERROR: '192.168.42.1 connection timed out
WARNING: Time synchronization failed
Link quality: tx=0, rx=-1, rx_useful=-1
```

## 원인

WSL2는 가상 네트워크를 사용하므로 드론 WiFi에 직접 접근하기 어려울 수 있습니다.

## 해결 방법

### 방법 1: WSL2 네트워크 모드 변경 (권장)

WSL2를 미러 네트워크 모드로 변경하면 Windows 네트워크를 직접 사용할 수 있습니다.

#### 1단계: .wslconfig 파일 생성

Windows에서 `C:\Users\beaco\.wslconfig` 파일 생성:

```ini
[wsl2]
networkingMode=mirrored
```

#### 2단계: WSL 재시작

PowerShell (관리자 권한):
```powershell
wsl --shutdown
```

그 후 WSL Ubuntu 재시작

#### 3단계: 연결 테스트

WSL Ubuntu에서:
```bash
# 드론 IP로 ping 테스트
ping 192.168.42.1

# 성공하면 서버 재시작
cd /mnt/c/Users/beaco/git/Embedded_PJ/backend
source venv/bin/activate
python server.py
```

---

### 방법 2: Docker 사용 (대안)

Docker는 host 네트워크 모드를 지원하므로 더 안정적일 수 있습니다.

#### 1단계: Docker Desktop 설치 및 실행

[Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드

#### 2단계: 컨테이너 실행

```bash
cd C:\Users\beaco\git\Embedded_PJ\backend
docker-compose up --build
```

---

### 방법 3: Windows에서 직접 실행 (Python 스크립트)

Olympe SDK 대신 간단한 HTTP 프록시를 사용하는 방법입니다.

#### 드론 REST API 직접 사용

Parrot Anafi는 REST API도 제공합니다:

```python
# Windows에서 직접 실행 가능
import requests

# 드론 상태 조회
response = requests.get('http://192.168.42.1/api/v1/status')
print(response.json())
```

---

## 연결 확인 체크리스트

### ✅ 1. Windows에서 드론 WiFi 연결 확인

```powershell
# PowerShell에서
ping 192.168.42.1
```

성공 예시:
```
Reply from 192.168.42.1: bytes=32 time=5ms TTL=64
```

### ✅ 2. WSL에서 드론 접근 확인

```bash
# WSL Ubuntu에서
ping 192.168.42.1
```

**실패하면**: WSL 네트워크 설정 문제 → 방법 1 적용

### ✅ 3. 방화벽 확인

Windows 방화벽이 WSL 트래픽을 차단할 수 있습니다.

```powershell
# PowerShell (관리자)
New-NetFirewallRule -DisplayName "WSL" -Direction Inbound -Action Allow
```

### ✅ 4. 드론 상태 확인

- 드론 LED가 녹색으로 깜빡이는지 확인
- 드론 배터리가 충분한지 확인 (최소 20%)
- 드론 펌웨어가 최신인지 확인

---

## 추가 디버깅

### 드론 연결 로그 확인

```bash
# WSL에서 상세 로그 활성화
export OLYMPE_LOG_LEVEL=DEBUG
python server.py
```

### 네트워크 인터페이스 확인

```bash
# WSL에서
ip addr show
route -n
```

### 드론 IP 확인

드론 IP가 192.168.42.1이 아닐 수 있습니다:

```bash
# Windows에서 드론 WiFi 연결 후
ipconfig

# 게이트웨이 주소 확인 (보통 드론 IP)
```

---

## 권장 순서

1. **먼저 시도**: 방법 1 (WSL2 미러 네트워크)
2. **안되면**: 방법 2 (Docker)
3. **최후**: Olympe 없이 REST API 직접 사용

---

## 성공 시 로그

정상 연결 시 다음과 같은 로그가 표시됩니다:

```
INFO: Connected to device: ANAFI-A127483
INFO: 드론 연결 성공!
```
