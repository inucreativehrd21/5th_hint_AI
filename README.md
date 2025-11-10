# 🚀 5th Hint AI - vLLM 기반 코딩 힌트 시스템# 🚀 백준 문제 힌트 생성 시스템



AI 기반 적응형 코딩 힌트 생성 시스템 (vLLM + Docker)vLLM Docker 기반 AI 코딩 힌트 제공 시스템



## 🎯 프로젝트 개요## ✨ 주요 특징



백준 알고리즘 문제를 푸는 학습자에게 **교육학적으로 설계된 적응형 힌트**를 제공하는 AI 시스템입니다.- � **Docker 기반 배포**: vLLM 공식 이미지 활용

- ⚡ **고속 추론**: vLLM의 PagedAttention (15-20x faster)

### 핵심 기능- 🎨 **Gradio UI**: 직관적인 웹 인터페이스

- 🌐 **RunPod 최적화**: 클라우드 GPU 환경 완벽 지원

- 🧠 **적응형 힌트 생성**: 사용자 코드 분석 기반 맞춤형 힌트- 🤖 **소크라테스 학습법**: 단계적 힌트 제공

- ⚡ **초고속 추론**: vLLM 엔진으로 15-24배 빠른 응답

- 🎓 **교육학적 설계**: 난이도별 점진적 힌트 제공## �📁 프로젝트 구조

- 🛡️ **보안 가드**: 정답 코드 노출 방지

- 🐳 **Docker 기반**: 간편한 배포 및 확장성```

5th-project_mvp/

## 🏗️ 시스템 아키텍처├── README.md                    # 프로젝트 전체 가이드

├── .gitignore                   # Git 제외 파일

```├── cleanup_project.bat/.sh      # 프로젝트 정리 스크립트

┌─────────────────┐│

│   사용자 (웹)   │├── crawler/                     # 백준 문제 크롤러

└────────┬────────┘│   ├── README.md

         │ HTTP│   ├── crawlers/

         ▼│   │   ├── baekjoon_hybrid_crawler.py

┌─────────────────┐│   │   ├── crawl_all_hybrid.py

│   Gradio UI     │ (포트 7860)│   │   ├── test_solved_ac_api.py

│   - 문제 선택   ││   │   └── requirements.txt

│   - 코드 입력   ││   └── data/raw/                # 크롤링 결과 저장

│   - 힌트 표시   ││

└────────┬────────┘├── hint-system/                 # 🎯 메인 힌트 생성 시스템

         │ REST API│   ├── app.py                   # Gradio 메인 앱

         ▼│   ├── config.py                # 환경 설정

┌─────────────────┐│   ├── docker-compose.yml       # Docker Compose 설정

│  vLLM Server    │ (포트 8000)│   ├── Dockerfile               # Gradio 앱 Dockerfile

│  - Qwen2.5-Coder││   ├── .env.example             # 환경 변수 예시

│  - GPU 가속     ││   ├── requirements-app.txt     # 경량 의존성

│  - OpenAI 호환  ││   ├── requirements.txt         # 전체 의존성

└─────────────────┘│   │

```│   ├── models/                  # 모델 추론 로직

│   │   ├── __init__.py

## 🚀 빠른 시작 (RunPod)│   │   ├── model_inference.py   # VLLMInference 클래스

│   │   └── model_config.py      # 모델 설정

### 1. RunPod Pod 생성│   │

│   ├── data/                    # 문제 데이터

- **템플릿**: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`│   │   └── problems_multi_solution.json

- **GPU**: RTX 4090 / RTX 5090 권장│   │

- **디스크**: 50GB+│   ├── evaluation/              # 평가 결과

- **포트**: 7860, 8000│   │   └── results/

│   │

### 2. 원클릭 실행│   ├── quick_start.sh           # 자동 배포 스크립트

│   ├── verify_system.sh         # 시스템 검증

```bash│   ├── test_system_validation.py

cd /workspace│   │

git clone https://github.com/inucreativehrd21/5th_hint_AI.git│   └── 📚 문서

cd 5th_hint_AI/hint-system│       ├── README_DOCKER.md              # Docker 사용 가이드 ⭐

bash runpod_docker_simple.sh│       ├── RUNPOD_DEPLOYMENT_GUIDE.md    # RunPod 배포 가이드 ⭐

```│       └── REFACTORING_SUMMARY.md        # 리팩토링 요약

│

### 3. 접속└── docs/                        # 개발 문서

    ├── MIGRATION_SUMMARY.md

- **Gradio UI**: http://localhost:7860    ├── PROMPT_IMPROVEMENT_LOG.md

- **vLLM API**: http://localhost:8000/v1    └── PROMPT_FIX_*.md

```

RunPod 대시보드에서 포트 노출 후 외부 접속 가능!

## 🚀 빠른 시작

## 📂 프로젝트 구조

### 🐳 Docker 기반 배포 (권장)

```

5th_hint_AI/가장 간단하고 안정적인 방법입니다.

├── hint-system/                    # 힌트 시스템 (메인)

│   ├── app.py                      # Gradio UI 앱```bash

│   ├── config.py                   # 설정 파일# 1. 프로젝트 클론

│   ├── models/                     # AI 모델 모듈git clone https://github.com/<your-username>/5th_project_mvp.git

│   │   ├── model_inference.py      # vLLM 추론cd 5th_project_mvp/hint-system

│   │   ├── code_analyzer.py        # 코드 분석

