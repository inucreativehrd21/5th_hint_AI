#!/bin/bash
# ============================================================================
# RunPod 환경 전용 서버 구동 스크립트
# Qwen2.5-Coder-7B + vLLM + Gradio 통합 시스템
# ============================================================================

set -e  # 에러 발생 시 즉시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 로고 출력
clear
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${MAGENTA}🚀 AI 코딩 힌트 시스템 - RunPod 배포 스크립트${NC}                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}Qwen2.5-Coder-7B + vLLM + Gradio${NC}                              ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 작업 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# 1. 환경 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/8] 환경 확인 중...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되지 않았습니다.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Python: ${PYTHON_VERSION}${NC}"

# NVIDIA GPU 확인
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA GPU 드라이버가 없습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GPU 정보:${NC}"
nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader | while IFS=',' read -r idx name total free; do
    echo -e "   ${CYAN}GPU $idx:${NC} $name"
    echo -e "   ${CYAN}Total:${NC} $total | ${CYAN}Free:${NC} $free"
done

# CUDA 버전 확인
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $5}' | cut -d',' -f1)
    echo -e "${GREEN}✅ CUDA: ${CUDA_VERSION}${NC}"
fi

# ============================================================================
# 2. 가상환경 확인 및 생성
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/8] Python 가상환경 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

VENV_PATH="/workspace/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠️  가상환경 없음. 생성 중...${NC}"
    python3 -m venv "$VENV_PATH"
    echo -e "${GREEN}✅ 가상환경 생성 완료: $VENV_PATH${NC}"
else
    echo -e "${GREEN}✅ 가상환경 존재: $VENV_PATH${NC}"
fi

# 가상환경 활성화
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✅ 가상환경 활성화됨${NC}"

# pip 업그레이드
echo -e "${YELLOW}   pip 업그레이드 중...${NC}"
pip install --upgrade pip -q

# ============================================================================
# 3. 환경 변수 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/8] 환경 변수 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# .env 파일 확인
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일 없음. 기본값으로 생성 중...${NC}"
    cat > .env << 'EOF'
# vLLM 서버 설정
VLLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
VLLM_PORT=8000
VLLM_HOST=0.0.0.0
VLLM_GPU_MEMORY_UTILIZATION=0.85
VLLM_MAX_MODEL_LEN=4096
VLLM_TENSOR_PARALLEL_SIZE=1
VLLM_DTYPE=auto

# Gradio 앱 설정
GRADIO_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
VLLM_SERVER_URL=http://localhost:8000/v1

# 데이터 경로
DATA_FILE_PATH=data/problems_multi_solution.json

# 기타 설정
DEFAULT_TEMPERATURE=0.7
HUGGING_FACE_HUB_TOKEN=
EOF
    echo -e "${GREEN}✅ .env 파일 생성됨${NC}"
else
    echo -e "${GREEN}✅ .env 파일 존재${NC}"
fi

# 환경 변수 로드
export $(grep -v '^#' .env | xargs)

# 설정 출력
echo -e "${CYAN}📋 현재 설정:${NC}"
echo -e "   ${CYAN}모델:${NC} ${VLLM_MODEL}"
echo -e "   ${CYAN}vLLM 포트:${NC} ${VLLM_PORT}"
echo -e "   ${CYAN}Gradio 포트:${NC} ${GRADIO_PORT}"
echo -e "   ${CYAN}GPU 메모리:${NC} ${VLLM_GPU_MEMORY_UTILIZATION}"
echo -e "   ${CYAN}최대 토큰:${NC} ${VLLM_MAX_MODEL_LEN}"

# ============================================================================
# 4. 의존성 설치 확인
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/8] 의존성 패키지 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# vLLM 설치 확인
if ! python -c "import vllm" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  vLLM 미설치. 설치 스크립트 실행 필요${NC}"
    echo -e "${YELLOW}   다음 명령어를 실행하세요: bash install_dependencies.sh${NC}"
    exit 1
fi
VLLM_VERSION=$(python -c "import vllm; print(vllm.__version__)" 2>/dev/null || echo "unknown")
echo -e "${GREEN}✅ vLLM: ${VLLM_VERSION}${NC}"

# Gradio 설치 확인
if ! python -c "import gradio" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Gradio 미설치. requirements.txt 설치 필요${NC}"
    pip install -r requirements.txt
