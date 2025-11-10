# ============================================================================
# RunPod 배포 가이드 - vLLM Docker 기반 힌트 생성 시스템
# ============================================================================

## 📋 목차
1. [RunPod 인스턴스 설정 권장사항](#runpod-인스턴스-설정-권장사항)
2. [배포 단계](#배포-단계)
3. [트러블슈팅](#트러블슈팅)

---

## 🚀 RunPod 인스턴스 설정 권장사항

### GPU 선택 (모델별)

#### **Qwen2.5-Coder-7B-Instruct (권장)**
| GPU 타입 | VRAM | 가격/시간 | 추천도 | 비고 |
|---------|------|----------|-------|------|
| **RTX 4090** | 24GB | ~$0.44 | ⭐⭐⭐⭐⭐ | **최고 가성비** |
| **RTX A5000** | 24GB | ~$0.49 | ⭐⭐⭐⭐ | 안정적 |
| **RTX 3090** | 24GB | ~$0.39 | ⭐⭐⭐⭐⭐ | 가성비 우수 |
| **RTX A4000** | 16GB | ~$0.29 | ⭐⭐⭐ | 최소 사양 (tight) |
| **A100 40GB** | 40GB | ~$1.09 | ⭐⭐ | 오버스펙, 비쌈 |
| **A100 80GB** | 80GB | ~$1.89 | ⭐ | 매우 비쌈 |

#### **더 작은 모델 (1.5B ~ 3B)**
- RTX 3060 (12GB): ~$0.19/시간
- RTX 3070 (8GB): ~$0.24/시간

### 디스크 용량
- **최소**: 40GB (모델 다운로드 + 시스템)
- **권장**: 50GB (여유 공간 확보)
- **주의**: Container Disk는 모델 캐시가 유지되지 않으므로, Volume Disk를 사용하거나 HuggingFace 캐시 경로를 영구 볼륨에 마운트

### 템플릿 선택
1. **RunPod PyTorch 2.1** (권장)
   - 이미지: `runpod/pytorch:2.1.0-py3.10-cuda12.1.0-devel-ubuntu22.04`
   - Docker와 NVIDIA Container Toolkit 포함
   - GPU 드라이버 설정 완료

2. **RunPod Docker** (직접 설정)
   - 이미지: `runpod/base:0.4.0-cuda12.1.0`
   - Docker Compose 수동 설치 필요

---

## 🛠️ 배포 단계

### 1. RunPod 인스턴스 생성
1. [RunPod Console](https://www.runpod.io/console/pods)에서 **Deploy** 클릭
2. GPU 타입 선택 (위 표 참고)
3. 템플릿: `RunPod PyTorch 2.1` 선택
4. Container Disk: 50GB
5. Volume Disk (선택): 100GB (모델 캐시 영구 저장)
6. **Expose HTTP Ports**: `7860, 8000` 추가
7. **Deploy** 클릭

### 2. 인스턴스 접속
```bash
# SSH 접속 (RunPod Console에서 SSH 명령어 복사)
ssh root@<pod-id>.ssh.runpod.io -p <port> -i ~/.ssh/id_rsa
```

### 3. 프로젝트 클론
```bash
# 작업 디렉토리 이동
cd /workspace

# Git 설치 (필요시)
apt-get update && apt-get install -y git

# 프로젝트 클론
git clone https://github.com/<your-username>/5th_project_mvp.git
cd 5th_project_mvp/hint-system
```

### 4. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (필요시)
nano .env

# 필수 설정 확인
# - VLLM_MODEL (기본값: Qwen/Qwen2.5-Coder-7B-Instruct)
# - VLLM_GPU_MEMORY_UTILIZATION (기본값: 0.85)
# - VLLM_MAX_MODEL_LEN (기본값: 4096)
```

### 5. Docker Compose 설치 (RunPod Docker 템플릿 사용 시)
```bash
# Docker Compose 설치
apt-get update
apt-get install -y docker-compose-plugin

# 또는
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 6. vLLM Docker 이미지 다운로드 (선택)
```bash
# vLLM 이미지 미리 다운로드 (10~15분 소요)
docker pull vllm/vllm-openai:latest

# 모델 미리 다운로드 (선택)
# 이렇게 하면 첫 실행 시 시간 절약
mkdir -p ~/.cache/huggingface
export VLLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct

# Python으로 모델 다운로드
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('${VLLM_MODEL}')"
```

### 7. 시스템 시작
```bash
# Docker Compose로 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# vLLM 서버 로그만 확인
docker-compose logs -f vllm-server

# Gradio 앱 로그만 확인
docker-compose logs -f hint-app
```

### 8. 접속 확인
```bash
# vLLM 서버 헬스체크
curl http://localhost:8000/health

# 모델 목록 확인
curl http://localhost:8000/v1/models

# Gradio 앱 확인
curl http://localhost:7860/
```

### 9. 웹 브라우저 접속
RunPod Console에서 **Connect** → **HTTP Service** → 포트 `7860` 클릭
- URL 형식: `https://<pod-id>-7860.proxy.runpod.net`

---

## 📊 리소스 사용량 모니터링

### GPU 사용률 확인
```bash
# nvidia-smi로 GPU 모니터링
watch -n 1 nvidia-smi

# Docker 컨테이너 리소스 사용량
docker stats
```

### 예상 메모리 사용량 (Qwen2.5-Coder-7B)
- **모델 가중치**: ~14GB (FP16)
- **KV Cache**: ~6GB (batch_size=256, seq_len=4096)
- **기타**: ~2GB
- **총합**: ~22GB (RTX 4090 24GB로 충분)

---

## 🔧 트러블슈팅

### 1. OOM (Out of Memory) 에러
```bash
# GPU 메모리 사용률 낮추기
nano .env
# VLLM_GPU_MEMORY_UTILIZATION=0.85 → 0.75

# 최대 시퀀스 길이 줄이기
# VLLM_MAX_MODEL_LEN=4096 → 2048

# 재시작
docker-compose restart vllm-server
```

### 2. vLLM 서버 연결 실패
```bash
# vLLM 서버 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs vllm-server

# 재시작
docker-compose restart vllm-server

# 헬스체크
curl http://localhost:8000/health
```

### 3. Gradio 앱 접속 안됨
```bash
# 앱 상태 확인
docker-compose ps hint-app

# 로그 확인
docker-compose logs hint-app

# 포트 확인 (7860 노출되었는지)
docker-compose port hint-app 7860

# 재시작
docker-compose restart hint-app
```

### 4. 모델 다운로드 느림
```bash
# HuggingFace 토큰 설정 (선택)
nano .env
# HUGGING_FACE_HUB_TOKEN=your_token_here

# 재시작
docker-compose down
docker-compose up -d
```

### 5. 전체 시스템 재시작
```bash
# 모든 컨테이너 중지 및 제거
docker-compose down

# 볼륨까지 제거 (모델 캐시 초기화)
docker-compose down -v

# 재시작
docker-compose up -d
```

---

## 🎯 성능 최적화 팁

### 1. GPU 메모리 최적화
- **Prefix Caching 활성화**: `--enable-prefix-caching` (이미 적용됨)
- **Flash Attention 사용**: `--use-flash-attention` (Ampere 이상 GPU)

### 2. 배치 처리 최적화
- `--max-num-seqs`: 동시 처리 시퀀스 수 (기본 256)
- `--max-num-batched-tokens`: 배치당 최대 토큰 수

### 3. 다중 GPU 사용
```bash
# .env 파일 수정
VLLM_TENSOR_PARALLEL_SIZE=2  # 2개 GPU 사용

# 재시작
docker-compose restart vllm-server
```

---

## 📝 참고 자료
- [vLLM 공식 문서](https://docs.vllm.ai/)
- [vLLM Docker Hub](https://hub.docker.com/r/vllm/vllm-openai)
- [RunPod 문서](https://docs.runpod.io/)
- [Qwen2.5-Coder 모델](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)

---

## 💡 추가 정보

### 비용 절감 팁
1. **Spot Instances 사용**: On-Demand 대비 ~50% 저렴
2. **Auto-Stop 설정**: 유휴 시간 후 자동 중지
3. **작은 모델 시도**: Qwen2.5-Coder-1.5B-Instruct (RTX 3060 12GB로 가능)

### 보안 권장사항
1. SSH 키 인증 사용
2. 필요한 포트만 노출
3. 환경 변수에 민감 정보 저장 (`.env` 파일을 Git에 커밋하지 않기)
