# AI 코딩 힌트 시스템 (Hint System)

Qwen2.5-Coder-7B 기반의 AI 코딩 힌트 생성 시스템입니다. vLLM을 사용하여 빠른 추론 속도를 제공하며, Gradio 웹 인터페이스를 통해 사용자 친화적인 UI를 제공합니다.

## 🚀 빠른 시작 (RunPod 환경)

### 1단계: 저장소 클론 및 이동

```bash
cd /workspace
git clone https://github.com/inucreativehrd21/5th_project_mvp.git
cd 5th_project_mvp/hint-system
```

### 2단계: 스크립트 권한 설정

```bash
bash setup_permissions.sh
```

### 3단계: 의존성 설치 (첫 실행 시)

```bash
bash install_dependencies.sh
```

소요 시간: 약 10-15분

### 4단계: 서버 시작

```bash
bash runpod_start.sh
```

서버가 시작되면 다음 주소로 접속 가능합니다:
- **Gradio UI**: http://localhost:7860
- **vLLM API**: http://localhost:8000/v1

---

## 📋 주요 기능

### 1. AI 코드 힌트 생성
- **모델**: Qwen2.5-Coder-7B-Instruct
- **방식**: RAG 기반 4단계 파이프라인
  1. 문제 메타데이터 조회 (MySQL)
  2. 벡터 유사도 검색 (ChromaDB)
  3. 프롬프트 생성
  4. LLM 추론 (vLLM)

### 2. 빠른 추론 속도
- **vLLM 엔진**: HuggingFace Transformers 대비 15-24배 빠름
- **평균 응답 시간**: 0.5-1초 (Warm Start)
- **GPU 최적화**: PagedAttention, Continuous Batching

### 3. 사용자 친화적 UI
- **Gradio 인터페이스**: 브라우저에서 바로 사용
- **실시간 힌트 생성**: 코드 입력 즉시 힌트 제공
- **Monaco Editor 통합**: VSCode 스타일 코드 편집기

---

## 🛠️ 스크립트 명령어

### 기본 명령어

| 스크립트 | 설명 | 사용 예시 |
|----------|------|-----------|
| `runpod_start.sh` | 서버 시작 (vLLM + Gradio) | `bash runpod_start.sh` |
| `runpod_stop.sh` | 서버 중지 | `bash runpod_stop.sh` |
| `runpod_restart.sh` | 서버 재시작 | `bash runpod_restart.sh` |
| `runpod_status.sh` | 시스템 상태 확인 | `bash runpod_status.sh` |

### 고급 명령어

```bash
# 실시간 로그 모니터링
tail -f logs/vllm_server.log     # vLLM 로그
tail -f logs/gradio_app.log      # Gradio 로그

# GPU 실시간 모니터링
nvidia-smi -l 1

# 시스템 상태 실시간 갱신 (2초마다)
watch -n 2 bash runpod_status.sh
```

---

## ⚙️ 설정 (.env 파일)

### 기본 설정

```bash
# vLLM 서버 설정
VLLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
VLLM_PORT=8000
VLLM_GPU_MEMORY_UTILIZATION=0.85
VLLM_MAX_MODEL_LEN=4096

# Gradio 앱 설정
GRADIO_PORT=7860
VLLM_SERVER_URL=http://localhost:8000/v1

# 데이터 경로
DATA_FILE_PATH=data/problems_multi_solution.json
```

### 성능 튜닝

#### GPU 메모리 조정 (RTX 4090 24GB 기준)

```bash
# 안정적 (권장)
VLLM_GPU_MEMORY_UTILIZATION=0.85

# 공격적 (OOM 위험)
VLLM_GPU_MEMORY_UTILIZATION=0.90

# 보수적 (여유 있음)
VLLM_GPU_MEMORY_UTILIZATION=0.75
```

---

## 📊 시스템 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                  Gradio Web UI                       │
│              (Port 7860, Browser)                    │
│  - 문제 선택                                           │
│  - 코드 입력 (Monaco Editor)                          │
│  - 힌트 요청 및 표시                                   │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼ HTTP API Call
┌──────────────────────────────────────────────────────┐
│              vLLM Inference Server                   │
│            (Port 8000, OpenAI API)                   │
│  - Model: Qwen2.5-Coder-7B-Instruct                 │
│  - GPU: RTX 4090 24GB                                │
│  - Engine: PagedAttention + Continuous Batching     │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼ Model Loading
┌──────────────────────────────────────────────────────┐
│          HuggingFace Model Cache                     │
│      ~/.cache/huggingface/hub/                       │
│  - Tokenizer                                         │
│  - Model Weights (8-bit Quantized)                  │
│  - Config Files                                      │
└──────────────────────────────────────────────────────┘
```

---

## 🐛 문제 해결

### 1. 서버가 시작되지 않음

```bash
# 로그 확인
tail -f logs/vllm_server.log

