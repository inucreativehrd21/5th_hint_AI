#!/bin/bash
# ============================================================================
# RunPod vLLM Docker 간편 실행 스크립트
# Docker 이미지 기반 - 설치 없이 바로 실행!
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
echo -e "${CYAN}║${NC}  ${MAGENTA}🚀 AI 코딩 힌트 시스템 - Docker 기반 간편 실행${NC}                  ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}vLLM 공식 이미지 사용 - 설치 없이 바로 시작!${NC}                  ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 작업 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# 1. 환경 확인
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/5] 환경 확인 중...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    echo -e "${YELLOW}   설치: curl -fsSL https://get.docker.com | sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"

# Docker Compose 확인
if ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose가 없습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose: $(docker compose version)${NC}"

# NVIDIA Docker Runtime 확인
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA Docker Runtime이 설정되지 않았습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ NVIDIA Docker Runtime 설정됨${NC}"

# GPU 정보
echo -e "${GREEN}✅ GPU 정보:${NC}"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while IFS=',' read -r idx name memory; do
    echo -e "   ${CYAN}GPU $idx:${NC} $name (VRAM: $memory)"
done

# ============================================================================
# 2. 환경 변수 설정
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/5] 환경 변수 설정...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일 없음. 기본값으로 생성...${NC}"
    cat > .env << 'EOF'
# vLLM 모델 설정
VLLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
VLLM_GPU_MEMORY_UTILIZATION=0.85
VLLM_MAX_MODEL_LEN=4096
VLLM_TENSOR_PARALLEL_SIZE=1
VLLM_DTYPE=auto

# Gradio 포트
GRADIO_PORT=7860

# 기타
DEFAULT_TEMPERATURE=0.7
HUGGING_FACE_HUB_TOKEN=
EOF
    echo -e "${GREEN}✅ .env 파일 생성됨${NC}"
else
    echo -e "${GREEN}✅ .env 파일 존재${NC}"
fi

# 환경 변수 로드
export $(grep -v '^#' .env | xargs)

echo -e "${CYAN}📋 설정:${NC}"
echo -e "   ${CYAN}모델:${NC} ${VLLM_MODEL}"
echo -e "   ${CYAN}GPU 메모리:${NC} ${VLLM_GPU_MEMORY_UTILIZATION}"
echo -e "   ${CYAN}최대 토큰:${NC} ${VLLM_MAX_MODEL_LEN}"

# ============================================================================
# 3. 데이터 파일 확인
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/5] 데이터 파일 확인...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f "data/problems_multi_solution.json" ]; then
    echo -e "${RED}❌ data/problems_multi_solution.json 파일이 없습니다.${NC}"
    exit 1
fi

FILE_SIZE=$(du -h data/problems_multi_solution.json | cut -f1)
echo -e "${GREEN}✅ 데이터 파일 존재 (크기: $FILE_SIZE)${NC}"

# ============================================================================
# 4. 기존 컨테이너 정리
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/5] 기존 컨테이너 정리...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 기존 컨테이너 중지 및 제거
if docker compose ps | grep -q "Up"; then
    echo -e "${YELLOW}   기존 컨테이너 중지 중...${NC}"
    docker compose down
    echo -e "${GREEN}✅ 기존 컨테이너 정리 완료${NC}"
else
    echo -e "${GREEN}✅ 실행 중인 컨테이너 없음${NC}"
fi

# ============================================================================
# 5. Docker Compose 실행
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/5] 시스템 시작 중...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}   Docker 이미지 다운로드 중... (첫 실행 시 5-10분 소요)${NC}"
echo -e "${YELLOW}   vLLM 모델 로딩 중... (첫 실행 시 추가 3-5분)${NC}"
echo ""

# Docker Compose 실행 (detached mode)
docker compose up -d

echo ""
echo -e "${GREEN}✅ 컨테이너 시작됨${NC}"
echo ""

# 컨테이너 상태 확인
echo -e "${CYAN}📊 컨테이너 상태:${NC}"
docker compose ps

# ============================================================================
# 헬스체크 대기
# ============================================================================
echo ""
echo -e "${YELLOW}⏳ vLLM 서버 준비 대기 중... (최대 5분)${NC}"

for i in {1..60}; do
    if docker compose exec -T vllm-server curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ vLLM 서버 준비 완료!${NC}"
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

# Gradio 앱 확인
echo -e "${YELLOW}⏳ Gradio 앱 확인 중...${NC}"
sleep 5

if curl -sf http://localhost:${GRADIO_PORT:-7860}/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Gradio 앱 실행 중!${NC}"
else
    echo -e "${YELLOW}⚠️  Gradio 앱 아직 준비 중... (1-2분 소요)${NC}"
fi

# ============================================================================
# 완료 메시지
# ============================================================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✅ 배포 완료! 시스템이 실행 중입니다.${NC}                            ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📊 접속 정보:${NC}"
echo -e "   ${CYAN}🌐 Gradio UI:${NC}       http://localhost:${GRADIO_PORT:-7860}"
echo -e "   ${CYAN}🚀 vLLM API:${NC}        http://localhost:8000/v1"
echo -e "   ${CYAN}❤️  Health Check:${NC}   http://localhost:8000/health"
echo -e "   ${CYAN}📚 API Docs:${NC}        http://localhost:8000/docs"
echo ""

# RunPod 외부 접속 정보
if [ -n "$RUNPOD_POD_ID" ]; then
    echo -e "${MAGENTA}🌍 RunPod 외부 접속:${NC}"
    echo -e "   ${CYAN}RunPod 대시보드에서 포트 ${GRADIO_PORT:-7860}을 노출하세요.${NC}"
    echo ""
fi

echo -e "${MAGENTA}📝 유용한 명령어:${NC}"
echo -e "   ${CYAN}로그 확인:${NC}              docker compose logs -f"
echo -e "   ${CYAN}vLLM 로그:${NC}              docker compose logs -f vllm-server"
echo -e "   ${CYAN}Gradio 로그:${NC}            docker compose logs -f hint-app"
echo -e "   ${CYAN}컨테이너 상태:${NC}          docker compose ps"
echo -e "   ${CYAN}시스템 중지:${NC}            docker compose down"
echo -e "   ${CYAN}시스템 재시작:${NC}          docker compose restart"
echo ""

echo -e "${MAGENTA}🎮 GPU 모니터링:${NC}"
echo -e "   ${CYAN}nvidia-smi -l 1${NC}         # 1초마다 GPU 상태 확인"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 시스템이 성공적으로 시작되었습니다!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
