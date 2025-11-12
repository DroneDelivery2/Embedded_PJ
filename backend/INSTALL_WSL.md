# Windows에서 Parrot Olympe SDK 설치 가이드 (WSL2)

## ⚠️ 중요
Parrot Olympe SDK는 Windows에서 직접 설치할 수 없습니다.
WSL2 (Windows Subsystem for Linux)를 사용해야 합니다.

## 1단계: WSL2 설치

### PowerShell을 관리자 권한으로 실행:

1. 시작 메뉴에서 "PowerShell" 검색
2. 우클릭 → "관리자 권한으로 실행"
3. 다음 명령어 실행:

```powershell
# WSL 설치
wsl --install

# 설치 완료 후 컴퓨터 재시작
```

### 재시작 후:
- Ubuntu 터미널이 자동으로 열립니다
- 사용자 이름과 비밀번호 설정
- 설정 완료까지 대기

## 2단계: Ubuntu 설정

```bash
# Ubuntu 터미널에서
sudo apt update
sudo apt upgrade -y

# Python 및 필수 패키지 설치
sudo apt install -y python3 python3-pip python3-dev python3-venv
sudo apt install -y build-essential git
```

## 3단계: 프로젝트 접근

WSL에서 Windows 파일에 접근할 수 있습니다:

```bash
# 현재 프로젝트 경로 예시:
# C:\Users\beaco\git\Embedded_PJ

# WSL에서 접근:
cd /mnt/c/Users/beaco/git/Embedded_PJ/backend

# 또는 프로젝트를 WSL로 복사 (선택사항):
# cp -r /mnt/c/Users/beaco/git/Embedded_PJ ~/drone-delivery
# cd ~/drone-delivery/backend
```

**팁**: Windows 경로를 WSL 경로로 변환
- `C:\` → `/mnt/c/`
- `\` → `/`

## 4단계: Python 가상환경 생성

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

## 5단계: Olympe SDK 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

## 6단계: 서버 실행

```bash
# WSL Ubuntu에서
python server.py
```

서버가 http://localhost:5000 에서 실행됩니다.
**Windows 브라우저에서 접속 가능합니다!**

## 7단계: 프론트엔드 실행 (Windows에서)

**새 PowerShell 또는 CMD 창을 열고:**

```powershell
# 프로젝트 루트 디렉토리에서
cd C:\Users\beaco\git\Embedded_PJ

# 프론트엔드 실행
npm run dev
```

이제 http://localhost:3000 에서 앱에 접속할 수 있습니다!

## 드론 WiFi 연결

WSL2에서도 Windows의 WiFi를 공유하므로:
1. Windows에서 드론 WiFi (ANAFI-XXXXXX) 연결
2. WSL2에서 자동으로 같은 네트워크 사용
3. 드론 IP: 192.168.42.1

## 문제 해결

### WSL2에서 네트워크 연결 안됨
```bash
# Windows PowerShell (관리자)
wsl --shutdown
# WSL 재시작
```

### 포트 접근 문제
```bash
# Windows 방화벽에서 포트 5000 허용
```

### Olympe 설치 오류
```bash
# 추가 의존성 설치
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
```
