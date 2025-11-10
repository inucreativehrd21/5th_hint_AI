# 🚀 RunPod vLLM 통합 이미지 배포 가이드

## 🎯 개요

vLLM 공식 이미지를 베이스로 Gradio UI가 통합된 **단일 Docker 이미지**를 생성하여 RunPod에서 "딸깍" 배포합니다.

---

## 📦 준비물

- Docker Desktop 설치 (로컬 빌드용)
- Docker Hub 계정
- RunPod 계정
- GPU: RTX 4090/5090 (24GB VRAM 권장)

---

## 🔨 1단계: Docker 이미지 빌드

### 1-1. 프로젝트 클론 (로컬)

```bash
git clone https://github.com/inucreativehrd21/5th_hint_AI.git
cd 5th_hint_AI/hint-system
```

### 1-2. Docker 이미지 빌드

```bash
# Docker Hub 사용자명 설정
DOCKER_USERNAME="your-dockerhub-username"

# 이미지 빌드 (5-10분 소요)
docker build -f Dockerfile.unified -t ${DOCKER_USERNAME}/hint-ai-vllm:latest .
```

**빌드 내용:**
- ✅ vLLM 공식 이미지 베이스 (`vllm/vllm-openai:latest`)
- ✅ Gradio 4.44.0 + 필수 패키지 설치
- ✅ 앱 코드 복사 및 환경 설정
- ✅ vLLM + Gradio 동시 실행 스크립트 생성

### 1-3. 로컬 테스트 (선택사항)

```bash
# GPU 있는 경우 테스트
docker run --gpus all \
  -p 8000:8000 \
  -p 7860:7860 \
  --ipc=host \
  --shm-size=16gb \
  ${DOCKER_USERNAME}/hint-ai-vllm:latest

# 접속 테스트
curl http://localhost:8000/health
# 브라우저: http://localhost:7860
```

---

## 📤 2단계: Docker Hub에 푸시

### 2-1. Docker Hub 로그인

```bash
docker login
# Username: your-dockerhub-username
# Password: your-dockerhub-password
```

### 2-2. 이미지 푸시

```bash
docker push ${DOCKER_USERNAME}/hint-ai-vllm:latest
```

**푸시 완료 후 이미지 주소:**
```
your-dockerhub-username/hint-ai-vllm:latest
```

---

## 🎮 3단계: RunPod에서 Pod 생성

### 3-1. RunPod 웹사이트 접속

https://www.runpod.io → 로그인

### 3-2. Pod 생성

1. **"Deploy"** 클릭
2. **GPU 선택**:
   - **Secure Cloud** 또는 **Community Cloud**
   - **GPU**: RTX 4090 또는 RTX 5090
   - **VRAM**: 24GB 권장

3. **템플릿 설정**:
   - **"Use Custom Image"** 클릭
   - **Container Image**: `your-dockerhub-username/hint-ai-vllm:latest`
   
4. **추가 설정**:
   - **Container Disk**: 50GB 이상
   - **Volume Disk**: 선택사항
   - **Expose Ports**: `8000, 7860`
   
5. **환경 변수** (선택사항):
   ```
   HF_TOKEN=your_huggingface_token_here
   VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct
   ```

6. **"Deploy"** 클릭!

---

## ✅ 4단계: Pod 구동 확인

### 4-1. Pod 시작 대기

- Pod 생성 후 **5-10분** 대기
- 모델 다운로드 + vLLM 서버 시작 시간

### 4-2. 로그 확인

RunPod 대시보드에서:
1. Pod 클릭 → **"Logs"** 탭
2. 다음 메시지 확인:
   ```
   🚀 Starting vLLM + Gradio Hint System...
   📦 Starting vLLM server on port 8000...
   ✅ vLLM server is ready!
   🎨 Starting Gradio UI on port 7860...
   ```

### 4-3. 접속

#### 방법 1: RunPod 포트 매핑 (추천)

1. Pod 상세 페이지 → **"Connect"** 탭
2. **"TCP Port Mappings"** 섹션에서 외부 URL 확인:
   ```
   7860 → https://xxxxx-7860.proxy.runpod.net (Gradio UI)
   8000 → https://xxxxx-8000.proxy.runpod.net (vLLM API)
   ```

#### 방법 2: SSH 터널링

```bash
# RunPod SSH 접속 정보 확인
ssh -p <SSH_PORT> root@<POD_IP>

# 터널링 (로컬 머신에서)
ssh -L 7860:localhost:7860 -L 8000:localhost:8000 -p <SSH_PORT> root@<POD_IP>

# 브라우저에서 접속
http://localhost:7860  # Gradio UI
http://localhost:8000  # vLLM API
```

---

## 🧪 5단계: 작동 테스트

### 5-1. vLLM API 테스트

```bash
# Health Check
curl https://xxxxx-8000.proxy.runpod.net/health

# 모델 정보
curl https://xxxxx-8000.proxy.runpod.net/v1/models
```

### 5-2. Gradio UI 테스트

1. Gradio URL 접속: `https://xxxxx-7860.proxy.runpod.net`
2. 문제 번호 입력 (예: `1000`)
3. 코드 작성
4. **"💡 힌트 받기"** 클릭
5. 힌트 생성 확인 (3-5초 소요)

