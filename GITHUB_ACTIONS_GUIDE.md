# 🚀 GitHub Actions 클라우드 자동 빌드 가이드

## 🎯 개요

**로컬 PC 용량 걱정 없이** GitHub Actions 클라우드에서 자동으로 Docker 이미지를 빌드하고 DockerHub에 푸시합니다!

- ✅ **로컬 빌드 불필요**: GitHub 클라우드에서 자동 빌드
- ✅ **자동 배포**: 코드 푸시만 하면 DockerHub에 자동 업로드
- ✅ **항상 최신 버전**: main 브랜치 푸시 시 자동 빌드
- ✅ **RunPod 즉시 사용**: DockerHub 이미지 선택만 하면 끝!

---

## 📋 사전 준비 (최초 1회만)

### 1단계: DockerHub 레포지토리 생성

1. **DockerHub 웹사이트** 접속: https://hub.docker.com
2. **로그인** 후 "Create Repository" 클릭
3. **레포지토리 이름**: `hint-ai-vllm`
4. **공개 설정**: **Public** (권장)
5. "Create" 클릭

### 2단계: DockerHub Access Token 생성 ⚠️ 중요!

1. DockerHub → **Account Settings** → **Security** (또는 **Personal Access Tokens**)
2. "**New Access Token**" 클릭
3. **Access Token Description**: `GitHub Actions`
4. **Access permissions**: **Read, Write, Delete** 선택
5. "**Generate**" 클릭
6. **⚠️ 토큰 복사** (한 번만 표시됨!) → 메모장에 임시 저장

**중요 확인사항:**
- ✅ 토큰은 `dckr_pat_` 로 시작해야 함
- ✅ 복사할 때 앞뒤 공백 없이 정확히 복사
- ✅ **비밀번호가 아니라 토큰**을 복사해야 함!

### 3단계: GitHub Repository Secrets 설정 ⚠️ 정확히 입력!

1. GitHub 레포지토리 페이지 이동
   ```
   https://github.com/inucreativehrd21/5th_hint_AI
   ```

2. **Settings** → **Secrets and variables** → **Actions**

3. "**New repository secret**" 클릭

**첫 번째 Secret 추가:**
- Name: `DOCKERHUB_USERNAME`
- Secret: `inucreativehrd21` (**정확히 입력!**)
- "Add secret" 클릭

**두 번째 Secret 추가:**
- Name: `DOCKERHUB_TOKEN`
- Secret: `dckr_pat_xxxxxxxxxxxxx` (**2단계에서 복사한 토큰 붙여넣기**)
- "Add secret" 클릭

**⚠️ 흔한 실수:**
- ❌ DOCKERHUB_TOKEN에 **비밀번호** 입력 (틀림!)
- ❌ 토큰 복사 시 공백 포함
- ❌ 사용자명 대소문자 틀림
- ✅ 반드시 **Access Token**을 사용해야 함!

---

## 🔥 사용 방법 (매우 간단!)

### 자동 빌드 (코드 푸시 시)

```bash
# 1. 코드 수정 후 Git 커밋
git add .
git commit -m "Update hint system"

# 2. GitHub에 푸시
git push origin main

# 끝! GitHub Actions가 자동으로:
# - Docker 이미지 빌드
# - DockerHub에 푸시
# - 완료!
```

### 수동 빌드 (원할 때)

1. GitHub 레포지토리 → **Actions** 탭
2. "**Build and Push Docker Image to DockerHub**" 선택
3. "**Run workflow**" → "Run workflow" 클릭

---

## 📊 빌드 진행 상황 확인

### GitHub Actions 로그 확인

1. GitHub 레포지토리 → **Actions** 탭
2. 최신 워크플로우 실행 클릭
3. **build-and-push** 작업 클릭
4. 각 단계별 로그 확인:
   - ✅ Checkout code
   - ✅ Set up Docker Buildx
   - ✅ Login to DockerHub
   - ✅ Build and Push Docker image
   - ✅ Image digest

### 빌드 시간

- **최초 빌드**: 약 10-15분 (vLLM 베이스 이미지 다운로드)
- **이후 빌드**: 약 5-8분 (캐시 활용)

