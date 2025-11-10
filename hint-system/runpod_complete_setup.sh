#!/bin/bash
# ============================================================================
# 🚀 RunPod 완전 자동 설치 스크립트
# ============================================================================
# 이 스크립트 하나로 모든 것을 설치합니다!
# - Docker
# - NVIDIA Container Toolkit
# - Docker Runtime 설정
# - 필수 유틸리티
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
echo -e "${CYAN}║${NC}  ${MAGENTA}🚀 RunPod 완전 자동 설치 스크립트${NC}                              ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}Docker + NVIDIA Runtime 원스톱 설치${NC}                          ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⏱️  예상 소요 시간: 8-12분${NC}"
echo -e "${YELLOW}📦 설치 항목: Docker, Docker Compose, NVIDIA Container Toolkit${NC}"
echo ""
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}설치를 취소합니다.${NC}"
    exit 0
fi

# ============================================================================
# 1. 시스템 확인
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/8] 시스템 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Root 권한 확인
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ 이 스크립트는 root 권한이 필요합니다.${NC}"
    echo -e "${YELLOW}   다음과 같이 실행하세요: sudo bash $0${NC}"
    exit 1
fi

# OS 확인
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}✅ OS: $NAME $VERSION_ID${NC}"
else
    echo -e "${RED}❌ OS 정보를 확인할 수 없습니다.${NC}"
    exit 1
fi

# GPU 확인
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA GPU 드라이버 확인됨${NC}"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -1 | while read line; do
        echo -e "${CYAN}   GPU: $line${NC}"
    done
else
    echo -e "${YELLOW}⚠️  nvidia-smi를 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}   GPU 없이 Docker만 설치합니다.${NC}"
fi

# ============================================================================
# 2. 기존 Docker 제거
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/8] 기존 Docker 제거...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
echo -e "${GREEN}✅ 기존 Docker 제거 완료${NC}"

# ============================================================================
# 3. 시스템 업데이트
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/8] 시스템 업데이트...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   apt 업데이트 중...${NC}"
apt-get update -y

echo -e "${YELLOW}   필수 패키지 설치 중...${NC}"
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    wget \
    vim \
    htop \
    tmux \
    jq \
    tree

echo -e "${GREEN}✅ 시스템 업데이트 완료${NC}"

# ============================================================================
# 4. Docker 저장소 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/8] Docker 저장소 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# GPG 키 디렉토리 생성
install -m 0755 -d /etc/apt/keyrings

# Docker GPG 키 추가
echo -e "${YELLOW}   Docker GPG 키 다운로드 중...${NC}"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# 저장소 추가
echo -e "${YELLOW}   Docker 저장소 추가 중...${NC}"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y

echo -e "${GREEN}✅ Docker 저장소 설정 완료${NC}"

# ============================================================================
# 5. Docker 설치
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/8] Docker 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   Docker 패키지 설치 중... (2-3분 소요)${NC}"
apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Docker 서비스 시작
systemctl start docker
systemctl enable docker

echo -e "${GREEN}✅ Docker 설치 완료${NC}"
echo -e "${CYAN}   버전: $(docker --version)${NC}"
echo -e "${CYAN}   Compose: $(docker compose version)${NC}"

# ============================================================================
# 6. NVIDIA Container Toolkit 설치
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/8] NVIDIA Container Toolkit 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}   NVIDIA 저장소 설정 중...${NC}"
    
    # GPG 키 다운로드
    mkdir -p /usr/share/keyrings
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
        gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    
    # 저장소 추가
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    apt-get update -y
    
    echo -e "${YELLOW}   NVIDIA Container Toolkit 설치 중...${NC}"
    apt-get install -y nvidia-container-toolkit
    
    echo -e "${GREEN}✅ NVIDIA Container Toolkit 설치 완료${NC}"
else
    echo -e "${YELLOW}⚠️  NVIDIA GPU 없음, 건너뜁니다.${NC}"
fi

# ============================================================================
# 7. Docker 데몬 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[7/8] Docker 데몬 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

mkdir -p /etc/docker

# 기존 설정 백업
if [ -f /etc/docker/daemon.json ]; then
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)
fi

if command -v nvidia-smi &> /dev/null; then
    # NVIDIA Runtime 설정
    echo -e "${YELLOW}   NVIDIA Runtime 설정 중...${NC}"
    cat > /etc/docker/daemon.json <<'EOF'
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    },
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
else
    # 기본 설정
    echo -e "${YELLOW}   기본 Docker 설정 중...${NC}"
    cat > /etc/docker/daemon.json <<'EOF'
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
fi

echo -e "${GREEN}✅ Docker 데몬 설정 완료${NC}"

# Docker 재시작
echo -e "${YELLOW}   Docker 재시작 중...${NC}"
systemctl restart docker
sleep 10

if systemctl is-active --quiet docker; then
    echo -e "${GREEN}✅ Docker 서비스 정상 작동${NC}"
else
    echo -e "${RED}❌ Docker 서비스 시작 실패${NC}"
    exit 1
fi

# ============================================================================
# 8. 테스트
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[8/8] 설치 테스트...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 테스트
echo -e "${YELLOW}   Docker 테스트 중...${NC}"
if docker run --rm hello-world > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker 정상 작동${NC}"
else
    echo -e "${RED}❌ Docker 테스트 실패${NC}"
fi

# GPU 테스트
if command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}   GPU 테스트 중...${NC}"
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
        echo -e "${GREEN}✅ GPU Docker 정상 작동${NC}"
    else
        echo -e "${YELLOW}⚠️  GPU 테스트 실패 (재시작 후 다시 시도)${NC}"
    fi
fi

# ============================================================================
# 완료
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ 모든 설치가 완료되었습니다!${NC}                                   ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📦 설치된 항목:${NC}"
echo -e "   ${CYAN}Docker:${NC}                $(docker --version)"
echo -e "   ${CYAN}Docker Compose:${NC}        $(docker compose version)"
if command -v nvidia-smi &> /dev/null; then
    echo -e "   ${CYAN}NVIDIA Driver:${NC}         $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
    echo -e "   ${CYAN}Container Toolkit:${NC}     설치됨"
fi
echo ""

echo -e "${MAGENTA}📝 다음 단계:${NC}"
echo ""
echo -e "${CYAN}# 1. 프로젝트 디렉토리로 이동${NC}"
echo -e "cd /workspace/5th_project_mvp/hint-system"
echo ""
echo -e "${CYAN}# 2. 서버 시작${NC}"
echo -e "bash runpod_docker_start.sh"
echo ""
echo -e "${CYAN}# 3. 웹 UI 접속${NC}"
echo -e "http://localhost:7860"
echo ""

echo -e "${MAGENTA}💡 유용한 명령어:${NC}"
echo -e "   ${CYAN}docker ps${NC}                      # 컨테이너 확인"
echo -e "   ${CYAN}bash runpod_docker_status.sh${NC}  # 상태 확인"
echo -e "   ${CYAN}bash runpod_docker_stop.sh${NC}    # 서버 중지"
if command -v nvidia-smi &> /dev/null; then
    echo -e "   ${CYAN}nvidia-smi${NC}                     # GPU 상태"
fi
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 설치 완료! 이제 vLLM 서버를 시작할 수 있습니다.${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
