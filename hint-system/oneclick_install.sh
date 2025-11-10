#!/bin/bash
# ============================================================================
# 🚀 RunPod vLLM 힌트 시스템 - 올인원 자동 설치 스크립트
# ============================================================================
# 이 스크립트 하나로 모든 것을 설치하고 배포합니다!
# 
# 기능:
# 1. Docker 설치 (없으면)
# 2. NVIDIA Container Toolkit 설치
# 3. Docker 데몬 시작 (필요시)
# 4. NVIDIA Runtime 설정
# 5. 프로젝트 클론 (없으면)
# 6. vLLM 서버 시작
# 7. Gradio UI 시작
#
# 사용법:
#   bash oneclick_install.sh
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# 로그 파일
LOG_FILE="/tmp/runpod_install_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}${MAGENTA}🚀 RunPod vLLM 힌트 시스템 - 올인원 자동 설치${NC}                     ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}Docker 설치부터 서버 배포까지 한 번에!${NC}                           ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⏱️  예상 소요 시간: 10-15분${NC}"
echo -e "${YELLOW}📝 로그 파일: $LOG_FILE${NC}"
echo ""
sleep 2

# ============================================================================
# 단계 1: 환경 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/7] 환경 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

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
    echo -e "${GREEN}✅ NVIDIA GPU 확인됨${NC}"
    nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader | while read line; do
        echo -e "${CYAN}   GPU: $line${NC}"
    done
else
    echo -e "${YELLOW}⚠️  nvidia-smi를 찾을 수 없습니다. GPU 없이 진행합니다.${NC}"
fi

# Root 권한 확인
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  root 권한이 필요합니다. sudo로 재실행 중...${NC}"
    exec sudo bash "$0" "$@"
    exit $?
fi

echo -e "${GREEN}✅ 환경 확인 완료${NC}"
sleep 1

# ============================================================================
# 단계 2: Docker 설치
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/7] Docker 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker 이미 설치됨: $(docker --version)${NC}"
else
    echo -e "${YELLOW}   Docker 설치 중... (3-5분 소요)${NC}"
    
    # 기존 Docker 제거
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # 의존성 설치
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    # Docker GPG 키 추가
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Docker 저장소 추가
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Docker 설치
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    echo -e "${GREEN}✅ Docker 설치 완료: $(docker --version)${NC}"
fi

# Docker Compose 확인
if command -v docker compose &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose 확인됨: $(docker compose version)${NC}"
else
    echo -e "${RED}❌ Docker Compose가 없습니다.${NC}"
    exit 1
fi

sleep 1

# ============================================================================
# 단계 3: NVIDIA Container Toolkit 설치
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/7] NVIDIA Container Toolkit 설치...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v nvidia-smi &> /dev/null; then
    if command -v nvidia-container-toolkit &> /dev/null; then
        echo -e "${GREEN}✅ NVIDIA Container Toolkit 이미 설치됨${NC}"
    else
        echo -e "${YELLOW}   NVIDIA Container Toolkit 설치 중...${NC}"
        
        # 저장소 추가
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
            gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg 2>/dev/null || true
        
        curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
        
        apt-get update -y
        apt-get install -y nvidia-container-toolkit
        
        echo -e "${GREEN}✅ NVIDIA Container Toolkit 설치 완료${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  NVIDIA GPU 없음, 건너뜁니다.${NC}"
fi

sleep 1

