# 🚀 5th Hint AI - vLLM 기반 코딩 힌트 시스템# 🚀 5th Hint AI - vLLM 기반 코딩 힌트 시스템# 🚀 백준 문제 힌트 생성 시스템



AI 기반 적응형 코딩 힌트 생성 시스템 (vLLM + Gradio + GitHub Actions)



## 🎯 프로젝트 개요AI 기반 적응형 코딩 힌트 생성 시스템 (vLLM + Docker)vLLM Docker 기반 AI 코딩 힌트 제공 시스템



백준 알고리즘 문제를 푸는 학습자에게 **교육학적으로 설계된 적응형 힌트**를 제공하는 AI 시스템입니다.



### 핵심 기능## 🎯 프로젝트 개요## ✨ 주요 특징



- 🧠 **적응형 힌트 생성**: 사용자 코드 분석 기반 맞춤형 힌트

- ⚡ **초고속 추론**: vLLM 엔진으로 15-24배 빠른 응답

- 🎓 **교육학적 설계**: 난이도별 점진적 힌트 제공백준 알고리즘 문제를 푸는 학습자에게 **교육학적으로 설계된 적응형 힌트**를 제공하는 AI 시스템입니다.- � **Docker 기반 배포**: vLLM 공식 이미지 활용

- 🛡️ **보안 가드**: 정답 코드 노출 방지

- ☁️ **클라우드 자동 빌드**: GitHub Actions로 자동 배포- ⚡ **고속 추론**: vLLM의 PagedAttention (15-20x faster)



## 🏗️ 시스템 아키텍처### 핵심 기능- 🎨 **Gradio UI**: 직관적인 웹 인터페이스



### 배포 워크플로우- 🌐 **RunPod 최적화**: 클라우드 GPU 환경 완벽 지원

```

GitHub Push → GitHub Actions → DockerHub → RunPod- 🧠 **적응형 힌트 생성**: 사용자 코드 분석 기반 맞춤형 힌트- 🤖 **소크라테스 학습법**: 단계적 힌트 제공

     ↓              ↓                ↓           ↓

   코드 수정    자동 빌드       이미지 저장   즉시 배포- ⚡ **초고속 추론**: vLLM 엔진으로 15-24배 빠른 응답

```

- 🎓 **교육학적 설계**: 난이도별 점진적 힌트 제공## �📁 프로젝트 구조

### 통합 Docker 이미지 구조

```- 🛡️ **보안 가드**: 정답 코드 노출 방지

┌────────────────────────────────┐

│  vLLM + Gradio 통합 컨테이너   │- 🐳 **Docker 기반**: 간편한 배포 및 확장성```

│                                │

│  ┌──────────────┐             │5th-project_mvp/

│  │ vLLM Server  │ :8000       │

│  │ (백그라운드)  │             │## 🏗️ 시스템 아키텍처├── README.md                    # 프로젝트 전체 가이드

│  └──────────────┘             │

│         ↕                     │├── .gitignore                   # Git 제외 파일

│  ┌──────────────┐             │

│  │  Gradio UI   │ :7860       │```├── cleanup_project.bat/.sh      # 프로젝트 정리 스크립트

│  │ (포그라운드)  │             │

│  └──────────────┘             │┌─────────────────┐│

└────────────────────────────────┘

```│   사용자 (웹)   │├── crawler/                     # 백준 문제 크롤러



## 🚀 빠른 시작└────────┬────────┘│   ├── README.md



### RunPod에서 즉시 사용 ⭐         │ HTTP│   ├── crawlers/



**가장 간단한 방법!** 이미 빌드된 이미지를 사용합니다.         ▼│   │   ├── baekjoon_hybrid_crawler.py



1. **RunPod 웹사이트** 접속: https://www.runpod.io┌─────────────────┐│   │   ├── crawl_all_hybrid.py

2. **Deploy** → **Custom Image**

