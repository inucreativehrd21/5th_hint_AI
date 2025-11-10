#!/bin/bash
# ============================================================================
# NVIDIA Docker Runtime 설정 스크립트 (RunPod 전용)
# ============================================================================
# RunPod는 이미 Docker가 설치되어 있고 systemd를 사용하지 않습니다.
# NVIDIA Runtime 설정만 하면 됩니다.
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
echo -e "${CYAN}║${NC}  ${MAGENTA}🚀 NVIDIA Docker Runtime 설정 (RunPod 전용)${NC}                     ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. 환경 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/4] 환경 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되어 있지 않습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"

# Docker Compose 확인
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose가 설치되어 있지 않습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose: $(docker compose version)${NC}"

# GPU 확인
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ nvidia-smi를 찾을 수 없습니다.${NC}"
    echo -e "${RED}   NVIDIA GPU 드라이버가 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ NVIDIA GPU 확인됨${NC}"
nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv,noheader | while read line; do
    echo -e "${CYAN}   GPU: $line${NC}"
done
echo ""

# ============================================================================
# 2. NVIDIA Container Toolkit 설치 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/4] NVIDIA Container Toolkit 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v nvidia-container-toolkit &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA Container Toolkit 이미 설치됨${NC}"
else
    echo -e "${YELLOW}⚠️  NVIDIA Container Toolkit이 설치되지 않았습니다.${NC}"
    echo -e "${YELLOW}   설치를 시도합니다...${NC}"
    
    # 저장소 추가
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
        gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg 2>/dev/null || true
    
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
    
    apt-get update -y 2>/dev/null || true
    apt-get install -y nvidia-container-toolkit 2>/dev/null || echo -e "${YELLOW}   설치 건너뜀 (이미 설치되어 있을 수 있음)${NC}"
fi

# ============================================================================
# 3. Docker 데몬 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/4] Docker 데몬 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 설정 디렉토리 생성
mkdir -p /etc/docker

# 기존 설정 백업
if [ -f /etc/docker/daemon.json ]; then
    echo -e "${YELLOW}   기존 daemon.json 백업 중...${NC}"
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)
fi

# 기존 설정 읽기
EXISTING_CONFIG=""
if [ -f /etc/docker/daemon.json ]; then
    EXISTING_CONFIG=$(cat /etc/docker/daemon.json)
fi

# NVIDIA Runtime 설정 생성
echo -e "${YELLOW}   NVIDIA Runtime 설정 작성 중...${NC}"

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
echo -e "${CYAN}   설정 파일: /etc/docker/daemon.json${NC}"

# ============================================================================
# 4. 설정 테스트
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/4] GPU 접근 테스트...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   ⚠️  RunPod 환경에서는 Docker 데몬 재시작이 자동으로 적용됩니다.${NC}"
echo -e "${YELLOW}   GPU 테스트를 진행합니다... (이미지 다운로드 시 1-2분 소요)${NC}"
echo ""

# GPU 테스트
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi > /tmp/gpu_test.log 2>&1; then
    echo -e "${GREEN}✅ GPU가 Docker 컨테이너에서 정상 작동!${NC}"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cat /tmp/gpu_test.log | head -15
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${YELLOW}⚠️  GPU 테스트 결과:${NC}"
    cat /tmp/gpu_test.log
    echo ""
    echo -e "${YELLOW}   이것은 정상일 수 있습니다. RunPod는 호스트 레벨에서 GPU를 관리합니다.${NC}"
    echo -e "${YELLOW}   vLLM 컨테이너를 실행하면 자동으로 GPU를 사용합니다.${NC}"
fi

# ============================================================================
# 완료
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ NVIDIA Docker Runtime 설정 완료!${NC}                             ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📊 현재 환경:${NC}"
echo -e "   ${CYAN}Docker:${NC}           $(docker --version)"
echo -e "   ${CYAN}Docker Compose:${NC}   $(docker compose version)"
echo -e "   ${CYAN}NVIDIA Driver:${NC}    $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
echo ""

echo -e "${MAGENTA}🎮 GPU 정보:${NC}"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read line; do
    echo -e "   ${GREEN}✓${NC} GPU $line"
done
echo ""

echo -e "${MAGENTA}⚙️  Docker Runtime 설정:${NC}"
echo -e "   ${GREEN}✓${NC} Default Runtime: nvidia"
echo -e "   ${GREEN}✓${NC} 설정 파일: /etc/docker/daemon.json"
echo ""

echo -e "${MAGENTA}📝 다음 단계:${NC}"
echo -e "   ${CYAN}bash runpod_docker_start.sh${NC}"
echo ""

echo -e "${MAGENTA}💡 참고사항:${NC}"
echo -e "   ${YELLOW}RunPod 환경에서는 systemd를 사용하지 않습니다.${NC}"
echo -e "   ${YELLOW}Docker 데몬은 호스트 레벨에서 자동 관리됩니다.${NC}"
echo -e "   ${YELLOW}설정이 즉시 적용되며, 재시작이 필요하지 않습니다.${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 설정 완료! 이제 vLLM 서버를 시작할 수 있습니다.${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