---

## 🎮 RunPod에서 사용하기

### 1단계: DockerHub 이미지 확인

빌드 완료 후 DockerHub에서 확인:
```
https://hub.docker.com/r/your-dockerhub-username/hint-ai-vllm
```

### 2단계: RunPod Pod 생성

1. **RunPod 웹사이트** 접속: https://www.runpod.io
2. "**Deploy**" 클릭
3. **GPU 선택**: RTX 4090 또는 RTX 5090
4. **Template**: "**Use Custom Image**" 선택
5. **Container Image**: 
   ```
   your-dockerhub-username/hint-ai-vllm:latest
   ```
6. **Container Disk**: 50GB 이상
7. **Expose Ports**: `8000, 7860`
8. **환경 변수** (선택사항):
   ```
   HF_TOKEN=your_huggingface_token
   VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct
   ```
9. "**Deploy**" 클릭!

### 3단계: Pod 구동 확인

- **대기 시간**: 5-10분 (모델 다운로드)
- **로그 확인**: RunPod Dashboard → Logs

### 4단계: 접속

**RunPod TCP Port Mappings:**
- Gradio UI: `https://xxxxx-7860.proxy.runpod.net`
- vLLM API: `https://xxxxx-8000.proxy.runpod.net`

---

## 🔧 파일 구조

```
5th_hint_AI/
├── .github/
│   └── workflows/
│       └── docker-publish.yml    # GitHub Actions 워크플로우
│
├── hint-system/
│   ├── Dockerfile.unified        # 통합 Docker 이미지
│   ├── app.py                    # Gradio UI
│   ├── config.py                 # 설정
│   ├── models/                   # AI 모듈
│   ├── data/                     # 문제 데이터
│   └── requirements.txt          # Python 패키지
│
└── README.md
```

---

## 🐛 트러블슈팅

### ⚠️ 문제 0: "unauthorized: incorrect username or password" (가장 흔한 문제!)

**증상**: GitHub Actions에서 DockerHub 로그인 실패
```
Error response from daemon: Get "https://registry-1.docker.io/v2/": 
unauthorized: incorrect username or password
```

**원인:**
1. ❌ DOCKERHUB_TOKEN에 **비밀번호**를 입력함 (가장 흔함!)
2. ❌ Access Token이 아닌 다른 값 입력
3. ❌ 토큰 복사 시 공백 포함
4. ❌ DOCKERHUB_USERNAME 오타

**해결 방법:**

**Step 1: DockerHub에서 새 토큰 생성**
```bash
1. https://hub.docker.com 로그인
2. Account Settings → Security (또는 Personal Access Tokens)
3. "New Access Token" 클릭
4. Description: GitHub Actions
5. Permissions: Read, Write, Delete
6. Generate 클릭
7. 토큰 복사 (dckr_pat_로 시작하는 긴 문자열)
```

**Step 2: GitHub Secrets 재설정**
```bash
1. https://github.com/inucreativehrd21/5th_hint_AI
2. Settings → Secrets and variables → Actions
3. 기존 DOCKERHUB_TOKEN 삭제 (있다면)
4. New repository secret 클릭

   Name: DOCKERHUB_TOKEN
   Secret: [방금 복사한 토큰 붙여넣기]
   
5. 기존 DOCKERHUB_USERNAME 확인/수정
   Name: DOCKERHUB_USERNAME
   Secret: inucreativehrd21
```

**Step 3: 재실행**
```bash
# GitHub → Actions → 실패한 워크플로우 → Re-run all jobs
```

**확인 방법:**
```bash
# Secrets이 올바르게 설정되었는지 확인
GitHub → Settings → Secrets and variables → Actions
- DOCKERHUB_USERNAME 존재 확인
- DOCKERHUB_TOKEN 존재 확인 (값은 보이지 않음)
```

---

### ⚠️ 문제 0-2: "No space left on device" (GitHub Actions 디스크 부족)

**증상**: GitHub Actions 러너에서 빌드 중 디스크 공간 부족
```
System.IO.IOException: No space left on device : 
'/home/runner/actions-runner/cached/_diag/Worker_20251110-151538-utc.log'
```