3. **Container Image**: │   Gradio UI     │ (포트 7860)│   │   ├── test_solved_ac_api.py

   ```

   inucreativehrd21/hint-ai-vllm:latest│   - 문제 선택   ││   │   └── requirements.txt

   ```

4. **GPU**: RTX 4090 또는 RTX 5090│   - 코드 입력   ││   └── data/raw/                # 크롤링 결과 저장

5. **Container Disk**: 50GB 이상

6. **Expose Ports**: `8000, 7860`│   - 힌트 표시   ││

7. **Deploy** 클릭!

└────────┬────────┘├── hint-system/                 # 🎯 메인 힌트 생성 시스템

8. **5-10분 대기** (모델 다운로드)

         │ REST API│   ├── app.py                   # Gradio 메인 앱

9. **접속**:

   - Gradio UI: `https://xxxxx-7860.proxy.runpod.net`         ▼│   ├── config.py                # 환경 설정

   - vLLM API: `https://xxxxx-8000.proxy.runpod.net`

┌─────────────────┐│   ├── docker-compose.yml       # Docker Compose 설정

### 개발자용: 코드 수정 및 자동 배포

│  vLLM Server    │ (포트 8000)│   ├── Dockerfile               # Gradio 앱 Dockerfile

```bash

# 1. 레포 클론│  - Qwen2.5-Coder││   ├── .env.example             # 환경 변수 예시

git clone https://github.com/inucreativehrd21/5th_hint_AI.git

cd 5th_hint_AI│  - GPU 가속     ││   ├── requirements-app.txt     # 경량 의존성



# 2. 코드 수정│  - OpenAI 호환  ││   ├── requirements.txt         # 전체 의존성

vim hint-system/app.py

└─────────────────┘│   │

# 3. Git 푸시 (자동 빌드 시작!)

git add .```│   ├── models/                  # 모델 추론 로직

git commit -m "Update hint system"

git push origin main│   │   ├── __init__.py



# GitHub Actions가 자동으로:## 🚀 빠른 시작 (RunPod)│   │   ├── model_inference.py   # VLLMInference 클래스

# - Docker 이미지 빌드

# - DockerHub에 푸시│   │   └── model_config.py      # 모델 설정

# - 완료! (5-15분 소요)

```### 1. RunPod Pod 생성│   │



📖 **상세 가이드**: [`GITHUB_ACTIONS_GUIDE.md`](GITHUB_ACTIONS_GUIDE.md)│   ├── data/                    # 문제 데이터



---- **템플릿**: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`│   │   └── problems_multi_solution.json



## 📂 프로젝트 구조- **GPU**: RTX 4090 / RTX 5090 권장│   │



```- **디스크**: 50GB+│   ├── evaluation/              # 평가 결과

5th_hint_AI/

├── .github/- **포트**: 7860, 8000│   │   └── results/

│   └── workflows/

│       └── docker-publish.yml    # GitHub Actions 워크플로우│   │

│

├── hint-system/                    # 힌트 시스템 (메인)### 2. 원클릭 실행│   ├── quick_start.sh           # 자동 배포 스크립트

│   ├── Dockerfile.unified          # vLLM + Gradio 통합 이미지

│   ├── app.py                      # Gradio UI 앱│   ├── verify_system.sh         # 시스템 검증

│   ├── config.py                   # 설정 파일

│   ├── models/                     # AI 모델 모듈```bash│   ├── test_system_validation.py

│   │   ├── model_inference.py      # vLLM 추론

│   │   ├── code_analyzer.py        # 코드 분석cd /workspace│   │

│   │   ├── adaptive_prompt.py      # 프롬프트 생성

│   │   ├── hint_validator.py       # 힌트 검증git clone https://github.com/inucreativehrd21/5th_hint_AI.git│   └── 📚 문서

│   │   └── security_guard.py       # 보안 가드

│   ├── data/                       # 문제 데이터cd 5th_hint_AI/hint-system│       ├── README_DOCKER.md              # Docker 사용 가이드 ⭐