│   │   ├── adaptive_prompt.py      # 프롬프트 생성# 2. 환경 변수 설정

│   │   ├── hint_validator.py       # 힌트 검증cp .env.example .env

│   │   └── security_guard.py       # 보안 가드# 필요시 .env 파일 편집

│   ├── data/                       # 문제 데이터

│   │   └── problems_multi_solution.json# 3. 자동 배포 (딸깍!)

│   ├── docker-compose.runpod.yml   # Docker Compose 설정chmod +x quick_start.sh

│   ├── Dockerfile.gradio           # Gradio UI 이미지./quick_start.sh

│   ├── runpod_docker_simple.sh     # 실행 스크립트

│   ├── requirements.txt            # Python 패키지# 4. 접속

│   └── README.md                   # 문서# http://localhost:7860

│```

├── crawler/                        # 백준 크롤러

│   └── crawlers/**상세 가이드**: [hint-system/README_DOCKER.md](hint-system/README_DOCKER.md)

│       ├── baekjoon_hybrid_crawler.py

│       └── crawl_all_hybrid.py### 🌩️ RunPod 클라우드 배포

│

└── README.md                       # 프로젝트 전체 문서GPU가 필요한 경우 RunPod에서 배포하세요.

```

**추천 설정**:

## 🛠️ 기술 스택- **GPU**: RTX 4090 (24GB) - ~$0.44/시간 ⭐⭐⭐⭐⭐

- **템플릿**: RunPod PyTorch 2.1

### AI/ML- **디스크**: Container 50GB, Volume 100GB

- **vLLM**: 초고속 LLM 추론 엔진

- **Qwen2.5-Coder-7B**: 코딩 특화 언어 모델```bash

- **Transformers**: HuggingFace 모델 로딩# RunPod 인스턴스 SSH 접속 후

cd /workspace

### Backendgit clone <repository-url>

- **FastAPI**: vLLM OpenAI 호환 APIcd 5th_project_mvp/hint-system

- **Gradio**: 웹 UI 프레임워크

# 자동 배포

### DevOps./quick_start.sh

- **Docker**: 컨테이너화

- **Docker Compose**: 멀티 컨테이너 관리# 포트 7860을 RunPod에서 노출

- **RunPod**: GPU 클라우드 플랫폼# Console → Connect → HTTP Service → 7860

```

## 📊 성능

**상세 가이드**: [hint-system/RUNPOD_DEPLOYMENT_GUIDE.md](hint-system/RUNPOD_DEPLOYMENT_GUIDE.md)

### 추론 속도

- **vLLM**: 평균 0.5-1.5초### 💻 로컬 개발 모드

- **기존 Transformers**: 평균 8-15초

- **속도 향상**: 15-24배Docker 없이 로컬에서 개발하려면:



### 리소스```bash

- **GPU 메모리**: 8-10GB (RTX 4090/5090)cd hint-system

- **CPU 메모리**: 8GB+

- **디스크**: 30GB+ (모델 + 데이터)# 가상환경 생성 및 활성화

python -m venv venv

## 🎓 교육학적 설계source venv/bin/activate  # Linux/Mac

# 또는

### 힌트 난이도 시스템venv\Scripts\activate  # Windows



1. **레벨 1 (추상적)**: 문제 접근 방향성# 의존성 설치

2. **레벨 2 (개념적)**: 필요한 알고리즘 개념pip install -r requirements-app.txt

3. **레벨 3 (구체적)**: 구현 방법 제시

4. **레벨 4 (상세)**: 코드 구조 가이드# vLLM 서버만 Docker로 실행

5. **레벨 5 (디버깅)**: 오류 분석 및 수정docker-compose up -d vllm-server



### 보안 가드# Gradio 앱 로컬 실행

python app.py --vllm-url http://localhost:8000/v1

- ✅ 정답 코드 직접 제공 차단```

- ✅ 함수/변수명 그대로 노출 방지## 📊 크롤러 (선택사항)

- ✅ 단계별 학습 유도

백준에서 문제 데이터를 직접 수집하려면:

## 📖 상세 가이드

```bash

### Docker 사용법cd crawler/crawlers



전체 가이드: [`hint-system/RUNPOD_DOCKER_GUIDE.md`](hint-system/RUNPOD_DOCKER_GUIDE.md)# 의존성 설치

pip install -r requirements.txt

### 주요 명령어

# 크롤링 실행

```bashpython crawl_all_hybrid.py

# 서비스 시작```

docker-compose -f docker-compose.runpod.yml up -d

**크롤러 기능:**

# 로그 확인- 백준 단계별 문제 목록 수집 (1~68단계)

docker-compose -f docker-compose.runpod.yml logs -f- 문제 상세 정보: 제목, 설명, 입출력 예제

- solved.ac API 통합: 난이도, 태그

# 서비스 중지- JSON 저장: `crawler/data/raw/`

docker-compose -f docker-compose.runpod.yml down

**참고**: 이미 준비된 데이터가 `hint-system/data/problems_multi_solution.json`에 있으므로 필수는 아닙니다.

# 서비스 재시작

docker-compose -f docker-compose.runpod.yml restart## 📚 주요 기능

```

### 1. AI 힌트 생성

## 🔧 환경 설정- **소크라테스 학습법**: 답을 주지 않고 질문으로 유도

- **코드 분석**: 완료/누락 부분 자동 파악

### .env 파일- **다음 단계 제시**: 점진적 힌트 제공



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
