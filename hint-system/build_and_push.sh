#!/bin/bash
# ============================================================================
# Docker 이미지 빌드 및 푸시 스크립트
# ============================================================================

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}vLLM + Gradio 통합 Docker 이미지 빌드${NC}                             ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Docker Hub 사용자명 입력
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${YELLOW}Docker Hub 사용자명을 입력하세요:${NC}"
    read -p "> " DOCKER_USERNAME
fi

if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED}❌ Docker Hub 사용자명이 필요합니다.${NC}"
    exit 1
fi

# 이미지 이름 및 태그
IMAGE_NAME="${DOCKER_USERNAME}/hint-ai-vllm"
IMAGE_TAG="latest"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${GREEN}✅ 이미지 이름: ${FULL_IMAGE}${NC}"
echo ""

# ============================================================================
# 1. Dockerfile 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/4] Dockerfile 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f "Dockerfile.unified" ]; then
    echo -e "${RED}❌ Dockerfile.unified를 찾을 수 없습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dockerfile.unified 확인됨${NC}"
echo ""

# ============================================================================
# 2. Docker 이미지 빌드
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/4] Docker 이미지 빌드 중... (5-10분 소요)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker build -f Dockerfile.unified -t ${FULL_IMAGE} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 이미지 빌드 완료!${NC}"
else
    echo -e "${RED}❌ 이미지 빌드 실패${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 3. Docker Hub 로그인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/4] Docker Hub 로그인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 이미 로그인되어 있는지 확인
if docker info | grep "Username:" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 이미 Docker Hub에 로그인되어 있습니다.${NC}"
else
    echo -e "${YELLOW}Docker Hub 로그인이 필요합니다.${NC}"
    docker login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Docker Hub 로그인 실패${NC}"
        exit 1
    fi
fi

echo ""

# ============================================================================
# 4. Docker Hub에 푸시
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/4] Docker Hub에 푸시 중...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker push ${FULL_IMAGE}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 이미지 푸시 완료!${NC}"
else
    echo -e "${RED}❌ 이미지 푸시 실패${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 완료
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}🎉 빌드 및 푸시 완료!${NC}                                               ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✨ 이미지가 Docker Hub에 푸시되었습니다!${NC}"
echo -e "   ${CYAN}이미지: ${FULL_IMAGE}${NC}"
echo ""

echo -e "${YELLOW}🚀 RunPod에서 사용하는 방법:${NC}"
echo -e "   1. RunPod 웹사이트 접속"
echo -e "   2. Deploy → Custom Image"
echo -e "   3. Container Image: ${CYAN}${FULL_IMAGE}${NC}"
echo -e "   4. GPU: RTX 4090/5090"
echo -e "   5. Expose Ports: ${CYAN}8000, 7860${NC}"
echo -e "   6. Deploy 클릭!"
echo ""

echo -e "${BLUE}📖 상세 가이드: RUNPOD_UNIFIED_DEPLOY.md${NC}"
echo ""