│   │   └── problems_multi_solution.json

│   ├── requirements.txt            # Python 패키지bash runpod_docker_simple.sh│       ├── RUNPOD_DEPLOYMENT_GUIDE.md    # RunPod 배포 가이드 ⭐

│   └── README.md                   # hint-system 문서

│```│       └── REFACTORING_SUMMARY.md        # 리팩토링 요약

├── crawler/                        # 백준 크롤러

│   └── crawlers/│

│       ├── baekjoon_hybrid_crawler.py

│       └── crawl_all_hybrid.py### 3. 접속└── docs/                        # 개발 문서

│

├── GITHUB_ACTIONS_GUIDE.md         # 클라우드 빌드 가이드    ├── MIGRATION_SUMMARY.md

└── README.md                       # 이 파일

```- **Gradio UI**: http://localhost:7860    ├── PROMPT_IMPROVEMENT_LOG.md



---- **vLLM API**: http://localhost:8000/v1    └── PROMPT_FIX_*.md



## 🛠️ 기술 스택```



### AI/MLRunPod 대시보드에서 포트 노출 후 외부 접속 가능!

- **vLLM 0.6.3**: 초고속 LLM 추론 엔진

- **Qwen2.5-Coder-7B**: 코딩 특화 언어 모델## 🚀 빠른 시작

- **Transformers 4.45+**: HuggingFace 모델 로딩

## 📂 프로젝트 구조

### Backend

- **FastAPI**: vLLM OpenAI 호환 API### 🐳 Docker 기반 배포 (권장)

- **Gradio 4.44**: 웹 UI 프레임워크

```

### DevOps

- **Docker**: 컨테이너화5th_hint_AI/가장 간단하고 안정적인 방법입니다.

- **GitHub Actions**: CI/CD 자동화

- **DockerHub**: 이미지 저장소├── hint-system/                    # 힌트 시스템 (메인)

- **RunPod**: GPU 클라우드 플랫폼

│   ├── app.py                      # Gradio UI 앱```bash

---

│   ├── config.py                   # 설정 파일# 1. 프로젝트 클론

## 🎓 힌트 시스템 특징

│   ├── models/                     # AI 모델 모듈git clone https://github.com/<your-username>/5th_project_mvp.git

### 3단계 난이도 시스템

│   │   ├── model_inference.py      # vLLM 추론cd 5th_project_mvp/hint-system

1. **🔰 초급 (Novice)**

   - 구체적인 힌트와 함수명 제공│   │   ├── code_analyzer.py        # 코드 분석

   - 코드 예시 포함

   - 처음 시작하거나 막막할 때│   │   ├── adaptive_prompt.py      # 프롬프트 생성# 2. 환경 변수 설정



2. **📚 중급 (Intermediate)**│   │   ├── hint_validator.py       # 힌트 검증cp .env.example .env

   - 추상적 힌트와 개념 설명

   - 방향성 제시│   │   └── security_guard.py       # 보안 가드# 필요시 .env 파일 편집

   - 어느 정도 진행했지만 막힌 부분이 있을 때

│   ├── data/                       # 문제 데이터

3. **🎓 고급 (Advanced)**

   - 소크라테스식 질문│   │   └── problems_multi_solution.json# 3. 자동 배포 (딸깍!)

   - 사고 유도

   - 거의 완성했거나 스스로 해결하고 싶을 때│   ├── docker-compose.runpod.yml   # Docker Compose 설정chmod +x quick_start.sh



### 4가지 지표 진단│   ├── Dockerfile.gradio           # Gradio UI 이미지./quick_start.sh



- **코드 유사도**: AST 기반 구조 분석│   ├── runpod_docker_simple.sh     # 실행 스크립트

- **문법 오류**: Python 구문 검증

- **논리 오류**: 알고리즘 로직 분석│   ├── requirements.txt            # Python 패키지# 4. 접속

