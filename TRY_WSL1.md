# WSL1으로 시도하기

## WSL1 vs WSL2

- **WSL1**: Windows 네트워크 직접 사용 → 드론 접근 가능
- **WSL2**: 가상 네트워크 사용 → 드론 접근 불가

## 🔄 WSL2 → WSL1 변환

### 1단계: 현재 WSL 버전 확인

```powershell
# PowerShell에서
wsl -l -v
```

출력 예시:
```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
```

### 2단계: WSL1으로 변환

```powershell
# PowerShell (관리자 권한)
wsl --set-version Ubuntu-22.04 1
```

변환 시간: 약 5~10분

### 3단계: 확인

```powershell
wsl -l -v
```

VERSION이 1로 변경되었는지 확인

### 4단계: WSL 재시작

```powershell
wsl --shutdown
wsl
```

---

## 🧪 테스트

### 1. 드론 WiFi 연결 (Windows)

```powershell
# WiFi 설정에서 ANAFI-A127483 연결
ping 192.168.42.1
```

### 2. WSL1에서 드론 접근 테스트

```bash
# WSL Ubuntu에서
ping 192.168.42.1
```

**성공하면 계속 진행!**

### 3. Olympe 설치

```bash
cd /mnt/c/Users/beaco/git/Embedded_PJ/backend
source venv/bin/activate
pip install parrot-olympe
```

### 4. 서버 실행

```bash
python server.py
```

### 5. 브라우저 테스트

```
http://localhost:3000
```

---

## ⚠️ WSL1 단점

- 성능이 WSL2보다 낮음
- 일부 Linux 기능 제한
- Docker Desktop과 호환성 문제

하지만 **드론 제어에는 충분합니다!**

---

## 🔙 WSL1 → WSL2 되돌리기

나중에 다시 WSL2로 돌아가려면:

```powershell
wsl --set-version Ubuntu-22.04 2
```

---

## 💡 결론

WSL1으로 변환하면 **드론 제어가 작동할 가능성이 높습니다!**

시도해보세요:

```powershell
# PowerShell (관리자)
wsl --set-version Ubuntu-22.04 1
wsl --shutdown
wsl
```

그리고 다시 서버를 실행하세요!
