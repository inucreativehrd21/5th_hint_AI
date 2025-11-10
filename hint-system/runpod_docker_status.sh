#!/bin/bash
# ============================================================================
# RunPod vLLM Docker 상태 확인 스크립트
# ============================================================================

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${MAGENTA}📊 AI 코딩 힌트 시스템 - 상태 확인${NC}                              ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 작업 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# 1. 컨테이너 상태
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1. 컨테이너 상태${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker compose ps

# ============================================================================
# 2. 서비스 헬스체크
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2. 서비스 헬스체크${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# vLLM 서버 확인
echo -e "${CYAN}🚀 vLLM 서버:${NC}"
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Health Check: OK${NC}"
    
    # 모델 정보
    MODEL_INFO=$(curl -s http://localhost:8000/v1/models 2>/dev/null)
    if [ -n "$MODEL_INFO" ]; then
        MODEL_ID=$(echo "$MODEL_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data'][0]['id'])" 2>/dev/null || echo "unknown")
        echo -e "   ${CYAN}모델:${NC} $MODEL_ID"
    fi
else
    echo -e "   ${YELLOW}⚠️  서버 응답 없음${NC}"
fi

# Gradio 앱 확인
echo ""
echo -e "${CYAN}🎨 Gradio 앱:${NC}"
GRADIO_PORT=$(grep GRADIO_PORT .env 2>/dev/null | cut -d'=' -f2 || echo "7860")
if curl -sf "http://localhost:${GRADIO_PORT}/" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ HTTP: OK${NC}"
else
    echo -e "   ${YELLOW}⚠️  서버 응답 없음${NC}"
fi

# ============================================================================
# 3. GPU 상태
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3. GPU 상태${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total \
        --format=csv,noheader | while IFS=',' read -r idx name temp util mem_used mem_total; do
        echo -e "${CYAN}GPU $idx:${NC} $name"
        echo -e "   ${CYAN}온도:${NC}         $temp"
        echo -e "   ${CYAN}사용률:${NC}       $util"
        echo -e "   ${CYAN}메모리:${NC}       $mem_used / $mem_total"
        echo ""
    done
else
    echo -e "${YELLOW}⚠️  nvidia-smi 없음${NC}"
fi

# ============================================================================
# 4. 디스크 사용량
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}4. 디스크 사용량${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 볼륨
echo -e "${CYAN}Docker 볼륨:${NC}"
docker volume ls | grep hint-system

# HuggingFace 캐시
if [ -d ~/.cache/huggingface ]; then
    HF_SIZE=$(du -sh ~/.cache/huggingface 2>/dev/null | cut -f1)
    echo -e "${CYAN}HF 모델 캐시:${NC}     $HF_SIZE"
fi

# ============================================================================
# 5. 최근 로그
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}5. 최근 로그 (마지막 5줄)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}🚀 vLLM 서버:${NC}"
docker compose logs --tail=5 vllm-server 2>/dev/null | sed 's/^/   /' || echo "   (로그 없음)"

echo ""
echo -e "${CYAN}🎨 Gradio 앱:${NC}"
docker compose logs --tail=5 hint-app 2>/dev/null | sed 's/^/   /' || echo "   (로그 없음)"

# ============================================================================
# 요약
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}💡 유용한 명령어${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "   ${CYAN}실시간 로그:${NC}            docker compose logs -f"
echo -e "   ${CYAN}GPU 모니터링:${NC}           nvidia-smi -l 1"
echo -e "   ${CYAN}컨테이너 재시작:${NC}        docker compose restart"
echo -e "   ${CYAN}시스템 중지:${NC}            bash runpod_docker_stop.sh"
echo ""
