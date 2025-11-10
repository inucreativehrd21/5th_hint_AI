#!/bin/bash
# ============================================================================
# Docker 설치 스크립트 (RunPod/Ubuntu 환경)
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${MAGENTA}🐳 Docker 설치 스크립트${NC}                                          ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}RunPod/Ubuntu 환경 전용${NC}                                        ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. 시스템 정보 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/7] 시스템 정보 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# OS 확인
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    echo -e "${GREEN}✅ OS: $OS $VER${NC}"
else
    echo -e "${RED}❌ OS 정보를 확인할 수 없습니다.${NC}"
    exit 1
fi

# 아키텍처 확인
ARCH=$(uname -m)
echo -e "${GREEN}✅ 아키텍처: $ARCH${NC}"

# 이미 Docker가 설치되어 있는지 확인
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${YELLOW}⚠️  Docker가 이미 설치되어 있습니다: $DOCKER_VERSION${NC}"
    read -p "재설치하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}설치를 취소합니다.${NC}"
        exit 0
    fi
fi

# ============================================================================
# 2. 기존 Docker 제거 (있는 경우)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/7] 기존 Docker 제거 중...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   이전 버전의 Docker 패키지 제거 중...${NC}"
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
echo -e "${GREEN}✅ 기존 Docker 제거 완료${NC}"

# ============================================================================
# 3. 시스템 업데이트
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/7] 시스템 패키지 업데이트...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   apt 패키지 목록 업데이트 중... (1-2분 소요)${NC}"
apt-get update -y

echo -e "${YELLOW}   필수 패키지 설치 중...${NC}"
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo -e "${GREEN}✅ 시스템 업데이트 완료${NC}"

# ============================================================================
# 4. Docker GPG 키 추가
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/7] Docker GPG 키 추가...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# GPG 키 디렉토리 생성
install -m 0755 -d /etc/apt/keyrings

# Docker GPG 키 다운로드
echo -e "${YELLOW}   Docker 공식 GPG 키 다운로드 중...${NC}"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo -e "${GREEN}✅ GPG 키 추가 완료${NC}"

# ============================================================================
# 5. Docker 저장소 추가
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/7] Docker 저장소 추가...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   Docker 공식 저장소 추가 중...${NC}"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# 저장소 목록 업데이트
apt-get update -y

echo -e "${GREEN}✅ Docker 저장소 추가 완료${NC}"

# ============================================================================
# 6. Docker Engine 설치
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/7] Docker Engine 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   Docker 패키지 설치 중... (2-3분 소요)${NC}"
apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

echo -e "${GREEN}✅ Docker Engine 설치 완료${NC}"

# Docker 서비스 시작
echo -e "${YELLOW}   Docker 서비스 시작 중...${NC}"
systemctl start docker
systemctl enable docker

echo -e "${GREEN}✅ Docker 서비스 시작됨${NC}"

# ============================================================================
# 7. NVIDIA Container Toolkit 설치 (GPU 지원)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[7/7] NVIDIA Container Toolkit 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# NVIDIA GPU 확인
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA GPU 감지됨${NC}"
    
    # NVIDIA Container Toolkit 저장소 추가
    echo -e "${YELLOW}   NVIDIA Container Toolkit 저장소 추가 중...${NC}"
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    apt-get update -y
    
    # NVIDIA Container Toolkit 설치
    echo -e "${YELLOW}   NVIDIA Container Toolkit 설치 중...${NC}"
    apt-get install -y nvidia-container-toolkit
    
    # Docker 데몬 재시작
    systemctl restart docker
    
    echo -e "${GREEN}✅ NVIDIA Container Toolkit 설치 완료${NC}"
else
    echo -e "${YELLOW}⚠️  NVIDIA GPU가 감지되지 않았습니다.${NC}"
    echo -e "${YELLOW}   GPU 없이 Docker만 사용할 수 있습니다.${NC}"
fi

# ============================================================================
# 설치 확인
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ Docker 설치 완료!${NC}                                              ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 버전 정보
echo -e "${MAGENTA}📦 설치된 버전:${NC}"
echo -e "   ${CYAN}Docker:${NC}          $(docker --version)"
echo -e "   ${CYAN}Docker Compose:${NC}  $(docker compose version)"

if command -v nvidia-smi &> /dev/null; then
    echo -e "   ${CYAN}NVIDIA Toolkit:${NC}  설치됨"
fi

echo ""

# 테스트
echo -e "${MAGENTA}🧪 설치 테스트:${NC}"
echo -e "${YELLOW}   Hello World 컨테이너 실행 중...${NC}"
if docker run --rm hello-world > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker가 정상적으로 작동합니다!${NC}"
else
    echo -e "${RED}❌ Docker 테스트 실패${NC}"
fi

# GPU 테스트
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo -e "${YELLOW}   GPU 테스트 중...${NC}"
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
        echo -e "${GREEN}✅ GPU가 Docker에서 정상적으로 작동합니다!${NC}"
    else
        echo -e "${RED}❌ GPU 테스트 실패${NC}"
        echo -e "${YELLOW}   Docker 데몬을 다시 시작해보세요: systemctl restart docker${NC}"
    fi
fi

echo ""
echo -e "${MAGENTA}📝 다음 단계:${NC}"
echo -e "   1. ${CYAN}cd /workspace/5th_project_mvp/hint-system${NC}"
echo -e "   2. ${CYAN}bash runpod_docker_start.sh${NC}"
echo ""

echo -e "${MAGENTA}💡 유용한 명령어:${NC}"
echo -e "   ${CYAN}docker --version${NC}              # Docker 버전 확인"
echo -e "   ${CYAN}docker ps${NC}                     # 실행 중인 컨테이너 확인"
echo -e "   ${CYAN}docker images${NC}                 # 이미지 목록 확인"
echo -e "   ${CYAN}docker compose version${NC}        # Docker Compose 버전 확인"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 설치가 완료되었습니다!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
