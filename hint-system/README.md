# 🚀 vLLM + Gradio 통합 힌트 시스템

**단일 Docker 이미지**로 vLLM 서버와 Gradio UI를 함께 실행하는 AI 기반 코딩 힌트 생성 시스템

---

## ✨ 주요 특징

- 🐳 **단일 Docker 이미지**: vLLM + Gradio가 하나의 컨테이너에서 동작
- ⚡ **초고속 추론**: vLLM 엔진으로 15-24배 빠른 응답  
- 🎯 **RunPod 최적화**: 템플릿 선택만으로 "딸깍" 배포
- 🎓 **교육학적 설계**: 난이도별 맞춤형 힌트 제공
- 🛡️ **보안 가드**: 정답 코드 노출 방지

---

## 🚀 빠른 시작 (3가지 방법)

### 방법 1: Docker Hub 이미지 사용 (RunPod 추천) ⭐

**가장 간단한 방법!** 이미 빌드된 이미지를 사용합니다.

1. **RunPod Pod 생성**
   - Deploy → **Custom Image**
   - Container Image: `your-dockerhub-username/hint-ai-vllm:latest`
   - GPU: RTX 4090/5090
   - Expose Ports: `8000, 7860`
   - Deploy 클릭!

2. **5-10분 대기** (모델 다운로드)

3. **접속**
   - Gradio UI: `https://xxxxx-7860.proxy.runpod.net`
   - vLLM API: `https://xxxxx-8000.proxy.runpod.net`

📖 **상세 가이드**: [`RUNPOD_UNIFIED_DEPLOY.md`](RUNPOD_UNIFIED_DEPLOY.md)

---

### 방법 2: Docker Compose 사용 (로컬/서버)

vLLM과 Gradio를 별도 컨테이너로 실행합니다.

```bash
cd /workspace
git clone https://github.com/inucreativehrd21/5th_hint_AI.git
cd 5th_hint_AI/hint-system
bash runpod_docker_simple.sh
```

📖 **상세 가이드**: [`RUNPOD_DOCKER_GUIDE.md`](RUNPOD_DOCKER_GUIDE.md)

---

### 방법 3: 커스텀 이미지 빌드

자신만의 Docker 이미지를 빌드하고 싶다면:

```bash
# 1. 이미지 빌드 및 푸시
bash build_and_push.sh

# 2. Docker Hub 사용자명 입력
> your-dockerhub-username

# 3. RunPod에서 사용
# Container Image: your-dockerhub-username/hint-ai-vllm:latest
```

---

## 📂 프로젝트 구조

```
hint-system/
├── app.py                        # Gradio UI 메인 앱
├── config.py                     # 설정 파일
├── models/                       # AI 모델 모듈
│   ├── model_inference.py        # vLLM 추론
│   ├── code_analyzer.py          # 코드 분석
│   ├── adaptive_prompt.py        # 프롬프트 생성
│   ├── hint_validator.py         # 힌트 검증
│   └── security_guard.py         # 보안 가드
├── data/                         # 문제 데이터
│   └── problems_multi_solution.json
│
├── Dockerfile.unified            # 통합 Docker 이미지
├── Dockerfile.gradio             # Gradio만 (Compose용)
├── docker-compose.runpod.yml     # Docker Compose 설정
│
├── build_and_push.sh             # 이미지 빌드 스크립트
├── runpod_docker_simple.sh       # Docker Compose 실행
│
├── RUNPOD_UNIFIED_DEPLOY.md      # 통합 이미지 배포 가이드
├── RUNPOD_DOCKER_GUIDE.md        # Docker Compose 가이드
└── README.md                     # 이 파일
```

---

## 🛠️ 기술 스택

### AI/ML
- **vLLM 0.6.3**: 초고속 LLM 추론 엔진
- **Qwen2.5-Coder-7B**: 코딩 특화 언어 모델
- **Transformers 4.45+**: HuggingFace 모델 로딩

### Backend
- **FastAPI**: vLLM OpenAI 호환 API
- **Gradio 4.44**: 웹 UI 프레임워크

### DevOps
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 관리
- **RunPod**: GPU 클라우드 플랫폼

---

## 🎓 힌트 시스템 특징

### 3단계 난이도 시스템

1. **🔰 초급 (Novice)**
   - 구체적인 힌트와 함수명 제공
   - 코드 예시 포함
   - 처음 시작하거나 막막할 때