fi
GRADIO_VERSION=$(python -c "import gradio; print(gradio.__version__)" 2>/dev/null || echo "unknown")
echo -e "${GREEN}✅ Gradio: ${GRADIO_VERSION}${NC}"

# ChromaDB 설치 확인 (RAG용)
if ! python -c "import chromadb" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  ChromaDB 미설치. 설치 중...${NC}"
    pip install chromadb -q
fi
echo -e "${GREEN}✅ ChromaDB 설치됨${NC}"

# ============================================================================
# 5. 데이터 파일 확인
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/8] 데이터 파일 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DATA_FILE="${DATA_FILE_PATH:-data/problems_multi_solution.json}"

if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}❌ 데이터 파일 없음: $DATA_FILE${NC}"
    echo -e "${YELLOW}   data/ 디렉토리에 problems_multi_solution.json을 배치하세요.${NC}"
    exit 1
fi

# 파일 크기 및 문제 수 확인
FILE_SIZE=$(du -h "$DATA_FILE" | cut -f1)
PROBLEM_COUNT=$(python3 -c "import json; print(len(json.load(open('$DATA_FILE'))))" 2>/dev/null || echo "unknown")

echo -e "${GREEN}✅ 데이터 파일 존재: $DATA_FILE${NC}"
echo -e "   ${CYAN}파일 크기:${NC} $FILE_SIZE"
echo -e "   ${CYAN}문제 수:${NC} $PROBLEM_COUNT개"

# ============================================================================
# 6. 기존 프로세스 확인 및 정리
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/8] 기존 프로세스 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 포트 사용 확인 및 프로세스 종료
for PORT in ${VLLM_PORT} ${GRADIO_PORT}; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  포트 $PORT 사용 중. 프로세스 종료 중...${NC}"
        PID=$(lsof -ti:$PORT)
        kill -9 $PID 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✅ 포트 $PORT 해제됨${NC}"
    else
        echo -e "${GREEN}✅ 포트 $PORT 사용 가능${NC}"
    fi
done

# ============================================================================
# 7. vLLM 서버 시작
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[7/8] vLLM 서버 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 로그 디렉토리 생성
mkdir -p logs

# vLLM 서버 시작
echo -e "${YELLOW}   vLLM 서버 백그라운드로 시작 중...${NC}"
echo -e "${CYAN}   모델:${NC} ${VLLM_MODEL}"

nohup python3 -m vllm.entrypoints.openai.api_server \
    --model "${VLLM_MODEL}" \
    --host "${VLLM_HOST}" \
    --port "${VLLM_PORT}" \
    --gpu-memory-utilization "${VLLM_GPU_MEMORY_UTILIZATION}" \
    --max-model-len "${VLLM_MAX_MODEL_LEN}" \
    --tensor-parallel-size "${VLLM_TENSOR_PARALLEL_SIZE}" \
    --dtype "${VLLM_DTYPE}" \
    --trust-remote-code \
    --max-num-seqs 256 \
    --enable-prefix-caching \
    --disable-log-requests \
    > logs/vllm_server.log 2>&1 &

VLLM_PID=$!
echo -e "${GREEN}✅ vLLM 서버 시작됨 (PID: $VLLM_PID)${NC}"
echo -e "   ${CYAN}로그:${NC} logs/vllm_server.log"

# vLLM 서버 헬스체크 대기
echo -e "${YELLOW}   vLLM 서버 준비 대기 중... (최대 5분)${NC}"
echo -e "${YELLOW}   모델 다운로드 및 로딩 중...${NC}"

VLLM_READY=false
for i in {1..60}; do
    if curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        VLLM_READY=true
        echo ""
        echo -e "${GREEN}✅ vLLM 서버 준비 완료!${NC}"
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

if [ "$VLLM_READY" = false ]; then
    echo -e "${RED}❌ vLLM 서버 시작 실패 (타임아웃)${NC}"
    echo -e "${YELLOW}   로그 확인: tail -f logs/vllm_server.log${NC}"
    exit 1
fi

# vLLM 모델 정보 확인
echo -e "${CYAN}   vLLM 서버 정보:${NC}"
curl -s "http://localhost:${VLLM_PORT}/v1/models" | python3 -m json.tool 2>/dev/null || echo "   (정보 확인 실패)"

