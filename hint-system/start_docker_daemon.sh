#!/bin/bash
# ============================================================================
# RunPod에서 Docker 데몬 수동 시작 스크립트
# ============================================================================

set -e

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
echo -e "${CYAN}║${NC}  ${MAGENTA}🐳 Docker 데몬 수동 시작 (RunPod)${NC}                               ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. 환경 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/5] 환경 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 실행 파일 확인
if ! command -v dockerd &> /dev/null; then
    echo -e "${RED}❌ dockerd를 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}   Docker가 설치되지 않았거나 PATH에 없습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ dockerd 실행 파일 확인됨: $(which dockerd)${NC}"

# 이미 실행 중인 Docker 데몬 확인
if pgrep -x "dockerd" > /dev/null; then
    echo -e "${YELLOW}⚠️  Docker 데몬이 이미 실행 중입니다.${NC}"
    
    # 소켓 확인
    if [ -S /var/run/docker.sock ]; then
        echo -e "${GREEN}✅ Docker 소켓 존재: /var/run/docker.sock${NC}"
        
        # 연결 테스트
        if docker ps > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Docker 연결 성공!${NC}"
            docker version
            echo ""
            echo -e "${GREEN}이미 Docker가 작동 중입니다. 서버를 시작하세요:${NC}"
            echo -e "${CYAN}bash runpod_docker_start.sh${NC}"
            exit 0
        fi
    fi
fi

# ============================================================================
# 2. 기존 Docker 프로세스 정리
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/5] 기존 프로세스 정리...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 기존 dockerd 프로세스 종료
if pgrep -x "dockerd" > /dev/null; then
    echo -e "${YELLOW}   기존 dockerd 프로세스 종료 중...${NC}"
    pkill -x dockerd || true
    sleep 2
fi

# 기존 소켓 제거
if [ -S /var/run/docker.sock ]; then
    echo -e "${YELLOW}   기존 Docker 소켓 제거 중...${NC}"
    rm -f /var/run/docker.sock
fi

echo -e "${GREEN}✅ 정리 완료${NC}"

# ============================================================================
# 3. 필요한 디렉토리 생성
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/5] Docker 디렉토리 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 필요한 디렉토리 생성
mkdir -p /var/run
mkdir -p /var/lib/docker
mkdir -p /etc/docker

echo -e "${GREEN}✅ 디렉토리 생성 완료${NC}"

# ============================================================================
# 4. Docker 데몬 시작
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/5] Docker 데몬 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 데몬 설정 파일 생성 (NVIDIA Runtime 포함)
if [ -f /etc/docker/daemon.json ]; then
    echo -e "${YELLOW}   기존 daemon.json 백업 중...${NC}"
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)
fi

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

echo -e "${GREEN}✅ daemon.json 생성 완료${NC}"

# Docker 데몬 백그라운드 실행
echo -e "${YELLOW}   Docker 데몬 시작 중... (10초 대기)${NC}"

# 로그 파일 준비
mkdir -p /tmp/docker-logs
DOCKER_LOG="/tmp/docker-logs/dockerd.log"

# dockerd 실행 (백그라운드)
nohup dockerd \
    --host=unix:///var/run/docker.sock \
    --data-root=/var/lib/docker \
    > "$DOCKER_LOG" 2>&1 &

DOCKERD_PID=$!
echo -e "${CYAN}   Docker 데몬 PID: $DOCKERD_PID${NC}"

# 시작 대기
for i in {1..20}; do
    if [ -S /var/run/docker.sock ]; then
        echo -e "${GREEN}✅ Docker 소켓 생성됨!${NC}"
        break
    fi
    sleep 0.5
    echo -n "."
done
echo ""

# ============================================================================
# 5. 연결 테스트
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/5] Docker 연결 테스트...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 소켓 권한 설정
if [ -S /var/run/docker.sock ]; then
    chmod 666 /var/run/docker.sock
    echo -e "${GREEN}✅ Docker 소켓 권한 설정 완료${NC}"
else
    echo -e "${RED}❌ Docker 소켓이 생성되지 않았습니다.${NC}"
    echo -e "${YELLOW}   로그 확인: cat $DOCKER_LOG${NC}"
    exit 1
fi

# 연결 테스트 (여러 번 시도)
echo -e "${YELLOW}   Docker 연결 테스트 중...${NC}"
CONNECTED=false
for i in {1..10}; do
    if docker info > /dev/null 2>&1; then
        CONNECTED=true
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

if [ "$CONNECTED" = true ]; then
    echo -e "${GREEN}✅ Docker 연결 성공!${NC}"
    echo ""
    docker version
    echo ""
    
    # GPU 테스트
    if command -v nvidia-smi &> /dev/null; then
        echo -e "${YELLOW}   GPU 접근 테스트 중...${NC}"
        if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
            echo -e "${GREEN}✅ GPU 접근 성공!${NC}"
        else
            echo -e "${YELLOW}⚠️  GPU 테스트 실패 (정상일 수 있음)${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Docker 연결 실패${NC}"
    echo ""
    echo -e "${YELLOW}Docker 데몬 로그:${NC}"
    tail -50 "$DOCKER_LOG"
    exit 1
fi

# ============================================================================
# 완료
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ Docker 데몬 시작 완료!${NC}                                        ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📊 Docker 정보:${NC}"
echo -e "   ${CYAN}데몬 PID:${NC}      $DOCKERD_PID"
echo -e "   ${CYAN}소켓:${NC}          /var/run/docker.sock"
echo -e "   ${CYAN}데이터 루트:${NC}   /var/lib/docker"
echo -e "   ${CYAN}로그 파일:${NC}     $DOCKER_LOG"
echo ""

echo -e "${MAGENTA}📝 다음 단계:${NC}"
echo -e "   ${CYAN}cd /workspace/5th_project_mvp/hint-system${NC}"
echo -e "   ${CYAN}bash runpod_docker_start.sh${NC}"
echo ""

echo -e "${MAGENTA}💡 유용한 명령어:${NC}"
echo -e "   ${CYAN}docker ps${NC}                  # 실행 중인 컨테이너"
echo -e "   ${CYAN}docker images${NC}              # 다운로드된 이미지"
echo -e "   ${CYAN}cat $DOCKER_LOG${NC}            # 데몬 로그 확인"
echo -e "   ${CYAN}kill $DOCKERD_PID${NC}          # Docker 데몬 종료"
echo ""

echo -e "${YELLOW}⚠️  주의: 이 터미널을 닫으면 Docker 데몬이 종료될 수 있습니다.${NC}"
echo -e "${YELLOW}   백그라운드에서 계속 실행되도록 nohup을 사용했습니다.${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 준비 완료! 이제 vLLM 서버를 시작할 수 있습니다.${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