- **개념 이해도**: 필요한 개념 체크

│   └── README.md                   # 문서# http://localhost:7860

### Chain-of-Hints

│```

- 이전 힌트 히스토리 저장

- 동일 난이도 3회 요청 시 자동 상승├── crawler/                        # 백준 크롤러

- 학습 진행도 추적

│   └── crawlers/**상세 가이드**: [hint-system/README_DOCKER.md](hint-system/README_DOCKER.md)

---

│       ├── baekjoon_hybrid_crawler.py

## 📊 성능

│       └── crawl_all_hybrid.py### 🌩️ RunPod 클라우드 배포

### 추론 속도

- **vLLM**: 평균 0.5-1.5초│

- **기존 Transformers**: 평균 8-15초

- **속도 향상**: **15-24배**└── README.md                       # 프로젝트 전체 문서GPU가 필요한 경우 RunPod에서 배포하세요.



### 리소스 요구사항```

- **GPU 메모리**: 8-10GB (RTX 4090/5090)

- **CPU 메모리**: 8GB+**추천 설정**:

- **디스크**: 30GB+ (모델 + 데이터)

## 🛠️ 기술 스택- **GPU**: RTX 4090 (24GB) - ~$0.44/시간 ⭐⭐⭐⭐⭐

---

- **템플릿**: RunPod PyTorch 2.1

## 🔧 환경 설정

### AI/ML- **디스크**: Container 50GB, Volume 100GB

### 환경 변수 (.env)

- **vLLM**: 초고속 LLM 추론 엔진

```bash

# vLLM 서버 설정- **Qwen2.5-Coder-7B**: 코딩 특화 언어 모델```bash

VLLM_API_BASE=http://127.0.0.1:8000/v1

VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct- **Transformers**: HuggingFace 모델 로딩# RunPod 인스턴스 SSH 접속 후



# HuggingFace 토큰 (선택)cd /workspace

HF_TOKEN=your_token_here

### Backendgit clone <repository-url>

# 캐시 디렉토리

HF_HOME=/root/.cache/huggingface- **FastAPI**: vLLM OpenAI 호환 APIcd 5th_project_mvp/hint-system



# Gradio 설정- **Gradio**: 웹 UI 프레임워크

GRADIO_SERVER_NAME=0.0.0.0

GRADIO_SERVER_PORT=7860# 자동 배포

```

### DevOps./quick_start.sh

---

- **Docker**: 컨테이너화

## 🧪 사용 예시

- **Docker Compose**: 멀티 컨테이너 관리# 포트 7860을 RunPod에서 노출

### 1. Gradio UI에서 사용

- **RunPod**: GPU 클라우드 플랫폼# Console → Connect → HTTP Service → 7860

1. 문제 선택 (예: #1000 - A+B)

2. 코드 작성```

3. 난이도 선택 (초급/중급/고급)

4. "힌트 받기" 클릭## 📊 성능

5. AI가 코드 분석 후 맞춤형 힌트 제공

**상세 가이드**: [hint-system/RUNPOD_DEPLOYMENT_GUIDE.md](hint-system/RUNPOD_DEPLOYMENT_GUIDE.md)

### 2. vLLM API 직접 호출

### 추론 속도

```bash

curl -X POST http://localhost:8000/v1/completions \- **vLLM**: 평균 0.5-1.5초### 💻 로컬 개발 모드

  -H "Content-Type: application/json" \

  -d '{- **기존 Transformers**: 평균 8-15초

    "model": "Qwen/Qwen2.5-Coder-7B-Instruct",

    "prompt": "Python으로 두 수의 합을 구하는 힌트를 주세요.",- **속도 향상**: 15-24배Docker 없이 로컬에서 개발하려면:

    "max_tokens": 200,

    "temperature": 0.7

  }'

```### 리소스```bash



---- **GPU 메모리**: 8-10GB (RTX 4090/5090)cd hint-system



