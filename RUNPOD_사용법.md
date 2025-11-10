# 🚀 RunPod 배포 & 사용 가이드

## ✅ 빌드 완료 확인

GitHub Actions 빌드가 성공했다면:

1. **DockerHub 확인**: https://hub.docker.com/r/inucreativehrd21/hint-ai-vllm
   - `latest` 태그가 보여야 함
   - "Last pushed" 시간이 방금이어야 함

2. **이미지 주소**:
   ```
   inucreativehrd21/hint-ai-vllm:latest
   ```

---

## 🎮 RunPod 배포 (5분 완성)

### 1단계: RunPod 접속

1. https://www.runpod.io 접속
2. 로그인 (계정 없으면 회원가입)
3. 좌측 메뉴 **"Pods"** 클릭
4. 우측 상단 **"+ Deploy"** 버튼 클릭

### 2단계: GPU 선택

**추천 GPU:**
- ✅ **RTX 4090** (24GB VRAM) - 가성비 최고
- ✅ **RTX 5090** (32GB VRAM) - 최고 성능
- ⚠️ RTX 3090 (24GB) - 사용 가능하나 느림

**선택 방법:**
- GPU 카드에서 "Secure Cloud" 또는 "Community Cloud" 선택
- 시간당 가격 확인 (보통 $0.3~$0.7/hour)
- **"Select"** 버튼 클릭

### 3단계: 템플릿 설정

스크롤을 내려 **"Customize Deployment"** 섹션에서:

#### Container Configuration

**Container Image:**
```
inucreativehrd21/hint-ai-vllm:latest
```

**Container Disk:**
```
50 GB
```
(모델 다운로드 공간 필요)

**Expose HTTP Ports:**
```
8000, 7860
```

**Expose TCP Ports:** (선택사항, HTTP로 충분)
```
비워둬도 됨
```

#### Environment Variables (선택사항)

필요하면 추가:

| Name | Value |
|------|-------|
| `HF_TOKEN` | `hf_xxxxxxxxxxxxx` (Hugging Face 토큰) |
| `VLLM_MODEL_NAME` | `Qwen/Qwen2.5-Coder-7B-Instruct` |

> **참고**: HF_TOKEN은 private 모델일 때만 필요. Qwen2.5-Coder는 public이라 없어도 됨!

### 4단계: 배포 시작

1. 스크롤을 최하단으로 내림
2. **"Deploy"** 버튼 클릭
3. 비용 확인 후 **"Confirm"** 클릭

---

## ⏱️ 초기 구동 시간

Pod가 시작되면:

1. **Docker 이미지 다운로드**: 2-3분
2. **vLLM 서버 시작**: 1-2분
3. **모델 다운로드**: 3-5분 (Qwen2.5-Coder-7B, 약 15GB)
4. **Gradio UI 시작**: 10초

**총 소요 시간: 약 6-10분**

### 로그 확인 방법

Pod 카드에서:
- **"Logs"** 버튼 클릭
- 실시간 로그 확인
- 다음 메시지가 보이면 준비 완료:

```
🚀 Starting vLLM + Gradio Hint System...
========================================
[vLLM] Model loaded successfully
[Gradio] Running on: http://0.0.0.0:7860
```

---

## 🌐 접속 방법

### Gradio UI 접속 (추천)

1. RunPod Pod 카드에서 **"Connect"** 버튼 클릭
2. **"Connect to HTTP Service [Port 7860]"** 선택
3. 또는 직접 URL:
   ```
   https://xxxxx-7860.proxy.runpod.net
   ```
   (xxxxx는 Pod ID)

### vLLM API 접속 (개발자용)

```
https://xxxxx-8000.proxy.runpod.net/v1
```

API 테스트:
```bash
curl https://xxxxx-8000.proxy.runpod.net/v1/models
```

---

## 💡 힌트 시스템 사용하기

### 1. Gradio UI에서 사용

1. **문제 번호** 입력: `1000` (백준 문제 번호)
2. **사용자 코드** 붙여넣기:
   ```python
   a, b = map(int, input().split())
   print(a + b)
   ```
3. **힌트 레벨** 선택: 1~3
4. **"힌트 생성"** 버튼 클릭
5. 결과 확인!

### 2. Python 코드에서 사용

```python
import openai

# RunPod vLLM API 엔드포인트
client = openai.OpenAI(
    base_url="https://xxxxx-8000.proxy.runpod.net/v1",
    api_key="dummy"  # vLLM은 API key 불필요
)

# 힌트 생성 요청
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-7B-Instruct",
    messages=[
        {"role": "system", "content": "You are a coding hint assistant."},
        {"role": "user", "content": "백준 1000번 문제에서 틀렸습니다. 힌트 주세요."}
    ]
)

print(response.choices[0].message.content)
```