# GPU 메모리 확인
nvidia-smi

# 포트 충돌 확인
lsof -i :8000
lsof -i :7860

# 재시작
bash runpod_restart.sh
```

### 2. GPU 메모리 부족

```bash
# .env 파일 수정
VLLM_GPU_MEMORY_UTILIZATION=0.75
VLLM_MAX_MODEL_LEN=2048

# 서버 재시작
bash runpod_restart.sh
```

### 3. 모델 다운로드 실패

```bash
# 인터넷 연결 확인
ping huggingface.co

# 캐시 확인
ls -lh ~/.cache/huggingface/hub/

# 수동 다운로드
python3 -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('Qwen/Qwen2.5-Coder-7B-Instruct')"
```

---

## 📈 성능 벤치마크

### RTX 4090 24GB 기준

| 메트릭 | 값 |
|--------|-----|
| 모델 로딩 시간 | 30-60초 |
| 첫 추론 (Cold Start) | 2-3초 |
| 평균 추론 (Warm) | 0.5-1초 |
| 최대 처리량 | ~50 req/min |
| GPU 메모리 사용 | ~18GB |
| GPU 사용률 | 60-90% |

---

## 📚 디렉토리 구조

```
hint-system/
├── runpod_start.sh              # 🟢 서버 시작
├── runpod_stop.sh               # 🔴 서버 중지
├── runpod_restart.sh            # 🔄 서버 재시작
├── runpod_status.sh             # 📊 상태 확인
├── setup_permissions.sh         # 🔧 권한 설정
├── install_dependencies.sh      # 📦 의존성 설치
├── app.py                       # Gradio 앱
├── vllm_server.py               # vLLM 서버 (참고용)
├── requirements.txt             # Python 패키지
├── .env                         # 환경 변수
├── .env.example                 # 환경 변수 예시
├── RUNPOD_GUIDE.md              # 🚀 상세 가이드
├── data/
│   └── problems_multi_solution.json  # 문제 데이터
├── logs/
│   ├── vllm_server.log          # vLLM 로그
│   ├── gradio_app.log           # Gradio 로그
│   ├── vllm.pid                 # vLLM PID
│   └── gradio.pid               # Gradio PID
└── models/
    ├── __init__.py
    ├── model_config.py
    └── model_inference.py       # vLLM 클라이언트
```

---

## 🔗 관련 문서

- **[RUNPOD_GUIDE.md](./RUNPOD_GUIDE.md)** - RunPod 배포 상세 가이드
- **[DEPLOYMENT_SUMMARY.md](../DEPLOYMENT_SUMMARY.md)** - 전체 배포 요약
- **[RECOMMENDATION_ALTERNATIVES.md](../docs/RECOMMENDATION_ALTERNATIVES.md)** - 추천 시스템 아키텍처

---

## 💡 주요 개선사항 (v2.0)

### 2025-11-10 업데이트

1. **RunPod 환경 최적화**
   - 전용 시작/중지/재시작 스크립트 추가
   - 실시간 상태 모니터링 기능
   - GPU 메모리 자동 관리

2. **사용자 경험 개선**
   - 컬러풀한 터미널 출력
   - 진행 상황 시각화
   - 상세한 에러 메시지

3. **안정성 향상**
   - 자동 포트 충돌 해결
   - 프로세스 정리 자동화
   - 헬스체크 통합

4. **문서화 강화**
   - 단계별 가이드 추가
   - 문제 해결 섹션 확장
   - 성능 튜닝 가이드

---

## 🤝 기여

문제 발견 또는 개선 제안:
- **GitHub Issues**: https://github.com/inucreativehrd21/5th_project_mvp/issues
- **Pull Requests**: 환영합니다!

---

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

## 👥 팀

- **AI 모델**: Qwen2.5-Coder-7B-Instruct (Alibaba Cloud)
- **인프라**: RunPod GPU Cloud
- **개발**: 5th Project MVP Team

---

**마지막 업데이트**: 2025-11-10  
**버전**: 2.0 (RunPod Optimized)
