#!/bin/bash
# ============================================================================
# RunPod vLLM Docker 실행 스크립트 (멘토님 피드백 반영)
# DockerHub 공식 이미지 사용 - 다운로드만 하면 끝!
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}${MAGENTA}🚀 RunPod vLLM Docker 힌트 시스템${NC}                                  ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}DockerHub 공식 이미지 사용 (딸깍!)${NC}                               ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 환경 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/4] 환경 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    echo -e "${YELLOW}   RunPod PyTorch 템플릿에는 Docker가 없습니다.${NC}"
    echo -e "${YELLOW}   대신 run_python_direct.sh를 사용하세요!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose 설치 중...${NC}"
    pip install docker-compose -q
fi
echo -e "${GREEN}✅ Docker Compose 사용 가능${NC}"

# GPU 확인
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA GPU 확인됨${NC}"
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read line; do
        echo -e "${CYAN}   GPU: $line${NC}"
    done
else
    echo -e "${YELLOW}⚠️  GPU 없음 (CPU 모드)${NC}"
fi

# ============================================================================
# 프로젝트 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/4] 프로젝트 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd /workspace 2>/dev/null || cd ~

if [ ! -d "5th_project_mvp/hint-system" ]; then
    echo -e "${YELLOW}   프로젝트 클론 중...${NC}"
    git clone https://github.com/inucreativehrd21/5th_project_mvp.git
fi

cd 5th_project_mvp/hint-system
echo -e "${GREEN}✅ 작업 디렉토리: $(pwd)${NC}"

# .env 파일 생성
if [ ! -f .env ]; then
    echo -e "${YELLOW}   .env 파일 생성 중...${NC}"
    cat > .env <<'EOF'
# vLLM 서버 설정
VLLM_API_BASE=http://vllm-server:8000/v1
VLLM_MODEL_NAME=Qwen/Qwen2.5-Coder-7B-Instruct

# HuggingFace 토큰 (선택사항)
HF_TOKEN=

# 캐시 디렉토리
HF_HOME=/workspace/.cache/huggingface
EOF
    echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
fi

# ============================================================================
# Docker 이미지 다운로드
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/4] vLLM 공식 이미지 다운로드... (딸깍!)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}   📦 vllm/vllm-openai:latest 다운로드 중...${NC}"
docker pull vllm/vllm-openai:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ vLLM 이미지 다운로드 완료!${NC}"
else
    echo -e "${RED}❌ 이미지 다운로드 실패${NC}"
    exit 1
fi

# ============================================================================
# Docker Compose 실행
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/4] 서비스 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   기존 컨테이너 정리 중...${NC}"
docker-compose -f docker-compose.runpod.yml down 2>/dev/null || true

echo -e "${YELLOW}   Docker Compose 시작 중...${NC}"
docker-compose -f docker-compose.runpod.yml up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 서비스 시작 완료!${NC}"
else
    echo -e "${RED}❌ 서비스 시작 실패${NC}"
    exit 1
fi

# 서비스 준비 대기
echo ""
echo -e "${YELLOW}⏳ vLLM 서버 준비 대기 중... (모델 로딩 2-3분)${NC}"
for i in {1..60}; do
    if docker exec vllm-hint-server curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ vLLM 서버 준비 완료!${NC}"
        break
    fi
    sleep 5
    if [ $((i % 6)) -eq 0 ]; then
        echo -e "${CYAN}   $(($i * 5))초 경과...${NC}"
    fi
done

echo -e "${YELLOW}⏳ Gradio UI 준비 대기 중...${NC}"
sleep 10

# ============================================================================
# 완료
# ============================================================================
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}${GREEN}🎉 Docker 기반 실행 완료!${NC}                                           ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}🚀 실행 중인 서비스:${NC}"
docker-compose -f docker-compose.runpod.yml ps

echo ""
echo -e "${MAGENTA}🌐 접속 정보:${NC}"
echo -e "   ${CYAN}Gradio UI:${NC}    http://localhost:7860"
echo -e "   ${CYAN}vLLM API:${NC}     http://localhost:8000"
echo -e "   ${CYAN}Health:${NC}       http://localhost:8000/health"
echo ""

echo -e "${MAGENTA}📝 로그 확인:${NC}"
echo -e "   ${CYAN}docker-compose -f docker-compose.runpod.yml logs -f vllm-server${NC}"
echo -e "   ${CYAN}docker-compose -f docker-compose.runpod.yml logs -f gradio-ui${NC}"
echo ""

echo -e "${MAGENTA}🛑 서비스 중지:${NC}"
echo -e "   ${CYAN}docker-compose -f docker-compose.runpod.yml down${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ 준비 완료! Gradio UI에 접속하세요! ✨${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