---

## 🛠️ 문제 해결

### ImportError: cannot import name 'AutoVideoProcessor'

**증상**: Pod 로그에서 다음 오류 발생
```
ImportError: cannot import name 'AutoVideoProcessor' from 'transformers'
```

**원인**: vLLM과 transformers 버전 호환 문제

**해결**: 이미 수정됨! (transformers 4.46.0으로 업그레이드)
- 최신 이미지를 다시 Pull 하세요
- Pod Stop → Start 또는 Terminate → 새로 Deploy

---

### Pod가 시작되지 않을 때

**증상**: Pod 상태가 계속 "Starting..."

**해결**:
1. Logs 확인
2. 이미지 이름 확인: `inucreativehrd21/hint-ai-vllm:latest`
3. Container Disk 50GB 이상인지 확인
4. GPU 메모리 20GB 이상인지 확인

### 모델 다운로드가 너무 느릴 때

**증상**: 10분 이상 걸림

**해결**:
1. RunPod 데이터센터 위치 확인
2. EU나 US 리전 선택
3. 한국에서는 US West 추천

### Gradio UI가 안 보일 때

**증상**: 7860 포트 접속 시 "Cannot connect"

**해결**:
1. Pod 로그 확인
2. `[Gradio] Running on` 메시지 확인
3. 5분 정도 더 기다리기 (모델 로딩 중)
4. Pod 재시작: Stop → Start

### Out of Memory 오류

**증상**: `CUDA out of memory`

**해결**:
1. GPU VRAM 확인 (최소 20GB 필요)
2. RTX 4090 또는 RTX 5090 사용
3. 다른 Pod 종료

---

## 💰 비용 관리

### 사용 후 반드시 중지!

Pod 사용 안 할 때:
1. Pod 카드에서 **"Stop"** 클릭
2. 중지된 Pod는 과금 안 됨
3. 다시 사용할 때 **"Start"** 클릭

### 완전 삭제

더 이상 사용 안 할 때:
1. Pod 카드에서 **"Terminate"** 클릭
2. 확인 메시지에서 **"Yes, terminate"**

### 예상 비용

- **RTX 4090**: $0.34/hour (저렴!)
- **RTX 5090**: $0.69/hour (성능 최고)
- **테스트**: 1시간 사용 시 약 $0.5
- **개발**: 하루 8시간 사용 시 약 $3

---

## 🔄 업데이트 방법

코드를 수정하고 새로 배포하려면:

### 1. 로컬에서 코드 수정

```bash
cd c:\develop1\model1\5th-project_mvp
# hint-system/ 폴더 안의 파일 수정
```

### 2. GitHub에 푸시

```bash
git add .
git commit -m "Update hint system logic"
git push origin main
```

### 3. GitHub Actions 빌드 대기

- GitHub → Actions 탭에서 빌드 확인
- 5-10분 대기

### 4. RunPod에서 재시작

**Option A: 같은 Pod 재사용**
```
1. Pod Stop
2. 1분 대기
3. Pod Start (자동으로 latest 이미지 다운로드)
```

**Option B: 새 Pod 생성**
```
1. 기존 Pod Terminate
2. 새 Pod Deploy (위 가이드 반복)
```

---

## 📱 접속 URL 정리

배포 완료 후 이 주소들을 메모하세요:

| 서비스 | URL | 용도 |
|--------|-----|------|
| **Gradio UI** | `https://xxxxx-7860.proxy.runpod.net` | 웹 인터페이스 |
| **vLLM API** | `https://xxxxx-8000.proxy.runpod.net/v1` | API 호출 |
| **API Docs** | `https://xxxxx-8000.proxy.runpod.net/docs` | API 문서 |

---

## ✅ 체크리스트

배포 전:
- [ ] DockerHub에 이미지 있는지 확인
- [ ] RunPod 계정에 크레딧 있는지 확인
- [ ] GPU 선택 (RTX 4090/5090)

배포 중:
- [ ] Container Image 입력: `inucreativehrd21/hint-ai-vllm:latest`
- [ ] Container Disk: 50GB
- [ ] Expose Ports: 8000, 7860
- [ ] Deploy 클릭

배포 후:
- [ ] Logs에서 "Running on" 메시지 확인
- [ ] Gradio UI 접속 테스트
- [ ] 힌트 생성 테스트
- [ ] **사용 안 할 땐 Stop!**

---

## 🎉 완료!

이제 어디서든 RunPod URL로 힌트 시스템을 사용할 수 있습니다!

**질문이나 문제가 있으면:**
- RunPod Logs 확인
- GitHub Issues에 문의
- GITHUB_ACTIONS_GUIDE.md 참고

**Happy Coding! 🚀**
