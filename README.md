# 🚀 백준 문제 힌트 생성 시스템

vLLM Docker 기반 AI 코딩 힌트 제공 시스템

## ✨ 주요 특징

- � **Docker 기반 배포**: vLLM 공식 이미지 활용
- ⚡ **고속 추론**: vLLM의 PagedAttention (15-20x faster)
- 🎨 **Gradio UI**: 직관적인 웹 인터페이스
- 🌐 **RunPod 최적화**: 클라우드 GPU 환경 완벽 지원
- 🤖 **소크라테스 학습법**: 단계적 힌트 제공

## �📁 프로젝트 구조

```
5th-project_mvp/
├── README.md                    # 프로젝트 전체 가이드
├── .gitignore                   # Git 제외 파일
├── cleanup_project.bat/.sh      # 프로젝트 정리 스크립트
│
├── crawler/                     # 백준 문제 크롤러
│   ├── README.md
│   ├── crawlers/
│   │   ├── baekjoon_hybrid_crawler.py
│   │   ├── crawl_all_hybrid.py
│   │   ├── test_solved_ac_api.py
│   │   └── requirements.txt
│   └── data/raw/                # 크롤링 결과 저장
│
├── hint-system/                 # 🎯 메인 힌트 생성 시스템
│   ├── app.py                   # Gradio 메인 앱
│   ├── config.py                # 환경 설정
│   ├── docker-compose.yml       # Docker Compose 설정
│   ├── Dockerfile               # Gradio 앱 Dockerfile
│   ├── .env.example             # 환경 변수 예시
│   ├── requirements-app.txt     # 경량 의존성
│   ├── requirements.txt         # 전체 의존성
│   │
│   ├── models/                  # 모델 추론 로직
│   │   ├── __init__.py
│   │   ├── model_inference.py   # VLLMInference 클래스
│   │   └── model_config.py      # 모델 설정
│   │
│   ├── data/                    # 문제 데이터
│   │   └── problems_multi_solution.json
│   │
│   ├── evaluation/              # 평가 결과
│   │   └── results/
│   │
│   ├── quick_start.sh           # 자동 배포 스크립트
│   ├── verify_system.sh         # 시스템 검증
│   ├── test_system_validation.py
│   │
│   └── 📚 문서
│       ├── README_DOCKER.md              # Docker 사용 가이드 ⭐
│       ├── RUNPOD_DEPLOYMENT_GUIDE.md    # RunPod 배포 가이드 ⭐
│       └── REFACTORING_SUMMARY.md        # 리팩토링 요약
│
└── docs/                        # 개발 문서
    ├── MIGRATION_SUMMARY.md
    ├── PROMPT_IMPROVEMENT_LOG.md
    └── PROMPT_FIX_*.md
```

## 🚀 빠른 시작

### 🐳 Docker 기반 배포 (권장)

가장 간단하고 안정적인 방법입니다.

```bash
# 1. 프로젝트 클론
git clone https://github.com/<your-username>/5th_project_mvp.git
cd 5th_project_mvp/hint-system

# 2. 환경 변수 설정
cp .env.example .env
# 필요시 .env 파일 편집

# 3. 자동 배포 (딸깍!)
chmod +x quick_start.sh
./quick_start.sh

# 4. 접속
# http://localhost:7860
```

**상세 가이드**: [hint-system/README_DOCKER.md](hint-system/README_DOCKER.md)

### 🌩️ RunPod 클라우드 배포

GPU가 필요한 경우 RunPod에서 배포하세요.

**추천 설정**:
- **GPU**: RTX 4090 (24GB) - ~$0.44/시간 ⭐⭐⭐⭐⭐
- **템플릿**: RunPod PyTorch 2.1
- **디스크**: Container 50GB, Volume 100GB

```bash
# RunPod 인스턴스 SSH 접속 후
cd /workspace
git clone <repository-url>
cd 5th_project_mvp/hint-system

# 자동 배포
./quick_start.sh

# 포트 7860을 RunPod에서 노출
# Console → Connect → HTTP Service → 7860
```

