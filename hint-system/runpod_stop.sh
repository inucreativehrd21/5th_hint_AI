#!/bin/bash
# ============================================================================
# RunPod 환경 서버 중지 스크립트
# vLLM + Gradio 프로세스 종료
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${RED}🛑 AI 코딩 힌트 시스템 - 서버 중지${NC}                              ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 작업 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# 1. PID 파일에서 프로세스 종료
# ============================================================================
echo -e "${BLUE}[1/3] PID 파일 기반 프로세스 종료...${NC}"

# vLLM 프로세스 종료
if [ -f logs/vllm.pid ]; then
    VLLM_PID=$(cat logs/vllm.pid)
    if ps -p "$VLLM_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}   vLLM 프로세스 종료 중 (PID: $VLLM_PID)...${NC}"
        kill -15 "$VLLM_PID" 2>/dev/null || true
        sleep 2
        
        # 강제 종료 확인
        if ps -p "$VLLM_PID" > /dev/null 2>&1; then
            echo -e "${RED}   강제 종료 (SIGKILL)...${NC}"
            kill -9 "$VLLM_PID" 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ vLLM 프로세스 종료됨${NC}"
    else
        echo -e "${YELLOW}⚠️  vLLM 프로세스가 이미 종료되었습니다.${NC}"
    fi
    rm -f logs/vllm.pid
else
    echo -e "${YELLOW}⚠️  vLLM PID 파일 없음${NC}"
fi

# Gradio 프로세스 종료
if [ -f logs/gradio.pid ]; then
    GRADIO_PID=$(cat logs/gradio.pid)
    if ps -p "$GRADIO_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}   Gradio 프로세스 종료 중 (PID: $GRADIO_PID)...${NC}"
        kill -15 "$GRADIO_PID" 2>/dev/null || true
        sleep 2
        
        # 강제 종료 확인
        if ps -p "$GRADIO_PID" > /dev/null 2>&1; then
            echo -e "${RED}   강제 종료 (SIGKILL)...${NC}"
            kill -9 "$GRADIO_PID" 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ Gradio 프로세스 종료됨${NC}"
    else
        echo -e "${YELLOW}⚠️  Gradio 프로세스가 이미 종료되었습니다.${NC}"
    fi
    rm -f logs/gradio.pid
else
    echo -e "${YELLOW}⚠️  Gradio PID 파일 없음${NC}"
fi

# ============================================================================
# 2. 포트 기반 프로세스 종료 (백업)
# ============================================================================
echo ""
echo -e "${BLUE}[2/3] 포트 기반 프로세스 종료...${NC}"

# .env 파일에서 포트 읽기
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

VLLM_PORT=${VLLM_PORT:-8000}
GRADIO_PORT=${GRADIO_PORT:-7860}

# 포트 기반 프로세스 종료
for PORT in $VLLM_PORT $GRADIO_PORT; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}   포트 $PORT 사용 중인 프로세스 종료...${NC}"
        PID=$(lsof -ti:$PORT)
        kill -9 $PID 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✅ 포트 $PORT 해제됨${NC}"
    else
        echo -e "${GREEN}✅ 포트 $PORT 이미 해제됨${NC}"
    fi
done

# ============================================================================
# 3. 프로세스 이름 기반 종료 (최종 확인)
# ============================================================================
echo ""
echo -e "${BLUE}[3/3] 프로세스 이름 기반 종료...${NC}"

# vLLM 관련 프로세스
VLLM_PROCS=$(pgrep -f "vllm.entrypoints.openai.api_server" || true)
if [ -n "$VLLM_PROCS" ]; then
    echo -e "${YELLOW}   남아있는 vLLM 프로세스 종료...${NC}"
    echo "$VLLM_PROCS" | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✅ vLLM 프로세스 정리 완료${NC}"
else
    echo -e "${GREEN}✅ vLLM 프로세스 없음${NC}"
fi

# Gradio 관련 프로세스
GRADIO_PROCS=$(pgrep -f "app.py" | grep -v $$ || true)
if [ -n "$GRADIO_PROCS" ]; then
    echo -e "${YELLOW}   남아있는 Gradio 프로세스 종료...${NC}"
    echo "$GRADIO_PROCS" | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✅ Gradio 프로세스 정리 완료${NC}"
else
    echo -e "${GREEN}✅ Gradio 프로세스 없음${NC}"
fi

# ============================================================================
# 완료 메시지
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ 모든 서버 프로세스가 종료되었습니다.${NC}                          ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 최종 상태 확인
echo -e "${CYAN}📊 최종 상태 확인:${NC}"

# 포트 확인
for PORT in $VLLM_PORT $GRADIO_PORT; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "   ${RED}⚠️  포트 $PORT: 여전히 사용 중${NC}"
    else
        echo -e "   ${GREEN}✅ 포트 $PORT: 해제됨${NC}"
    fi
done

# GPU 메모리 확인
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo -e "${CYAN}🎮 GPU 메모리 상태:${NC}"
    nvidia-smi --query-gpu=index,name,memory.used,memory.free --format=csv,noheader | while IFS=',' read -r idx name used free; do
        echo -e "   ${CYAN}GPU $idx:${NC} Used: $used | Free: $free"
    done
fi

echo ""
echo -e "${YELLOW}💡 서버를 다시 시작하려면:${NC}"
echo -e "   ${CYAN}bash runpod_start.sh${NC}"
echo ""
