# RunPod vLLM Docker 실행 가이드 (멘토님 피드백 반영)

## 🎯 핵심 개념

**멘토님 피드백:**
> DockerHub에서 최신 vllm 관련 이미지가 지속적으로 업데이트 되고 있고, 그 이미지를 단순히 내려받기만 하면 됩니다! 전부 딸깍입니다 ㅎㅎ

**변경 사항:**
- ❌ **Before**: RunPod 접속 → vllm pip 설치 → `python vllm_server.py` 실행
- ✅ **After**: DockerHub 이미지 다운로드 → 컨테이너 실행 → 주소로 통신

---

## 🚀 빠른 시작 (Docker 있는 경우)

### 전제 조건
RunPod에서 **Docker 지원 템플릿** 사용:
- `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- 또는 Base 템플릿

### 원클릭 실행

```bash
cd /workspace
git clone https://github.com/inucreativehrd21/5th_project_mvp.git
cd 5th_project_mvp/hint-system
bash runpod_docker_simple.sh
```

**끝!** 5분이면 실행됩니다.

---

## 📋 작동 원리

### 기존 방식 (Offline Serving)

```
RunPod 인스턴스 생성
  ↓
SSH 접속
  ↓
pip install vllm  (5-10분)
  ↓
python vllm_server.py  (수동 실행)
  ↓
python app.py  (별도 터미널)
```

### 새로운 방식 (Docker 이미지)

```
RunPod 인스턴스 생성 (Docker 지원 템플릿)
  ↓
docker pull vllm/vllm-openai:latest  (딸깍!)
  ↓
docker-compose up -d  (자동 실행)
  ↓
✅ vLLM 서버가 이미 서빙 중!
✅ Gradio UI가 주소로 통신!
```

---

## 🏗️ 아키텍처

### Docker Compose 구조

```yaml
services:
  vllm-server:  # vLLM 공식 이미지
    image: vllm/vllm-openai:latest  # ← 딸깍!
    ports: ["8000:8000"]
    command: >
      --model Qwen/Qwen2.5-Coder-7B-Instruct
      --host 0.0.0.0
      --port 8000
  
  gradio-ui:  # 커스텀 Gradio 앱
    build: Dockerfile.gradio
    ports: ["7860:7860"]
    environment:
      - VLLM_API_BASE=http://vllm-server:8000/v1  # ← 주소로 통신!
```

### 통신 흐름

```
사용자
  ↓ (웹 브라우저)
Gradio UI (7860 포트)
  ↓ (HTTP API 호출)
vLLM Server (8000 포트)
  ↓ (GPU 추론)
응답 반환
```

---

## 📦 파일 구조

### 새로 추가된 파일

```
hint-system/
├── docker-compose.runpod.yml    # Docker Compose 설정 (핵심!)
├── Dockerfile.gradio             # Gradio UI 이미지
├── runpod_docker_simple.sh       # 원클릭 실행 스크립트
└── RUNPOD_DOCKER_GUIDE.md        # 이 문서
```

### 기존 파일 (그대로 사용)

```
hint-system/
├── app.py                        # Gradio UI 코드
├── models/
│   ├── model_inference.py        # vLLM API 호출 로직
│   ├── code_analyzer.py
│   ├── adaptive_prompt.py
│   └── hint_validator.py
├── data/
│   └── problems_multi_solution.json
└── requirements.txt
```

---

## 🔧 상세 설정

### docker-compose.runpod.yml

```yaml
version: '3.8'

services:
  vllm-server:
    image: vllm/vllm-openai:latest  # DockerHub 공식 이미지
    container_name: vllm-hint-server
    ports:
      - "8000:8000"
    environment:
      - HF_TOKEN=${HF_TOKEN:-}  # HuggingFace 토큰 (선택)
    command: >
      --model Qwen/Qwen2.5-Coder-7B-Instruct
      --host 0.0.0.0
      --port 8000
      --dtype auto
      --max-model-len 4096
      --gpu-memory-utilization 0.85
      --trust-remote-code
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - ${HF_HOME:-~/.cache/huggingface}:/root/.cache/huggingface
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 120s

  gradio-ui:
    build:
      context: .
      dockerfile: Dockerfile.gradio
    container_name: hint-gradio-ui
    ports:
      - "7860:7860"
    environment:
      - VLLM_API_BASE=http://vllm-server:8000/v1  # vLLM 서버 주소
      - VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct
    depends_on:
      vllm-server:
        condition: service_healthy  # vLLM 준비 후 시작
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

### Dockerfile.gradio

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Python 패키지
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드
COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

---

## 🎮 사용 방법

### 1. 서비스 시작

```bash
bash runpod_docker_simple.sh
```

또는 수동으로:

```bash
docker-compose -f docker-compose.runpod.yml up -d
```

### 2. 로그 확인

```bash
# vLLM 서버 로그
docker-compose -f docker-compose.runpod.yml logs -f vllm-server

# Gradio UI 로그
docker-compose -f docker-compose.runpod.yml logs -f gradio-ui

# 모든 로그
docker-compose -f docker-compose.runpod.yml logs -f
```

