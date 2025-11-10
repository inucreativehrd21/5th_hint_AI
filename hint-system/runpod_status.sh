#!/bin/bash
# ============================================================================
# RunPod 환경 시스템 상태 확인 스크립트
# vLLM + Gradio 프로세스 및 리소스 모니터링
# ============================================================================

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${MAGENTA}📊 AI 코딩 힌트 시스템 - 상태 모니터링${NC}                          ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 작업 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 환경 변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

VLLM_PORT=${VLLM_PORT:-8000}
GRADIO_PORT=${GRADIO_PORT:-7860}

# ============================================================================
# 1. 프로세스 상태
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. 프로세스 상태${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# vLLM 프로세스 확인
echo -e "${CYAN}🚀 vLLM 서버:${NC}"
if [ -f logs/vllm.pid ]; then
    VLLM_PID=$(cat logs/vllm.pid)
    if ps -p "$VLLM_PID" > /dev/null 2>&1; then
        # CPU 및 메모리 사용량
        CPU_MEM=$(ps -p "$VLLM_PID" -o %cpu,%mem,etime --no-headers)
        echo -e "   ${GREEN}✅ 실행 중${NC} (PID: $VLLM_PID)"
        echo -e "   ${CYAN}CPU/MEM/Time:${NC} $CPU_MEM"
    else
        echo -e "   ${RED}❌ 중지됨${NC} (PID 파일 존재하지만 프로세스 없음)"
    fi
else
    VLLM_PROCS=$(pgrep -f "vllm.entrypoints.openai.api_server" || true)
    if [ -n "$VLLM_PROCS" ]; then
        echo -e "   ${YELLOW}⚠️  실행 중이지만 PID 파일 없음${NC}"
        echo "   PIDs: $VLLM_PROCS"
    else
        echo -e "   ${RED}❌ 중지됨${NC}"
    fi
fi

# Gradio 프로세스 확인
echo ""
echo -e "${CYAN}🎨 Gradio 앱:${NC}"
if [ -f logs/gradio.pid ]; then
    GRADIO_PID=$(cat logs/gradio.pid)
    if ps -p "$GRADIO_PID" > /dev/null 2>&1; then
        CPU_MEM=$(ps -p "$GRADIO_PID" -o %cpu,%mem,etime --no-headers)
        echo -e "   ${GREEN}✅ 실행 중${NC} (PID: $GRADIO_PID)"
        echo -e "   ${CYAN}CPU/MEM/Time:${NC} $CPU_MEM"
    else
        echo -e "   ${RED}❌ 중지됨${NC} (PID 파일 존재하지만 프로세스 없음)"
    fi
else
    GRADIO_PROCS=$(pgrep -f "app.py" || true)
    if [ -n "$GRADIO_PROCS" ]; then
        echo -e "   ${YELLOW}⚠️  실행 중이지만 PID 파일 없음${NC}"
        echo "   PIDs: $GRADIO_PROCS"
    else
        echo -e "   ${RED}❌ 중지됨${NC}"
    fi
fi

# ============================================================================
# 2. 네트워크 상태 (포트 리스닝)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. 네트워크 상태${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# vLLM 포트
echo -e "${CYAN}🚀 vLLM 포트 ($VLLM_PORT):${NC}"
if lsof -Pi :$VLLM_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ 리스닝 중${NC}"
    
    # Health check
    if curl -sf "http://localhost:$VLLM_PORT/health" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Health check 성공${NC}"
        
        # 모델 정보 가져오기
        MODEL_INFO=$(curl -s "http://localhost:$VLLM_PORT/v1/models" 2>/dev/null)
        if [ -n "$MODEL_INFO" ]; then
            MODEL_ID=$(echo "$MODEL_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data'][0]['id'])" 2>/dev/null || echo "unknown")
            echo -e "   ${CYAN}현재 모델:${NC} $MODEL_ID"
        fi
    else
        echo -e "   ${YELLOW}⚠️  Health check 실패${NC}"
    fi
else
    echo -e "   ${RED}❌ 포트 사용 안 됨${NC}"
fi

# Gradio 포트
echo ""
echo -e "${CYAN}🎨 Gradio 포트 ($GRADIO_PORT):${NC}"
if lsof -Pi :$GRADIO_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ 리스닝 중${NC}"
    
    # HTTP 접속 확인
    if curl -sf "http://localhost:$GRADIO_PORT/" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ HTTP 접속 가능${NC}"
    else
        echo -e "   ${YELLOW}⚠️  HTTP 접속 실패${NC}"
    fi
else
    echo -e "   ${RED}❌ 포트 사용 안 됨${NC}"
fi

# ============================================================================
# 3. GPU 상태
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. GPU 상태${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v nvidia-smi &> /dev/null; then
    # GPU 정보 (테이블 형식)
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw \
        --format=csv,noheader | while IFS=',' read -r idx name temp util mem_used mem_total power; do
        echo -e "${CYAN}GPU $idx:${NC} $name"
        echo -e "   ${CYAN}온도:${NC}         $temp"
        echo -e "   ${CYAN}사용률:${NC}       $util"
        echo -e "   ${CYAN}메모리:${NC}       $mem_used / $mem_total"
        echo -e "   ${CYAN}전력:${NC}         $power"
        echo ""
    done
    
    # vLLM 프로세스의 GPU 메모리 사용량
    if [ -f logs/vllm.pid ]; then
        VLLM_PID=$(cat logs/vllm.pid)
        GPU_MEM=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader | grep "^$VLLM_PID," | cut -d',' -f2 || echo "N/A")
        if [ "$GPU_MEM" != "N/A" ]; then
            echo -e "${CYAN}vLLM GPU 메모리:${NC} $GPU_MEM"
        fi
    fi
else
    echo -e "${RED}❌ nvidia-smi 없음${NC}"
fi

# ============================================================================
# 4. 디스크 사용량
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. 디스크 사용량${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 작업 디렉토리
WORKSPACE_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo -e "${CYAN}작업 디렉토리:${NC}    $WORKSPACE_SIZE"

# 로그 디렉토리
if [ -d logs ]; then
    LOGS_SIZE=$(du -sh logs 2>/dev/null | cut -f1)
    echo -e "${CYAN}로그 디렉토리:${NC}    $LOGS_SIZE"
fi

# HuggingFace 캐시
if [ -d ~/.cache/huggingface ]; then
    HF_CACHE_SIZE=$(du -sh ~/.cache/huggingface 2>/dev/null | cut -f1)
    echo -e "${CYAN}HF 모델 캐시:${NC}    $HF_CACHE_SIZE"
fi

# 전체 디스크
echo ""
echo -e "${CYAN}전체 디스크 사용량:${NC}"
df -h / | tail -1 | awk '{print "   사용: "$3" / "$2" ("$5")"}'

# ============================================================================
# 5. 최근 로그 (마지막 10줄)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5. 최근 로그${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# vLLM 로그
if [ -f logs/vllm_server.log ]; then
    echo -e "${CYAN}🚀 vLLM 서버 (최근 5줄):${NC}"
    tail -5 logs/vllm_server.log | sed 's/^/   /'
    echo ""
else
    echo -e "${YELLOW}⚠️  vLLM 로그 파일 없음${NC}"
    echo ""
fi

# Gradio 로그
if [ -f logs/gradio_app.log ]; then
    echo -e "${CYAN}🎨 Gradio 앱 (최근 5줄):${NC}"
    tail -5 logs/gradio_app.log | sed 's/^/   /'
    echo ""
else
    echo -e "${YELLOW}⚠️  Gradio 로그 파일 없음${NC}"
    echo ""
fi

# ============================================================================
# 6. 시스템 리소스
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6. 시스템 리소스${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo -e "${CYAN}CPU 사용률:${NC}       ${CPU_USAGE}%"

# 메모리
MEM_INFO=$(free -h | grep Mem)
MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
MEM_PERCENT=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
echo -e "${CYAN}메모리 사용:${NC}      $MEM_USED / $MEM_TOTAL (${MEM_PERCENT}%)"

# 가동 시간
UPTIME=$(uptime -p)
echo -e "${CYAN}시스템 가동:${NC}      $UPTIME"

# ============================================================================
# 요약 및 권장 사항
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${MAGENTA}📝 시스템 상태 요약${NC}                                                ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 상태 요약
VLLM_STATUS="❌"
GRADIO_STATUS="❌"

if lsof -Pi :$VLLM_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    VLLM_STATUS="✅"
fi

if lsof -Pi :$GRADIO_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    GRADIO_STATUS="✅"
fi

echo -e "   ${CYAN}vLLM 서버:${NC}        $VLLM_STATUS"
echo -e "   ${CYAN}Gradio 앱:${NC}        $GRADIO_STATUS"
echo ""

# 권장 사항
if [ "$VLLM_STATUS" = "❌" ] || [ "$GRADIO_STATUS" = "❌" ]; then
    echo -e "${YELLOW}⚠️  일부 서비스가 중지되어 있습니다.${NC}"
    echo -e "${CYAN}   서버 시작: bash runpod_start.sh${NC}"
    echo ""
fi

# GPU 메모리 경고
if command -v nvidia-smi &> /dev/null; then
    GPU_MEM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    GPU_MEM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    GPU_MEM_PERCENT=$((GPU_MEM_USED * 100 / GPU_MEM_TOTAL))
    
    if [ $GPU_MEM_PERCENT -gt 90 ]; then
        echo -e "${RED}⚠️  GPU 메모리 사용률이 ${GPU_MEM_PERCENT}%로 높습니다!${NC}"
        echo -e "${YELLOW}   vLLM GPU 메모리 설정을 낮추는 것을 고려하세요.${NC}"
        echo ""
    fi
fi

echo -e "${MAGENTA}💡 유용한 명령어:${NC}"
echo -e "   ${CYAN}실시간 모니터링:${NC}     watch -n 2 bash runpod_status.sh"
echo -e "   ${CYAN}GPU 모니터링:${NC}        nvidia-smi -l 1"
echo -e "   ${CYAN}로그 실시간 확인:${NC}    tail -f logs/vllm_server.log"
echo -e "   ${CYAN}서버 재시작:${NC}         bash runpod_start.sh"
echo -e "   ${CYAN}서버 중지:${NC}           bash runpod_stop.sh"
echo ""