# ============================================================================
# 단계 4: Docker 데몬 설정 및 시작
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/7] Docker 데몬 설정 및 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 소켓 확인
if [ -S /var/run/docker.sock ]; then
    echo -e "${GREEN}✅ Docker 소켓 이미 존재함${NC}"
    
    # 연결 테스트
    if docker ps > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker 데몬 정상 작동 중${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker 데몬 연결 실패, 재시작 시도 중...${NC}"
        systemctl restart docker 2>/dev/null || dockerd > /tmp/dockerd.log 2>&1 &
        sleep 5
    fi
else
    echo -e "${YELLOW}   Docker 소켓 없음, 데몬 시작 중...${NC}"
    
    # 디렉토리 생성
    mkdir -p /var/run /var/lib/docker /etc/docker
    
    # daemon.json 생성
    if command -v nvidia-smi &> /dev/null; then
        cat > /etc/docker/daemon.json <<'EOF'
{
    "data-root": "/var/lib/docker",
    "storage-driver": "overlay2",
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
        cat > /etc/docker/daemon.json <<'EOF'
{
    "data-root": "/var/lib/docker",
    "storage-driver": "overlay2",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
    fi
    
    # Docker 데몬 시작
    if systemctl is-active --quiet docker 2>/dev/null; then
        systemctl restart docker
    else
        # systemd 없으면 직접 시작
        nohup dockerd --host=unix:///var/run/docker.sock > /tmp/dockerd.log 2>&1 &
    fi
    
    # 시작 대기
    echo -e "${YELLOW}   Docker 데몬 시작 대기 중...${NC}"
    for i in {1..30}; do
        if [ -S /var/run/docker.sock ]; then
            chmod 666 /var/run/docker.sock
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # 연결 테스트
    sleep 3
    if docker ps > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker 데몬 시작 완료${NC}"
    else
        echo -e "${RED}❌ Docker 데몬 시작 실패${NC}"
        echo -e "${YELLOW}   로그: cat /tmp/dockerd.log${NC}"
        exit 1
    fi
fi

sleep 1

# ============================================================================
# 단계 5: 프로젝트 클론
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/7] 프로젝트 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 작업 디렉토리 이동
cd /workspace 2>/dev/null || cd ~

# 프로젝트 디렉토리 확인
if [ -d "5th_project_mvp/hint-system" ]; then
    echo -e "${GREEN}✅ 프로젝트 디렉토리 이미 존재함${NC}"
    cd 5th_project_mvp/hint-system
    
    # Git pull 시도
    if [ -d ".git" ]; then
        echo -e "${YELLOW}   최신 코드 업데이트 중...${NC}"
        git pull origin main 2>/dev/null || echo -e "${YELLOW}   업데이트 건너뜀${NC}"
    fi
else
    echo -e "${YELLOW}   프로젝트 클론 중...${NC}"
    git clone https://github.com/inucreativehrd21/5th_project_mvp.git
    cd 5th_project_mvp/hint-system
    echo -e "${GREEN}✅ 프로젝트 클론 완료${NC}"
fi

# 실행 권한 부여
chmod +x *.sh 2>/dev/null || true

sleep 1

# ============================================================================
# 단계 6: 환경 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/7] 환경 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# .env 파일 생성
if [ ! -f .env ]; then
    echo -e "${YELLOW}   .env 파일 생성 중...${NC}"
    cat > .env <<'EOF'
# vLLM 모델 설정
VLLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
VLLM_GPU_MEMORY_UTILIZATION=0.85
VLLM_MAX_MODEL_LEN=4096
VLLM_TENSOR_PARALLEL_SIZE=1

# API 설정
VLLM_API_BASE=http://vllm-server:8000/v1
VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct

# GPU 설정
CUDA_VISIBLE_DEVICES=0

# 로깅
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
else
    echo -e "${GREEN}✅ .env 파일 이미 존재함${NC}"
fi

# 데이터 파일 확인
if [ -f "data/problems_multi_solution.json" ]; then
    FILE_SIZE=$(du -h "data/problems_multi_solution.json" | cut -f1)
    echo -e "${GREEN}✅ 데이터 파일 확인됨: problems_multi_solution.json ($FILE_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠️  데이터 파일이 없습니다. 서버 시작 후 업로드 필요${NC}"
fi

sleep 1

# ============================================================================
# 단계 7: 서버 시작
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[7/7] vLLM 서버 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 기존 컨테이너 정리
echo -e "${YELLOW}   기존 컨테이너 정리 중...${NC}"
docker compose down 2>/dev/null || true

# Docker Compose 시작
echo -e "${YELLOW}   Docker Compose로 시스템 시작 중...${NC}"
echo -e "${CYAN}   - vLLM 서버 (포트 8000)${NC}"
echo -e "${CYAN}   - Gradio UI (포트 7860)${NC}"
echo ""

docker compose up -d

# 서비스 시작 대기
echo -e "${YELLOW}   서비스 시작 대기 중...${NC}"
sleep 10

# vLLM 서버 준비 대기
echo -e "${YELLOW}   vLLM 서버 준비 대기 중... (모델 로딩 2-3분 소요)${NC}"
VLLM_READY=false
for i in {1..60}; do
    if docker compose exec -T vllm-server curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        VLLM_READY=true
        break
    fi
    sleep 5
    echo -n "."
done
echo ""

if [ "$VLLM_READY" = true ]; then
    echo -e "${GREEN}✅ vLLM 서버 준비 완료!${NC}"
else
    echo -e "${YELLOW}⚠️  vLLM 서버 준비 시간 초과 (백그라운드에서 계속 로딩 중)${NC}"
fi

# Gradio UI 확인
if curl -sf http://localhost:7860 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Gradio UI 준비 완료!${NC}"
else
    echo -e "${YELLOW}⚠️  Gradio UI 준비 중...${NC}"
fi

sleep 2

# ============================================================================
# 완료
# ============================================================================
clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}${GREEN}🎉 설치 및 배포 완료!${NC}                                                 ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📊 설치된 구성:${NC}"
echo -e "   ${CYAN}Docker:${NC}                $(docker --version)"
echo -e "   ${CYAN}Docker Compose:${NC}        $(docker compose version)"
if command -v nvidia-smi &> /dev/null; then
    echo -e "   ${CYAN}NVIDIA Driver:${NC}         $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
    echo -e "   ${CYAN}Container Toolkit:${NC}     설치됨"
fi
echo ""

echo -e "${MAGENTA}🎮 GPU 정보:${NC}"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read line; do
        echo -e "   ${GREEN}✓${NC} GPU $line"
    done
else
    echo -e "   ${YELLOW}GPU 없음 (CPU 모드)${NC}"
fi
echo ""

echo -e "${MAGENTA}🚀 실행 중인 서비스:${NC}"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${MAGENTA}🌐 접속 정보:${NC}"
echo -e "   ${CYAN}Gradio UI:${NC}        http://localhost:7860"
echo -e "   ${CYAN}vLLM API:${NC}         http://localhost:8000"
echo -e "   ${CYAN}Health Check:${NC}     http://localhost:8000/health"
echo ""

echo -e "${MAGENTA}💡 유용한 명령어:${NC}"
echo -e "   ${CYAN}docker compose ps${NC}                  # 컨테이너 상태 확인"
echo -e "   ${CYAN}docker compose logs -f${NC}             # 실시간 로그 확인"
echo -e "   ${CYAN}docker compose logs vllm-server${NC}    # vLLM 로그만 보기"
echo -e "   ${CYAN}docker compose stop${NC}                # 서비스 중지"
echo -e "   ${CYAN}docker compose restart${NC}             # 서비스 재시작"
if command -v nvidia-smi &> /dev/null; then
    echo -e "   ${CYAN}nvidia-smi${NC}                         # GPU 상태 확인"
fi
echo ""

echo -e "${MAGENTA}📝 다음 단계:${NC}"
echo -e "   1. ${CYAN}http://localhost:7860${NC} 접속"
echo -e "   2. 백준 문제 번호 입력 (예: 1000)"
echo -e "   3. 힌트 생성 버튼 클릭"
echo -e "   4. AI 생성 힌트 확인!"
echo ""

echo -e "${MAGENTA}🔧 RunPod 포트 노출:${NC}"
echo -e "   RunPod 웹사이트에서 포트 노출 필요:"
echo -e "   - 포트 ${CYAN}7860${NC} (Gradio UI)"
echo -e "   - 포트 ${CYAN}8000${NC} (vLLM API)"
echo ""

echo -e "${YELLOW}📋 로그 파일: $LOG_FILE${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}✨ 모든 준비가 완료되었습니다! 즐거운 코딩 되세요! ✨${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
