# Windows 빠른 시작 가이드

## 🚀 5분 안에 시작하기 (WSL2 사용)

### 1단계: WSL2 설치 (처음 한 번만)

**PowerShell 관리자 권한으로 실행:**

```powershell
wsl --install
```

컴퓨터 재시작 → Ubuntu 설정 완료

---

### 2단계: WSL Ubuntu에서 백엔드 실행

**Ubuntu 터미널 열기:**

```bash
# 프로젝트로 이동
cd /mnt/c/Users/beaco/git/Embedded_PJ/backend

# 시스템 패키지 설치 (처음 한 번만)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Python 가상환경 생성 (처음 한 번만)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치 (처음 한 번만)
pip install --upgrade pip
pip install -r requirements.txt

# 서버 실행
python server.py
```

✅ 백엔드 서버 실행 중: http://localhost:5000

---

### 3단계: Windows에서 프론트엔드 실행

**새 PowerShell 창 열기:**

```powershell
# 프로젝트로 이동
cd C:\Users\beaco\git\Embedded_PJ

# 의존성 설치 (처음 한 번만)
npm install

# 개발 서버 실행
npm run dev
```

✅ 프론트엔드 실행 중: http://localhost:3000

---

### 4단계: 드론 연결

1. **Parrot Anafi 드론 전원 켜기**
2. **Windows WiFi 설정에서 "ANAFI-XXXXXX" 연결**
3. **브라우저에서 http://localhost:3000 접속**
4. **"드론 연결" 버튼 클릭**

---

## 🔄 다음번 실행할 때

### 터미널 1 (WSL Ubuntu):
```bash
cd /mnt/c/Users/beaco/git/Embedded_PJ/backend
source venv/bin/activate
python server.py
```

### 터미널 2 (Windows PowerShell):
```powershell
cd C:\Users\beaco\git\Embedded_PJ
npm run dev
```

---

## ⚠️ 문제 해결

### "pip install 실패"
```bash
# WSL에서
sudo apt install -y python3-dev build-essential
pip install --upgrade pip
pip install -r requirements.txt
```

### "포트 5000 이미 사용 중"
```bash
# Windows PowerShell에서
netstat -ano | findstr :5000
# PID 확인 후
taskkill /PID [PID번호] /F
```

### "WSL 네트워크 연결 안됨"
```powershell
# Windows PowerShell (관리자)
wsl --shutdown
# WSL 재시작
```

---

## 📚 더 자세한 가이드

- WSL2 상세 가이드: `backend/INSTALL_WSL.md`
- Docker 가이드: `backend/INSTALL_DOCKER.md`
- 전체 설정 가이드: `SETUP.md`
