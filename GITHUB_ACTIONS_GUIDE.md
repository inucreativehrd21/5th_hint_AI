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

### 2단계: DockerHub Access Token 생성

1. DockerHub → **Account Settings** → **Security**
2. "**New Access Token**" 클릭
3. **Access Token Description**: `GitHub Actions`
4. **Access permissions**: **Read, Write, Delete** 선택
5. "**Generate**" 클릭
6. **토큰 복사** (한 번만 표시됨!) → 안전한 곳에 저장

### 3단계: GitHub Repository Secrets 설정

1. GitHub 레포지토리 페이지 이동
2. **Settings** → **Secrets and variables** → **Actions**
3. "**New repository secret**" 클릭

**첫 번째 Secret 추가:**
- Name: `DOCKERHUB_USERNAME`
- Secret: `your-dockerhub-username` (DockerHub 사용자명)
- "Add secret" 클릭

**두 번째 Secret 추가:**
- Name: `DOCKERHUB_TOKEN`
- Secret: `위에서 복사한 Access Token`
- "Add secret" 클릭

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