2. **📚 중급 (Intermediate)**
   - 추상적 힌트와 개념 설명
   - 방향성 제시
   - 어느 정도 진행했지만 막힌 부분이 있을 때

3. **🎓 고급 (Advanced)**
   - 소크라테스식 질문
   - 사고 유도
   - 거의 완성했거나 스스로 해결하고 싶을 때

### 4가지 지표 진단

- **코드 유사도**: AST 기반 구조 분석
- **문법 오류**: Python 구문 검증
- **논리 오류**: 알고리즘 로직 분석
- **개념 이해도**: 필요한 개념 체크

### Chain-of-Hints

- 이전 힌트 히스토리 저장
- 동일 난이도 3회 요청 시 자동 상승
- 학습 진행도 추적

---

## 🧪 사용 예시

### 1. Gradio UI에서 사용

1. 문제 선택 (예: #1000 - A+B)
2. 코드 작성
3. 난이도 선택 (초급/중급/고급)
4. "힌트 받기" 클릭
5. AI가 코드 분석 후 맞춤형 힌트 제공

### 2. vLLM API 직접 호출

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "prompt": "Python으로 두 수의 합을 구하는 힌트를 주세요.",
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

---

## 📊 성능

### 추론 속도
- **vLLM**: 평균 0.5-1.5초
- **기존 Transformers**: 평균 8-15초
- **속도 향상**: **15-24배**

### 리소스 요구사항
- **GPU 메모리**: 8-10GB (RTX 4090/5090)
- **CPU 메모리**: 8GB+
- **디스크**: 30GB+ (모델 + 데이터)

---

## 🔧 환경 설정

### 환경 변수 (.env)

```bash
# vLLM 서버 설정
VLLM_API_BASE=http://127.0.0.1:8000/v1
VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct

# HuggingFace 토큰 (선택)
HF_TOKEN=your_token_here

# 캐시 디렉토리
HF_HOME=/root/.cache/huggingface

# Gradio 설정
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
```

---

## 🐛 문제 해결

### vLLM 서버가 시작되지 않음

```bash
# 로그 확인
docker logs <container_id>

# GPU 메모리 사용률 조정
VLLM_GPU_MEMORY_UTILIZATION=0.75

# 또는 더 작은 모델 사용
VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-1.5B-Instruct
```

### Gradio UI 접속 안 됨

```bash
# 포트 확인
netstat -tlnp | grep 7860

# 방화벽 확인
sudo ufw allow 7860

# RunPod: TCP Port Mappings 확인
```

### 모델 다운로드 느림

```bash
# HuggingFace 토큰 설정
export HF_TOKEN=your_token_here

# 또는 미리 다운로드된 모델 사용
# Volume 마운트: -v /path/to/models:/root/.cache/huggingface
```

---

## 📚 추가 문서

- **[RUNPOD_UNIFIED_DEPLOY.md](RUNPOD_UNIFIED_DEPLOY.md)**: 통합 이미지 배포 완벽 가이드
- **[RUNPOD_DOCKER_GUIDE.md](RUNPOD_DOCKER_GUIDE.md)**: Docker Compose 사용 가이드
- **[상위 README](../README.md)**: 프로젝트 전체 개요

---

## 🤝 기여

이 프로젝트는 교육 목적으로 개발되었습니다.

### 개발 팀
- 크롤링: 백준 문제 데이터 수집
- AI 모델: Qwen2.5-Coder 활용
- 시스템: vLLM + Docker 아키텍처

---

## 📄 라이선스

MIT License

---

## 🙏 감사의 말

- **vLLM 팀**: 초고속 추론 엔진
- **Qwen 팀**: 우수한 코딩 모델
- **백준**: 알고리즘 문제 플랫폼
- **멘토님**: Docker 아키텍처 조언

---

## 📞 문의

- GitHub Issues: [5th_hint_AI/issues](https://github.com/inucreativehrd21/5th_hint_AI/issues)

---

**🚀 지금 바로 시작하세요!**

```bash
# Docker Hub 이미지 사용 (RunPod)
Container Image: your-dockerhub-username/hint-ai-vllm:latest

# 또는 Git 클론 후 실행
git clone https://github.com/inucreativehrd21/5th_hint_AI.git
cd 5th_hint_AI/hint-system
bash runpod_docker_simple.sh
```