### 3. 서비스 상태 확인

```bash
docker-compose -f docker-compose.runpod.yml ps
```

### 4. Health Check

```bash
# vLLM 서버
curl http://localhost:8000/health

# 모델 정보
curl http://localhost:8000/v1/models

# Gradio UI
curl http://localhost:7860
```

### 5. 서비스 중지

```bash
docker-compose -f docker-compose.runpod.yml down
```

### 6. 서비스 재시작

```bash
docker-compose -f docker-compose.runpod.yml restart
```

---

## 🌐 외부 접속 (RunPod 포트 노출)

### RunPod 대시보드 설정

1. Pod 상세 페이지 이동
2. "Connect" → "TCP Port Mappings"
3. 포트 추가:
   ```
   Internal Port: 7860 → Gradio UI
   Internal Port: 8000 → vLLM API
   ```
4. 생성된 URL로 접속:
   ```
   https://xxxxx-7860.proxy.runpod.net  (Gradio UI)
   https://xxxxx-8000.proxy.runpod.net  (vLLM API)
   ```

---

## 🔥 문제 해결

### Docker가 없는 경우

RunPod PyTorch 템플릿에는 Docker가 없습니다!

**해결 방법:**
```bash
# Python 직접 실행 방식 사용
bash run_python_direct.sh
```

### vLLM 서버가 시작되지 않음

```bash
# 로그 확인
docker-compose -f docker-compose.runpod.yml logs vllm-server

# 컨테이너 재시작
docker-compose -f docker-compose.runpod.yml restart vllm-server
```

### GPU 인식 안 됨

```bash
# NVIDIA Docker Runtime 확인
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# docker-compose.yml에서 GPU 설정 확인
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### 모델 다운로드 느림

HuggingFace 캐시 디렉토리 설정:

```bash
# .env 파일에 추가
HF_HOME=/workspace/.cache/huggingface
```

### 포트 충돌

```bash
# 사용 중인 포트 확인
netstat -tlnp | grep 8000
netstat -tlnp | grep 7860

# 기존 프로세스 종료
docker-compose -f docker-compose.runpod.yml down
```

---

## 📊 리소스 사용량

### GPU 메모리 (RTX 5090 기준)

- **vLLM 모델 로딩**: 약 7-8GB VRAM
- **추론 시**: 추가 2-3GB
- **총 권장**: 16GB+ VRAM

### 디스크 공간

- **모델 다운로드**: 약 15GB
- **Docker 이미지**: 약 10GB
- **총 권장**: 50GB+

---

## 🎓 멘토님 피드백 완전 반영

### Before (기존 방식)

```bash
# 1. RunPod 인스턴스 생성
# 2. SSH 접속
ssh root@xxx.xxx.xxx.xxx

# 3. vLLM 설치 (5-10분)
pip install vllm

# 4. 서버 실행 (수동)
python vllm_server.py  # 터미널 1

# 5. UI 실행 (수동)
python app.py  # 터미널 2
```

### After (Docker 방식)

```bash
# 1. RunPod 인스턴스 생성 (Docker 지원 템플릿)
# 2. 원클릭 실행
bash runpod_docker_simple.sh

# ✅ 끝! vLLM이 이미 서빙 중!
# ✅ Gradio UI가 주소로 통신 중!
```

### 핵심 개선 사항

1. **vLLM 설치 불필요**: Docker 이미지에 포함
2. **수동 실행 불필요**: docker-compose가 자동 실행
3. **업데이트 간단**: `docker pull` 한 번으로 최신 버전
4. **관리 편함**: `docker-compose ps/logs/restart`로 모든 제어
5. **주소로 통신**: `http://vllm-server:8000/v1` 로 API 호출

---

## 📚 추가 자료

### vLLM Docker 공식 문서

- https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html
- DockerHub: https://hub.docker.com/r/vllm/vllm-openai

### Docker Compose 문서

- https://docs.docker.com/compose/

### RunPod 문서

- https://docs.runpod.io/
- GPU Pod: https://docs.runpod.io/pods/overview

---

## ✅ 체크리스트

실행 전 확인:

- [ ] RunPod Pod 생성 (Docker 지원 템플릿)
- [ ] GPU 할당됨 (RTX 4090/5090 권장)
- [ ] 디스크 50GB+ 확보
- [ ] Docker 작동 확인 (`docker ps`)
- [ ] 프로젝트 클론 완료
- [ ] `runpod_docker_simple.sh` 실행
- [ ] vLLM 서버 health check 통과
- [ ] Gradio UI 접속 확인
- [ ] RunPod 포트 노출 설정
- [ ] 외부에서 접속 테스트

---

## 🎉 결론

**멘토님 말씀대로 "딸깍" 완성!**

```bash
# 1. 이미지 다운로드 (딸깍!)
docker pull vllm/vllm-openai:latest

# 2. 실행 (딸깍!)
docker-compose -f docker-compose.runpod.yml up -d

# 3. 접속 (딸깍!)
http://localhost:7860
```

**이제 vLLM 설치도, 수동 실행도 필요 없습니다!** 🚀