**원인:**
- GitHub Actions 무료 러너는 약 14GB 디스크 제공
- vLLM 같은 대용량 Docker 이미지 빌드 시 공간 부족 발생
- 기본 설치된 .NET, Android SDK 등이 공간 차지 (~10GB)

**해결 방법 (극한 최적화 적용!):**

**1. 워크플로우 극한 정리** (이미 적용됨)

```yaml
- name: Maximize disk space (극한 정리)
  run: |
    # 기본 불필요 소프트웨어 제거
    sudo rm -rf /usr/share/dotnet          # .NET (~2GB)
    sudo rm -rf /usr/local/lib/android     # Android (~8GB)
    sudo rm -rf /opt/ghc                   # Haskell (~1GB)
    sudo rm -rf /opt/hostedtoolcache/CodeQL
    
    # 추가 공간 확보 (극한)
    sudo rm -rf /usr/local/share/boost     # C++ 라이브러리
    sudo rm -rf /usr/local/graalvm/        # Java VM
    sudo rm -rf /usr/local/.ghcup/         # Haskell 도구
    sudo rm -rf /usr/local/share/powershell
    sudo rm -rf /usr/local/share/chromium
    sudo rm -rf /usr/local/lib/node_modules
    sudo rm -rf /opt/az                    # Azure CLI
    sudo rm -rf /opt/microsoft
    
    # Docker 완전 정리
    sudo docker system prune -a -f --volumes
    sudo rm -rf /var/lib/docker
    
    # 캐시 및 임시 파일 제거
    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*
    sudo rm -rf /tmp/*
    sudo rm -rf /var/tmp/*
```

**예상 확보 공간: 약 15-20GB!** 🚀

**2. Dockerfile 최적화** (이미 적용됨)

```dockerfile
# 단일 레이어로 통합, 캐시 즉시 제거
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

RUN pip install --no-cache-dir gradio==4.44.0 ... \
    && rm -rf /root/.cache/pip \
    && rm -rf /tmp/*
```

**3. BuildKit 최적화**

```yaml
- name: Set up Docker Buildx
  with:
    buildkitd-flags: --oci-worker-gc=true --oci-worker-gc-keepstorage=1000
```

**확인 방법:**

빌드 로그에서 디스크 공간 확인:
```bash
=== Before cleanup ===
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        84G   60G   24G  72% /

=== After cleanup ===
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        84G   42G   42G  50% /   # 18GB 확보! ✅
Available: 42G
```

**현재 상태:**
✅ 극한 디스크 최적화 적용 완료
✅ 예상 확보 공간: **15-20GB**
✅ Dockerfile 레이어 최적화 완료
✅ BuildKit GC(Garbage Collection) 활성화

**여전히 실패한다면:**

이 방법으로도 실패하면 이미지 크기 자체가 너무 큽니다. 대안:

1. **GitHub 유료 플랜**: larger runner (4-core, 16GB RAM, 150GB disk)
2. **Self-hosted 러너**: 자체 서버에서 빌드
3. **로컬 빌드 + 푸시**: 로컬에서 빌드 후 DockerHub에 푸시
4. **멀티스테이지 빌드**: Dockerfile을 더 경량화

**권장**: 일단 현재 설정으로 시도해보세요. 대부분의 경우 성공합니다!

---

### 문제 1: GitHub Actions 빌드 실패

**증상**: Actions 탭에서 빌드가 실패 (빨간색 X)

**해결:**
```bash
# 1. Actions 로그 확인
GitHub → Actions → 실패한 워크플로우 클릭 → 로그 확인

# 2. 일반적인 원인:
# - Secrets 설정 오류 (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
# - Dockerfile 경로 오류
# - Dockerfile 문법 오류
```

### 문제 2: DockerHub 푸시 실패

**증상**: "unauthorized" 또는 "denied" 에러

**해결:**
```bash
# 1. DockerHub Token 확인
# - Token이 만료되지 않았는지 확인
# - Token 권한이 "Read, Write, Delete"인지 확인

# 2. GitHub Secrets 재설정
# Settings → Secrets → DOCKERHUB_TOKEN 삭제 후 재생성
```