---

## 📊 리소스 모니터링

### Pod 내부에서 확인

```bash
# SSH 접속
ssh -p <SSH_PORT> root@<POD_IP>

# GPU 사용량
nvidia-smi

# 프로세스 확인
ps aux | grep python

# 메모리 사용량
free -h

# 디스크 사용량
df -h
```

### RunPod 대시보드

- **"Stats"** 탭에서 실시간 GPU/CPU/메모리 사용량 확인

---

## 🔧 트러블슈팅

### 문제 1: Pod이 시작되지 않음

**증상**: Pod이 "Pending" 상태에서 멈춤

**해결:**
```bash
# 로그 확인
RunPod Dashboard → Logs

# 일반적인 원인:
1. 이미지 pull 실패 → Docker Hub 이미지 주소 확인
2. GPU 메모리 부족 → 더 큰 GPU 선택
3. 디스크 부족 → Container Disk 크기 증가 (50GB+)
```

### 문제 2: vLLM 서버 시작 실패

**증상**: 로그에 "CUDA out of memory" 에러

**해결:**
```bash
# 환경변수 추가 (GPU 메모리 사용률 감소)
VLLM_GPU_MEMORY_UTILIZATION=0.75

# 또는 더 작은 모델 사용
VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-1.5B-Instruct
```

### 문제 3: Gradio UI 접속 안 됨

**증상**: vLLM은 정상이지만 Gradio가 안 열림

**해결:**
```bash
# SSH 접속 후 수동 확인
curl http://localhost:7860

# 로그 확인
docker logs <container_id>

# 포트 노출 확인
RunPod Dashboard → Connect → TCP Port Mappings
```

### 문제 4: 모델 다운로드 느림

**증상**: HuggingFace에서 모델 다운로드가 매우 느림

**해결:**
```bash
# HuggingFace 토큰 설정 (환경변수)
HF_TOKEN=your_token_here

# 또는 미리 다운로드된 모델 사용 (Volume 마운트)
# RunPod Volume에 모델 저장 후 마운트
```

---

## 📝 유용한 명령어

### Docker Hub 이미지 업데이트

```bash
# 코드 수정 후 재빌드
docker build -f Dockerfile.unified -t ${DOCKER_USERNAME}/hint-ai-vllm:latest .

# 새 버전 태그 추가
docker tag ${DOCKER_USERNAME}/hint-ai-vllm:latest ${DOCKER_USERNAME}/hint-ai-vllm:v1.0

# 푸시
docker push ${DOCKER_USERNAME}/hint-ai-vllm:latest
docker push ${DOCKER_USERNAME}/hint-ai-vllm:v1.0
```

### RunPod Pod 재시작

```bash
# Pod 중지
RunPod Dashboard → Stop Pod

# Pod 시작
RunPod Dashboard → Start Pod

# 또는 SSH 접속 후 컨테이너 재시작
docker restart <container_id>
```

---

## 🎯 최종 체크리스트

배포 완료 확인:

- [ ] Docker 이미지 빌드 완료
- [ ] Docker Hub 푸시 완료
- [ ] RunPod Pod 생성 완료
- [ ] vLLM 서버 정상 작동 (`/health` 응답 확인)
- [ ] Gradio UI 접속 가능
- [ ] 힌트 생성 테스트 성공
- [ ] 외부 URL로 접속 가능
- [ ] 리소스 사용량 정상 (GPU 메모리 80% 이하)

---

## 🚀 요약

### 로컬에서 (한 번만)

```bash
# 1. 빌드
docker build -f Dockerfile.unified -t your-username/hint-ai-vllm:latest .

# 2. 푸시
docker login
docker push your-username/hint-ai-vllm:latest
```

### RunPod에서 (매번)

1. **Deploy** → **Custom Image**
2. 이미지: `your-username/hint-ai-vllm:latest`
3. GPU: RTX 4090/5090
4. Ports: `8000, 7860`
5. **Deploy** 클릭!

**끝! 5-10분 후 사용 가능!** 🎉

---

## 📚 참고 자료

- **vLLM 공식 문서**: https://docs.vllm.ai/
- **Gradio 문서**: https://www.gradio.app/docs
- **RunPod 문서**: https://docs.runpod.io/
- **Docker Hub**: https://hub.docker.com/

---

## 💡 팁

### 비용 절약

- **Spot Instances** 사용 (Community Cloud)
- 사용 안 할 때는 Pod **Stop**
- Volume을 사용해 모델 캐시 재사용

### 성능 최적화

- `--gpu-memory-utilization 0.85` → `0.90` (여유 있을 때)
- `--max-model-len 4096` → `8192` (긴 코드 처리)
- SSD Volume 마운트로 I/O 속도 향상

### 자동화

- RunPod API로 Pod 생성 자동화
- GitHub Actions로 Docker 이미지 자동 빌드/푸시
- Webhook으로 배포 트리거

---

**이제 RunPod에서 vLLM 템플릿을 선택하듯이 여러분의 통합 이미지를 선택하면 끝입니다!** 🚀