**상세 가이드**: [hint-system/RUNPOD_DEPLOYMENT_GUIDE.md](hint-system/RUNPOD_DEPLOYMENT_GUIDE.md)

### 💻 로컬 개발 모드

Docker 없이 로컬에서 개발하려면:

```bash
cd hint-system

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements-app.txt

# vLLM 서버만 Docker로 실행
docker-compose up -d vllm-server

# Gradio 앱 로컬 실행
python app.py --vllm-url http://localhost:8000/v1
```
## 📊 크롤러 (선택사항)

백준에서 문제 데이터를 직접 수집하려면:

```bash
cd crawler/crawlers

# 의존성 설치
pip install -r requirements.txt

# 크롤링 실행
python crawl_all_hybrid.py
```

**크롤러 기능:**
- 백준 단계별 문제 목록 수집 (1~68단계)
- 문제 상세 정보: 제목, 설명, 입출력 예제
- solved.ac API 통합: 난이도, 태그
- JSON 저장: `crawler/data/raw/`

**참고**: 이미 준비된 데이터가 `hint-system/data/problems_multi_solution.json`에 있으므로 필수는 아닙니다.

## 📚 주요 기능

### 1. AI 힌트 생성
- **소크라테스 학습법**: 답을 주지 않고 질문으로 유도
- **코드 분석**: 완료/누락 부분 자동 파악
- **다음 단계 제시**: 점진적 힌트 제공

### 2. 다중 모델 지원
- **Qwen2.5-Coder-7B**: 코드 생성 특화 (권장)
- **DeepSeek-Coder**: 코드 이해 특화
- **CodeLlama**: Meta 공식 모델

### 3. 실시간 추론
- **vLLM 엔진**: 15-20x 빠른 추론
- **GPU 최적화**: PagedAttention, Continuous Batching
- **낮은 지연시간**: 1-2초 내 응답

## �️ 기술 스택

### 인프라
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션
- **vLLM**: 고속 LLM 추론 엔진

### 백엔드
- **Python 3.10+**
- **OpenAI API (vLLM)**: API 호환 인터페이스
- **requests**: HTTP 클라이언트

### 프론트엔드
- **Gradio 4.44**: 웹 UI 프레임워크

### 크롤러
- **BeautifulSoup4**: HTML 파싱
- **solved.ac API**: 문제 메타데이터

## 📖 문서

### 시작 가이드
- 📘 **[Docker 사용 가이드](hint-system/README_DOCKER.md)** - Docker 기반 배포
- 📗 **[RunPod 배포 가이드](hint-system/RUNPOD_DEPLOYMENT_GUIDE.md)** - 클라우드 GPU 배포
- � **[리팩토링 요약](hint-system/REFACTORING_SUMMARY.md)** - 최신 변경사항

### 개발 문서
- [프롬프트 개선 로그](docs/PROMPT_IMPROVEMENT_LOG.md)
- [데이터 구조 변경](docs/MIGRATION_SUMMARY.md)
- [크롤러 README](crawler/README.md)

## 🎯 프롬프트 엔지니어링

### 소크라테스 학습법 적용
```
❌ 나쁜 힌트: "함수를 정의하려면 def 키워드가 필요해"
✅ 좋은 힌트: "이 계산을 100번 써야 한다면 코드를 100번 복사할 건가?"
```

### 핵심 원칙
1. **답을 직접 주지 않기**
2. **질문으로 유도하기**
3. **학생의 코드 구조 분석**
4. **다음 단계만 제시**

## 🔧 시스템 요구사항

### Docker 배포 (권장)
- **OS**: Linux (Ubuntu 22.04+), Windows 10/11 + WSL2
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **GPU**: NVIDIA GPU + NVIDIA Container Toolkit
- **VRAM**: 24GB (RTX 3090/4090, A5000 등)
- **메모리**: 32GB RAM 권장
- **디스크**: 50GB

### 로컬 개발
- **Python**: 3.10+
- **RAM**: 8GB+ (GPU 미사용 시)
- **GPU**: 선택사항 (CPU도 가능, 느림)

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
