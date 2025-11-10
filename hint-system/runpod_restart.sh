#!/bin/bash
# ============================================================================
# RunPod 환경 서버 재시작 스크립트 (빠른 재시작)
# ============================================================================

set -e

# 색상 정의
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🔄 서버 재시작 중...${NC}"
echo ""

# 작업 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 서버 중지
bash runpod_stop.sh

# 3초 대기
sleep 3

# 서버 시작
bash runpod_start.sh