## 🐛 문제 해결- **CPU 메모리**: 8GB+



### GitHub Actions 빌드 실패- **디스크**: 30GB+ (모델 + 데이터)# 가상환경 생성 및 활성화



```bashpython -m venv venv

# Actions 로그 확인

GitHub → Actions → 실패한 워크플로우 클릭## 🎓 교육학적 설계source venv/bin/activate  # Linux/Mac



# Secrets 확인# 또는

Settings → Secrets → DOCKERHUB_USERNAME, DOCKERHUB_TOKEN

```### 힌트 난이도 시스템venv\Scripts\activate  # Windows



### RunPod에서 이미지를 찾을 수 없음



```bash1. **레벨 1 (추상적)**: 문제 접근 방향성# 의존성 설치

# DockerHub 레포지토리 공개 설정 확인

DockerHub → 레포지토리 → Settings → Visibility → Public2. **레벨 2 (개념적)**: 필요한 알고리즘 개념pip install -r requirements-app.txt



# 이미지 이름 정확히 입력3. **레벨 3 (구체적)**: 구현 방법 제시

inucreativehrd21/hint-ai-vllm:latest

```4. **레벨 4 (상세)**: 코드 구조 가이드# vLLM 서버만 Docker로 실행



### vLLM 서버가 시작되지 않음5. **레벨 5 (디버깅)**: 오류 분석 및 수정docker-compose up -d vllm-server



```bash

# Pod 로그 확인

RunPod Dashboard → Logs### 보안 가드# Gradio 앱 로컬 실행



# GPU 메모리 사용률 조정python app.py --vllm-url http://localhost:8000/v1

환경변수: VLLM_GPU_MEMORY_UTILIZATION=0.75

```- ✅ 정답 코드 직접 제공 차단```



---- ✅ 함수/변수명 그대로 노출 방지## 📊 크롤러 (선택사항)



## 📚 추가 문서- ✅ 단계별 학습 유도



- **[GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)**: 클라우드 자동 빌드 완벽 가이드백준에서 문제 데이터를 직접 수집하려면:

- **[hint-system/README.md](hint-system/README.md)**: 힌트 시스템 상세 문서

## 📖 상세 가이드

---

```bash

## 🤝 기여

### Docker 사용법cd crawler/crawlers

이 프로젝트는 교육 목적으로 개발되었습니다.



### 개발 팀

- 크롤링: 백준 문제 데이터 수집전체 가이드: [`hint-system/RUNPOD_DOCKER_GUIDE.md`](hint-system/RUNPOD_DOCKER_GUIDE.md)# 의존성 설치

- AI 모델: Qwen2.5-Coder 활용

- 시스템: vLLM + Docker + GitHub Actions 아키텍처pip install -r requirements.txt



---### 주요 명령어



## 📄 라이선스# 크롤링 실행



MIT License```bashpython crawl_all_hybrid.py



---# 서비스 시작```



## 🙏 감사의 말docker-compose -f docker-compose.runpod.yml up -d



- **vLLM 팀**: 초고속 추론 엔진**크롤러 기능:**

- **Qwen 팀**: 우수한 코딩 모델

- **백준**: 알고리즘 문제 플랫폼# 로그 확인- 백준 단계별 문제 목록 수집 (1~68단계)

- **GitHub**: Actions 무료 제공

- **멘토님**: Docker + 클라우드 아키텍처 조언docker-compose -f docker-compose.runpod.yml logs -f- 문제 상세 정보: 제목, 설명, 입출력 예제



---- solved.ac API 통합: 난이도, 태그



## 📞 문의# 서비스 중지- JSON 저장: `crawler/data/raw/`



