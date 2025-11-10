#!/bin/bash
# ============================================================================
# RunPod vLLM Docker 중지 스크립트
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${RED}🛑 AI 코딩 힌트 시스템 중지${NC}                                     ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 작업 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 컨테이너 중지
echo -e "${YELLOW}⏳ 컨테이너 중지 중...${NC}"
docker compose down

echo ""
echo -e "${GREEN}✅ 모든 컨테이너가 중지되었습니다.${NC}"
echo ""

# 최종 상태
echo -e "${CYAN}📊 컨테이너 상태:${NC}"
docker compose ps

# GPU 메모리 확인
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo -e "${CYAN}🎮 GPU 메모리 상태:${NC}"
    nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader | while IFS=',' read -r idx used free; do
        echo -e "   ${CYAN}GPU $idx:${NC} Used: $used | Free: $free"
    done
fi

echo ""
echo -e "${YELLOW}💡 다시 시작하려면:${NC}"
echo -e "   ${CYAN}bash runpod_docker_start.sh${NC}"
echo ""
