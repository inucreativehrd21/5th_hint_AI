#!/bin/bash
# ============================================================================
# NVIDIA Docker Runtime 완전 설정 스크립트
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
echo -e "${CYAN}║${NC}  ${MAGENTA}🚀 NVIDIA Docker Runtime 완전 설정${NC}                              ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}RunPod 환경 최적화 버전${NC}                                      ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. GPU 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/6] GPU 환경 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ nvidia-smi를 찾을 수 없습니다.${NC}"
    echo -e "${RED}   NVIDIA GPU 드라이버가 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ NVIDIA GPU 드라이버 확인됨${NC}"
echo ""
nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv,noheader | while read line; do
    echo -e "${CYAN}   GPU: $line${NC}"
done
echo ""

# ============================================================================
# 2. NVIDIA Container Toolkit 설치
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/6] NVIDIA Container Toolkit 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# GPG 키 디렉토리 확인
if [ ! -d "/usr/share/keyrings" ]; then
    mkdir -p /usr/share/keyrings
fi

# NVIDIA Container Toolkit 저장소 추가
echo -e "${YELLOW}   저장소 설정 중...${NC}"

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

# GPG 키 다운로드
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# 저장소 목록 추가
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

echo -e "${YELLOW}   패키지 목록 업데이트 중...${NC}"
apt-get update -y

echo -e "${YELLOW}   NVIDIA Container Toolkit 설치 중...${NC}"
apt-get install -y nvidia-container-toolkit

echo -e "${GREEN}✅ NVIDIA Container Toolkit 설치 완료${NC}"

# ============================================================================
# 3. Docker 데몬 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/6] Docker 데몬 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 데몬 설정 디렉토리 생성
mkdir -p /etc/docker

# 기존 설정 백업
if [ -f /etc/docker/daemon.json ]; then
    echo -e "${YELLOW}   기존 daemon.json 백업 중...${NC}"
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)
fi

# NVIDIA Runtime 설정
echo -e "${YELLOW}   NVIDIA Runtime 설정 생성 중...${NC}"

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

echo -e "${GREEN}✅ Docker 데몬 설정 완료${NC}"

# ============================================================================
# 4. Docker 서비스 재시작
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/6] Docker 서비스 재시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   Docker 데몬 재시작 중... (10초 대기)${NC}"
systemctl restart docker

# 재시작 대기
sleep 10

if systemctl is-active --quiet docker; then
    echo -e "${GREEN}✅ Docker 서비스 정상 작동 중${NC}"
else
    echo -e "${RED}❌ Docker 서비스 시작 실패${NC}"
    echo -e "${YELLOW}   로그 확인: journalctl -xeu docker${NC}"
    exit 1
fi

# ============================================================================
# 5. NVIDIA Runtime 테스트
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/6] NVIDIA Runtime 테스트...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   Docker Runtime 확인 중...${NC}"
if docker info 2>/dev/null | grep -q "nvidia"; then
    echo -e "${GREEN}✅ NVIDIA Runtime이 기본 런타임으로 설정됨${NC}"
else
    echo -e "${RED}❌ NVIDIA Runtime 설정 확인 실패${NC}"
    echo -e "${YELLOW}   수동 확인 필요: docker info | grep -i runtime${NC}"
fi

echo ""
echo -e "${YELLOW}   GPU 접근 테스트 중... (이미지 다운로드 시 1-2분 소요)${NC}"

# CUDA 테스트 컨테이너 실행
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi > /tmp/gpu_test.log 2>&1; then
    echo -e "${GREEN}✅ GPU가 Docker 컨테이너에서 정상 작동!${NC}"
    echo ""
    echo -e "${CYAN}   GPU 테스트 결과:${NC}"
    cat /tmp/gpu_test.log | head -20
else
    echo -e "${RED}❌ GPU 테스트 실패${NC}"
    echo -e "${YELLOW}   오류 내용:${NC}"
    cat /tmp/gpu_test.log
    exit 1
fi

# ============================================================================
# 6. 추가 필수 패키지 설치
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/6] 추가 필수 패키지 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   시스템 유틸리티 설치 중...${NC}"
apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    tmux \
    jq \
    tree \
    ncdu

echo -e "${GREEN}✅ 필수 패키지 설치 완료${NC}"

# ============================================================================
# 완료 및 정보 출력
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ NVIDIA Docker Runtime 설정 완료!${NC}                             ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📊 설치된 구성:${NC}"
echo -e "   ${CYAN}Docker:${NC}                $(docker --version)"
echo -e "   ${CYAN}Docker Compose:${NC}        $(docker compose version)"
echo -e "   ${CYAN}NVIDIA Driver:${NC}         $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
echo -e "   ${CYAN}Container Toolkit:${NC}     $(nvidia-container-toolkit --version 2>/dev/null | head -1 || echo 'Installed')"
echo ""

echo -e "${MAGENTA}🎮 사용 가능한 GPU:${NC}"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read line; do
    echo -e "   ${GREEN}✓${NC} GPU $line"
done
echo ""

echo -e "${MAGENTA}🔧 Docker Runtime 설정:${NC}"
echo -e "   ${GREEN}✓${NC} Default Runtime: nvidia"
echo -e "   ${GREEN}✓${NC} GPU 자동 인식 활성화"
echo -e "   ${GREEN}✓${NC} 로그 관리 설정 완료"
echo ""

echo -e "${MAGENTA}📝 다음 단계:${NC}"
echo -e "   ${CYAN}cd /workspace/5th_project_mvp/hint-system${NC}"
echo -e "   ${CYAN}bash runpod_docker_start.sh${NC}"
echo ""

echo -e "${MAGENTA}💡 유용한 명령어:${NC}"
echo -e "   ${CYAN}docker info | grep -i runtime${NC}     # Runtime 확인"
echo -e "   ${CYAN}docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi${NC}"
echo -e "   ${CYAN}                                     # GPU 테스트${NC}"
echo -e "   ${CYAN}nvidia-smi${NC}                          # GPU 상태 확인"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 모든 설정이 완료되었습니다! 이제 vLLM 서버를 시작할 수 있습니다.${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