- GitHub Issues: [5th_hint_AI/issues](https://github.com/inucreativehrd21/5th_hint_AI/issues)docker-compose -f docker-compose.runpod.yml down



---**참고**: 이미 준비된 데이터가 `hint-system/data/problems_multi_solution.json`에 있으므로 필수는 아닙니다.



**🚀 지금 바로 시작하세요!**# 서비스 재시작



```bashdocker-compose -f docker-compose.runpod.yml restart## 📚 주요 기능

# RunPod에서 즉시 사용

Container Image: inucreativehrd21/hint-ai-vllm:latest```



# 또는 개발하기### 1. AI 힌트 생성

git clone https://github.com/inucreativehrd21/5th_hint_AI.git

cd 5th_hint_AI## 🔧 환경 설정- **소크라테스 학습법**: 답을 주지 않고 질문으로 유도

# 코드 수정 후 push하면 자동 빌드!

```- **코드 분석**: 완료/누락 부분 자동 파악



**로컬 PC 용량 걱정 없이 GitHub Actions가 클라우드에서 자동으로 빌드합니다!** ☁️### .env 파일- **다음 단계 제시**: 점진적 힌트 제공




```bash### 2. 다중 모델 지원

# vLLM 서버 설정- **Qwen2.5-Coder-7B**: 코드 생성 특화 (권장)

VLLM_API_BASE=http://vllm-server:8000/v1- **DeepSeek-Coder**: 코드 이해 특화

VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct- **CodeLlama**: Meta 공식 모델



# HuggingFace 토큰 (선택)### 3. 실시간 추론

HF_TOKEN=your_token_here- **vLLM 엔진**: 15-20x 빠른 추론

- **GPU 최적화**: PagedAttention, Continuous Batching

# 캐시 디렉토리- **낮은 지연시간**: 1-2초 내 응답

HF_HOME=/workspace/.cache/huggingface

```## �️ 기술 스택



## 🧪 테스트### 인프라

- **Docker**: 컨테이너화

### Health Check- **Docker Compose**: 멀티 컨테이너 오케스트레이션

- **vLLM**: 고속 LLM 추론 엔진

```bash

# vLLM 서버### 백엔드

curl http://localhost:8000/health- **Python 3.10+**

- **OpenAI API (vLLM)**: API 호환 인터페이스

# 모델 정보- **requests**: HTTP 클라이언트

curl http://localhost:8000/v1/models

```### 프론트엔드

- **Gradio 4.44**: 웹 UI 프레임워크

### API 테스트

### 크롤러

```bash- **BeautifulSoup4**: HTML 파싱

curl -X POST http://localhost:8000/v1/completions \- **solved.ac API**: 문제 메타데이터

  -H "Content-Type: application/json" \

  -d '{## 📖 문서

    "model": "Qwen/Qwen2.5-Coder-7B-Instruct",

    "prompt": "Python으로 피보나치 수열을 구현하는 힌트를 주세요.",### 시작 가이드

    "max_tokens": 200,- 📘 **[Docker 사용 가이드](hint-system/README_DOCKER.md)** - Docker 기반 배포

    "temperature": 0.7- 📗 **[RunPod 배포 가이드](hint-system/RUNPOD_DEPLOYMENT_GUIDE.md)** - 클라우드 GPU 배포

  }'- � **[리팩토링 요약](hint-system/REFACTORING_SUMMARY.md)** - 최신 변경사항

```

### 개발 문서

## 🤝 기여- [프롬프트 개선 로그](docs/PROMPT_IMPROVEMENT_LOG.md)

- [데이터 구조 변경](docs/MIGRATION_SUMMARY.md)

이 프로젝트는 교육 목적으로 개발되었습니다.- [크롤러 README](crawler/README.md)



### 개발 팀## 🎯 프롬프트 엔지니어링



- 크롤링: 백준 문제 데이터 수집### 소크라테스 학습법 적용

- AI 모델: Qwen2.5-Coder 파인튜닝```

- 시스템: vLLM + Docker 아키텍처❌ 나쁜 힌트: "함수를 정의하려면 def 키워드가 필요해"

✅ 좋은 힌트: "이 계산을 100번 써야 한다면 코드를 100번 복사할 건가?"

