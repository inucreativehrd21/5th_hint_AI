# 🚀 vLLM Docker 기반 힌트 생성 시스템

백준 알고리즘 문제 해결을 위한 AI 힌트 생성 시스템입니다. vLLM의 공식 Docker 이미지를 활용하여 빠르고 안정적인 추론을 제공합니다.

## ✨ 주요 특징

- 🐳 **Docker 기반 배포**: vLLM 공식 이미지 사용, 의존성 관리 간소화
- ⚡ **고속 추론**: vLLM의 PagedAttention과 Continuous Batching
- 🎨 **Gradio UI**: 직관적인 웹 인터페이스
- 🔧 **간편한 설정**: 환경 변수 기반 구성
- 🌐 **RunPod 최적화**: 클라우드 GPU 환경 완벽 지원

## 📋 시스템 요구사항

### 최소 사양 (Qwen2.5-Coder-7B 기준)
- **GPU**: NVIDIA GPU (CUDA 12.1+)
  - RTX 3090/4090 (24GB VRAM) - 권장
  - RTX A5000 (24GB VRAM)
  - A100 40GB/80GB (오버스펙)
- **메모리**: 32GB RAM
- **디스크**: 50GB (모델 + 시스템)
- **OS**: Linux (Ubuntu 22.04 권장)

### 소프트웨어
- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/<your-username>/5th_project_mvp.git
cd 5th_project_mvp/hint-system
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 필요시 .env 편집
nano .env
```

### 3. 자동 배포 스크립트 실행
```bash
# 실행 권한 부여
chmod +x quick_start.sh

# 배포 시작
./quick_start.sh
```

### 4. 접속
- **Gradio UI**: http://localhost:7860
- **vLLM API**: http://localhost:8000/v1

## 🐳 수동 배포 (고급)

### Docker Compose로 시작
```bash
# 모든 서비스 시작 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 개별 서비스 관리
```bash
# vLLM 서버만 시작
docker-compose up -d vllm-server

# Gradio 앱만 시작
docker-compose up -d hint-app

# 특정 서비스 재시작
docker-compose restart vllm-server

# 특정 서비스 로그 확인
docker-compose logs -f vllm-server
```

### 시스템 중지
```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 제거 (모델 캐시 초기화)
docker-compose down -v
```

## 🔧 설정 가이드

### 주요 환경 변수 (.env)

```bash
# vLLM 모델 설정
VLLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
VLLM_GPU_MEMORY_UTILIZATION=0.85  # GPU 메모리 사용률 (0.0~1.0)
VLLM_MAX_MODEL_LEN=4096            # 최대 시퀀스 길이

# Gradio 앱 설정
VLLM_SERVER_URL=http://vllm-server:8000/v1
GRADIO_PORT=7860

# 데이터 경로
DATA_FILE_PATH=data/problems_multi_solution.json
```

### GPU 메모리 최적화

OOM (Out of Memory) 에러 발생 시:
```bash
# .env 파일 수정
VLLM_GPU_MEMORY_UTILIZATION=0.75  # 0.85 → 0.75로 낮춤
VLLM_MAX_MODEL_LEN=2048            # 4096 → 2048로 낮춤

# 재시작
docker-compose restart vllm-server
```

## 📊 RunPod 배포

상세한 RunPod 배포 가이드는 [RUNPOD_DEPLOYMENT_GUIDE.md](RUNPOD_DEPLOYMENT_GUIDE.md)를 참고하세요.

### 추천 GPU (가성비)
1. **RTX 4090** (24GB) - ~$0.44/시간 ⭐⭐⭐⭐⭐
2. **RTX 3090** (24GB) - ~$0.39/시간 ⭐⭐⭐⭐⭐
3. **RTX A5000** (24GB) - ~$0.49/시간 ⭐⭐⭐⭐

### 빠른 배포
```bash
# RunPod 인스턴스 SSH 접속 후
cd /workspace
git clone <repository-url>
cd 5th_project_mvp/hint-system

# 자동 배포
chmod +x quick_start.sh
./quick_start.sh

# 포트 7860을 RunPod에서 노출
# Console → Connect → HTTP Service → 7860
```

## 🔍 트러블슈팅

### 시스템 검증
```bash
# 전체 시스템 검증
chmod +x verify_system.sh
./verify_system.sh
```

### 일반적인 문제

#### 1. vLLM 서버 연결 실패
```bash
# 로그 확인
docker-compose logs vllm-server

# 헬스체크
curl http://localhost:8000/health

# 재시작
docker-compose restart vllm-server
```

#### 2. Gradio 앱 접속 불가
```bash
# 로그 확인
docker-compose logs hint-app

# 포트 확인
docker-compose port hint-app 7860

# 재시작
docker-compose restart hint-app
```

#### 3. 데이터 파일 없음
```bash
# 볼륨 마운트 확인
docker-compose exec hint-app ls -la /app/data/

# 파일 존재 확인
ls -la data/problems_multi_solution.json
```

#### 4. GPU 인식 안됨
```bash
# NVIDIA 드라이버 확인
nvidia-smi

# Docker에서 GPU 확인
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# NVIDIA Container Toolkit 재설치
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

## 📝 개발 가이드

### 로컬 개발 (vLLM 서버만 Docker로 실행)

```bash
# vLLM 서버만 시작
docker-compose up -d vllm-server

# 로컬에서 Gradio 앱 실행
pip install -r requirements-app.txt
python app.py --server-name 127.0.0.1 --vllm-url http://localhost:8000/v1
```

### 코드 수정 후 재빌드
```bash
# Gradio 앱만 재빌드
docker-compose build hint-app
docker-compose up -d hint-app

# 전체 재빌드
docker-compose down
docker-compose up --build -d
```

## 📚 프로젝트 구조

```
hint-system/
├── app.py                      # Gradio 애플리케이션 메인
├── config.py                   # 설정 관리
├── docker-compose.yml          # Docker Compose 설정
├── Dockerfile                  # Gradio 앱 Dockerfile
├── requirements-app.txt        # Gradio 앱 의존성
├── .env.example               # 환경 변수 예시
├── quick_start.sh             # 자동 배포 스크립트
├── verify_system.sh           # 시스템 검증 스크립트
├── RUNPOD_DEPLOYMENT_GUIDE.md # RunPod 배포 가이드
├── models/
│   ├── model_inference.py     # VLLMInference 클래스
│   └── model_config.py        # 모델 설정
└── data/
    └── problems_multi_solution.json  # 문제 데이터
```

## 🤝 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📄 라이선스

MIT License

## 🙏 감사의 말

- [vLLM](https://github.com/vllm-project/vllm) - 고속 LLM 추론 엔진
- [Gradio](https://www.gradio.app/) - 웹 UI 프레임워크
- [Qwen](https://github.com/QwenLM/Qwen) - 코드 생성 모델

## 📞 지원

문제가 발생하면 이슈를 생성하거나 다음을 확인하세요:
- [vLLM 공식 문서](https://docs.vllm.ai/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [RunPod 문서](https://docs.runpod.io/)