# ============================================================================
# 8. Gradio 앱 시작
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[8/8] Gradio 앱 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Gradio 앱 백그라운드로 시작
echo -e "${YELLOW}   Gradio 앱 백그라운드로 시작 중...${NC}"

nohup python3 app.py > logs/gradio_app.log 2>&1 &
GRADIO_PID=$!

echo -e "${GREEN}✅ Gradio 앱 시작됨 (PID: $GRADIO_PID)${NC}"
echo -e "   ${CYAN}로그:${NC} logs/gradio_app.log"

# Gradio 앱 준비 대기
echo -e "${YELLOW}   Gradio 앱 준비 대기 중...${NC}"

GRADIO_READY=false
for i in {1..20}; do
    if curl -s "http://localhost:${GRADIO_PORT}/" > /dev/null 2>&1; then
        GRADIO_READY=true
        echo ""
        echo -e "${GREEN}✅ Gradio 앱 준비 완료!${NC}"
        break
    fi
    echo -n "."
    sleep 3
done
echo ""

if [ "$GRADIO_READY" = false ]; then
    echo -e "${YELLOW}⚠️  Gradio 앱 확인 실패 (타임아웃)${NC}"
    echo -e "${YELLOW}   로그 확인: tail -f logs/gradio_app.log${NC}"
fi

# PID 저장
echo "$VLLM_PID" > logs/vllm.pid
echo "$GRADIO_PID" > logs/gradio.pid

# ============================================================================
# 완료 메시지
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ 배포 완료! 시스템이 실행 중입니다.${NC}                            ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 접속 정보
echo -e "${MAGENTA}📊 접속 정보:${NC}"
echo -e "   ${CYAN}🌐 Gradio UI:${NC}       http://localhost:${GRADIO_PORT}"
echo -e "   ${CYAN}🚀 vLLM API:${NC}        http://localhost:${VLLM_PORT}/v1"
echo -e "   ${CYAN}❤️  vLLM Health:${NC}    http://localhost:${VLLM_PORT}/health"
echo -e "   ${CYAN}📚 API Docs:${NC}        http://localhost:${VLLM_PORT}/docs"
echo ""

# RunPod 외부 접속 정보
if [ -n "$RUNPOD_POD_ID" ]; then
    echo -e "${MAGENTA}🌍 RunPod 외부 접속:${NC}"
    echo -e "   ${CYAN}포트 ${GRADIO_PORT}을 RunPod 대시보드에서 노출하세요.${NC}"
    echo ""
fi

# 프로세스 정보
echo -e "${MAGENTA}🔧 프로세스 정보:${NC}"
echo -e "   ${CYAN}vLLM PID:${NC}          $VLLM_PID"
echo -e "   ${CYAN}Gradio PID:${NC}        $GRADIO_PID"
echo ""

# 유용한 명령어
echo -e "${MAGENTA}📝 유용한 명령어:${NC}"
echo -e "   ${CYAN}실시간 로그 확인:${NC}"
echo -e "     tail -f logs/vllm_server.log    # vLLM 로그"
echo -e "     tail -f logs/gradio_app.log     # Gradio 로그"
echo ""
echo -e "   ${CYAN}프로세스 상태 확인:${NC}"
echo -e "     ps aux | grep vllm              # vLLM 프로세스"
echo -e "     ps aux | grep gradio            # Gradio 프로세스"
echo ""
echo -e "   ${CYAN}서버 중지:${NC}"
echo -e "     bash runpod_stop.sh             # 모든 서버 중지"
echo -e "     kill -9 $VLLM_PID               # vLLM만 중지"
echo -e "     kill -9 $GRADIO_PID             # Gradio만 중지"
echo ""
echo -e "   ${CYAN}시스템 재시작:${NC}"
echo -e "     bash runpod_start.sh            # 이 스크립트 재실행"
echo ""

# GPU 모니터링
echo -e "${MAGENTA}📊 GPU 모니터링:${NC}"
echo -e "   ${CYAN}nvidia-smi -l 1${NC}               # 1초마다 GPU 상태 확인"
echo ""

# 최종 상태 확인
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}시스템이 정상적으로 시작되었습니다! 🎉${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