## 📄 라이선스```



MIT License### 핵심 원칙

1. **답을 직접 주지 않기**

## 🙏 감사의 말2. **질문으로 유도하기**

3. **학생의 코드 구조 분석**

- **vLLM 팀**: 초고속 추론 엔진4. **다음 단계만 제시**

- **Qwen 팀**: 우수한 코딩 모델

- **백준**: 알고리즘 문제 플랫폼## 🔧 시스템 요구사항

- **멘토님**: Docker 아키텍처 조언

### Docker 배포 (권장)

## 📞 문의- **OS**: Linux (Ubuntu 22.04+), Windows 10/11 + WSL2

- **Docker**: 20.10+

- GitHub Issues: [5th_hint_AI/issues](https://github.com/inucreativehrd21/5th_hint_AI/issues)- **Docker Compose**: 2.0+

- **GPU**: NVIDIA GPU + NVIDIA Container Toolkit

---- **VRAM**: 24GB (RTX 3090/4090, A5000 등)

- **메모리**: 32GB RAM 권장

**🚀 지금 바로 시작하세요!**- **디스크**: 50GB



```bash### 로컬 개발

git clone https://github.com/inucreativehrd21/5th_hint_AI.git- **Python**: 3.10+

cd 5th_hint_AI/hint-system- **RAM**: 8GB+ (GPU 미사용 시)

bash runpod_docker_simple.sh- **GPU**: 선택사항 (CPU도 가능, 느림)

```

## � 트러블슈팅

### vLLM 서버 연결 실패
```bash
# 로그 확인
docker-compose logs vllm-server

# 재시작
docker-compose restart vllm-server
```

### GPU 인식 안됨
```bash
# NVIDIA 드라이버 확인
nvidia-smi

# Docker GPU 테스트
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### OOM (Out of Memory)
```bash
# .env 파일 수정
VLLM_GPU_MEMORY_UTILIZATION=0.75  # 0.85 → 0.75
VLLM_MAX_MODEL_LEN=2048            # 4096 → 2048

# 재시작
docker-compose restart vllm-server
```

**더 많은 해결책**: [RUNPOD_DEPLOYMENT_GUIDE.md](hint-system/RUNPOD_DEPLOYMENT_GUIDE.md)

## 📝 데이터 구조

### problems_multi_solution.json

```json
{
  "problem_id": "1000",
  "title": "A+B",
  "level": 1,
  "tags": ["구현", "사칙연산"],
  "description": "두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램...",
  "input_description": "첫째 줄에 A와 B가 주어진다.",
  "output_description": "첫째 줄에 A+B를 출력한다.",
  "examples": [
    {
      "input": "1 2",
      "output": "3"
    }
  ]
}
```

## 🤝 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📄 라이선스

MIT License

## 🙏 감사의 말

- [vLLM](https://github.com/vllm-project/vllm) - 고속 LLM 추론
- [Gradio](https://www.gradio.app/) - 웹 UI
- [Qwen](https://github.com/QwenLM/Qwen) - 코드 생성 모델
- [백준 온라인 저지](https://www.acmicpc.net/)
- [solved.ac](https://solved.ac/)
- 코멘트 작성
- 결과 저장 (`evaluation/results/`)

## 🚨 주의사항

1. **함수명/변수명 언급 방지**
   - snake_case 패턴 자동 필터링
   - 일반 함수(input, print)는 허용

2. **모델 크기**
   - 소형 모델(1.5B)은 불안정할 수 있음
   - Temperature 낮춰서 사용 권장

3. **메모리 관리**
   - 여러 모델 동시 로드 시 메모리 부족 가능
   - 필요한 모델만 선택

## 📄 라이선스

Educational use only

## 👥 기여자

Team 5 - PlayData AI 부트캠프

## 📧 문의

- GitHub Issues
- Email: [your-email]

---

**마지막 업데이트:** 2025-01-30
**버전:** 1.0.0
