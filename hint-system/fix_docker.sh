#!/bin/bash
# ============================================================================
# RunPod Docker 문제 해결 스크립트
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${YELLOW}⚠️  RunPod Docker 문제 해결${NC}                                       ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Docker 소켓 권한 확인${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -S /var/run/docker.sock ]; then
    echo -e "${GREEN}✅ Docker 소켓 존재: /var/run/docker.sock${NC}"
    ls -la /var/run/docker.sock
    
    # 권한 확인
    if [ -r /var/run/docker.sock ] && [ -w /var/run/docker.sock ]; then
        echo -e "${GREEN}✅ 현재 사용자가 Docker 소켓에 접근 가능${NC}"
    else
        echo -e "${YELLOW}⚠️  권한 부족. 권한 부여 중...${NC}"
        sudo chmod 666 /var/run/docker.sock
        echo -e "${GREEN}✅ 권한 부여 완료${NC}"
    fi
else
    echo -e "${RED}❌ Docker 소켓이 없습니다: /var/run/docker.sock${NC}"
    echo ""
    echo -e "${YELLOW}가능한 원인:${NC}"
    echo -e "  1. Docker 데몬이 실행되지 않음"
    echo -e "  2. RunPod가 Docker-in-Docker를 지원하지 않음"
    echo -e "  3. 다른 소켓 경로 사용 중"
    echo ""
    
    # 대안 경로 확인
    for socket_path in /run/docker.sock /host/var/run/docker.sock; do
        if [ -S "$socket_path" ]; then
            echo -e "${GREEN}✅ 대안 소켓 발견: $socket_path${NC}"
            export DOCKER_HOST="unix://$socket_path"
            echo -e "${CYAN}환경 변수 설정: DOCKER_HOST=$DOCKER_HOST${NC}"
        fi
    done
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Docker 연결 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker 연결 성공!${NC}"
    echo ""
    docker version --format '{{.Server.Version}}'
else
    echo -e "${RED}❌ Docker 연결 실패${NC}"
    echo ""
    echo -e "${YELLOW}오류 내용:${NC}"
    docker ps 2>&1 | head -5
    echo ""
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🔧 해결 방법:${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    echo -e "${MAGENTA}방법 1: Docker 소켓 권한 부여${NC}"
    echo -e "${CYAN}sudo chmod 666 /var/run/docker.sock${NC}"
    echo ""
    
    echo -e "${MAGENTA}방법 2: 현재 사용자를 docker 그룹에 추가${NC}"
    echo -e "${CYAN}sudo usermod -aG docker \$USER${NC}"
    echo -e "${CYAN}newgrp docker${NC}"
    echo ""
    
    echo -e "${MAGENTA}방법 3: Docker 데몬 시작 (일반 Linux)${NC}"
    echo -e "${CYAN}sudo systemctl start docker${NC}"
    echo ""
    
    echo -e "${MAGENTA}방법 4: Docker 서비스 시작 (Docker Desktop)${NC}"
    echo -e "${CYAN}systemctl --user start docker-desktop${NC}"
    echo ""
    
    echo -e "${RED}⚠️  중요: RunPod는 Docker-in-Docker를 기본적으로 지원하지 않을 수 있습니다.${NC}"
    echo -e "${YELLOW}대안: RunPod Pod 생성 시 'Expose Docker Socket' 옵션 활성화 필요${NC}"
    echo ""
    
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Docker Compose 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if docker compose version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose 사용 가능${NC}"
    docker compose version
else
    echo -e "${RED}❌ Docker Compose 없음${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✅ Docker 환경 정상!${NC}                                              ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}이제 다음 명령어로 서버를 시작하세요:${NC}"
echo -e "${YELLOW}bash runpod_docker_start.sh${NC}"
echo ""