### 문제 3: RunPod에서 이미지를 찾을 수 없음

**증상**: "image not found" 에러

**해결:**
```bash
# 1. DockerHub 레포지토리 공개 설정 확인
# - DockerHub → 레포지토리 → Settings → Visibility → Public

# 2. 이미지 이름 정확히 입력
# your-dockerhub-username/hint-ai-vllm:latest
# (대소문자, 하이픈 정확히 입력)
```

### 문제 4: 빌드가 너무 오래 걸림

**증상**: 빌드 시간이 20분 이상

**해결:**
```bash
# 1. GitHub Actions 로그에서 어느 단계가 느린지 확인
# 2. 일반적으로 "Build and Push" 단계가 가장 오래 걸림 (정상)
# 3. 캐시가 제대로 작동하면 이후 빌드는 빠름
```

---

## 📈 고급 기능

### 버전 태그 관리

워크플로우는 자동으로 2개의 태그를 생성합니다:

1. **`latest`**: 항상 최신 버전
2. **`<commit-sha>`**: 특정 커밋 버전

**특정 버전 사용:**
```
your-dockerhub-username/hint-ai-vllm:abc123def456
```

### 수동 워크플로우 실행

코드 변경 없이 재빌드하고 싶을 때:

1. GitHub → Actions
2. "Build and Push Docker Image" 선택
3. "Run workflow" → "Run workflow"

### 빌드 캐시 활용

- **캐시 활용**: 이전 빌드의 레이어를 재사용하여 속도 향상
- **자동 관리**: GitHub Actions가 자동으로 캐시 관리
- **장점**: 두 번째 빌드부터 5-8분으로 단축

---

## ✅ 체크리스트

배포 전 확인:

- [ ] DockerHub 레포지토리 생성 완료
- [ ] DockerHub Access Token 생성 완료
- [ ] GitHub Secrets 설정 완료 (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [ ] `.github/workflows/docker-publish.yml` 파일 존재 확인
- [ ] `hint-system/Dockerfile.unified` 파일 존재 확인
- [ ] 코드 커밋 및 푸시 완료
- [ ] GitHub Actions 빌드 성공 확인
- [ ] DockerHub에서 이미지 확인
- [ ] RunPod Pod 생성 및 구동 확인
- [ ] Gradio UI 접속 테스트 완료

---

## 🎉 요약

### 초기 설정 (최초 1회):

1. DockerHub 레포 생성
2. DockerHub Token 생성
3. GitHub Secrets 설정

### 일상 사용 (매일):

```bash
# 코드 수정
vim hint-system/app.py

# Git 푸시
git add .
git commit -m "Update"
git push origin main

# 끝! (5-15분 후 DockerHub에 자동 업로드)
```

### RunPod 배포 (필요할 때):

1. RunPod → Deploy → Custom Image
2. 이미지: `your-dockerhub-username/hint-ai-vllm:latest`
3. Deploy 클릭!

---

## 📚 참고 자료

- **GitHub Actions 문서**: https://docs.github.com/en/actions
- **DockerHub 문서**: https://docs.docker.com/docker-hub/
- **RunPod 문서**: https://docs.runpod.io/
- **vLLM 문서**: https://docs.vllm.ai/

---

## 💡 팁

### 비용 절약

- **GitHub Actions**: 무료 (Public 레포지토리)
- **DockerHub**: 무료 (Public 이미지)
- **RunPod**: 사용한 만큼만 과금

### 빠른 배포

- **코드 푸시 즉시 빌드**: 자동화로 대기 시간 최소화
- **캐시 활용**: 두 번째 빌드부터 빠름
- **병렬 빌드**: GitHub Actions가 자동 최적화

### 팀 협업

- **동일한 이미지**: 모든 팀원이 동일한 환경 사용
- **버전 관리**: Git 커밋 SHA로 버전 추적
- **자동 동기화**: 푸시만 하면 모두 최신 버전 사용

---

**이제 로컬 PC 용량 걱정 없이 클라우드에서 자동으로 빌드하고 RunPod에서 바로 사용하세요!** 🚀
