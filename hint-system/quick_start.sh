#!/bin/bash
# ============================================================================
# RunPod 배포 빠른 시작 스크립트
# vLLM Docker 기반 힌트 생성 시스템 자동 배포
# ============================================================================

set -e  # 에러 발생 시 즉시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로고 출력
echo ""
echo "======================================================================"
echo "  🚀 vLLM Docker 기반 힌트 생성 시스템 - 자동 배포"
echo "======================================================================"
echo ""

# 1. 환경 확인
echo -e "${BLUE}[1/7] 환경 확인...${NC}"

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    echo "   apt-get update && apt-get install -y docker.io"
    exit 1
fi
echo -e "${GREEN}✅ Docker 설치됨: $(docker --version)${NC}"

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose 없음. 설치 중...${NC}"
    apt-get update
    apt-get install -y docker-compose-plugin
fi
echo -e "${GREEN}✅ Docker Compose 설치됨${NC}"

# NVIDIA GPU 확인
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA GPU 드라이버가 없습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ GPU 감지됨:${NC}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# 2. 환경 변수 설정
echo ""
echo -e "${BLUE}[2/7] 환경 변수 설정...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일 없음. .env.example에서 복사 중...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env 파일 생성됨${NC}"
    echo -e "${YELLOW}   필요시 .env 파일을 수정하세요.${NC}"
else
    echo -e "${GREEN}✅ .env 파일 존재${NC}"
fi

# 환경 변수 로드
source .env

# 3. 데이터 파일 확인
echo ""
echo -e "${BLUE}[3/7] 데이터 파일 확인...${NC}"

DATA_FILE="data/problems_multi_solution.json"
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}❌ 데이터 파일 없음: $DATA_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 데이터 파일 존재: $DATA_FILE${NC}"

# 4. vLLM Docker 이미지 다운로드
echo ""
echo -e "${BLUE}[4/7] vLLM Docker 이미지 다운로드...${NC}"
echo -e "${YELLOW}   (처음 실행 시 10~15분 소요)${NC}"

docker pull vllm/vllm-openai:latest
echo -e "${GREEN}✅ vLLM 이미지 다운로드 완료${NC}"

# 5. Gradio 앱 빌드
echo ""
echo -e "${BLUE}[5/7] Gradio 앱 Docker 이미지 빌드...${NC}"

docker-compose build hint-app
echo -e "${GREEN}✅ Gradio 앱 빌드 완료${NC}"

# 6. 시스템 시작
echo ""
echo -e "${BLUE}[6/7] 시스템 시작...${NC}"

docker-compose up -d
echo -e "${GREEN}✅ 컨테이너 시작됨${NC}"

# 7. 상태 확인
echo ""
echo -e "${BLUE}[7/7] 시스템 상태 확인...${NC}"
sleep 5

# vLLM 서버 헬스체크 대기
echo -e "${YELLOW}   vLLM 서버 시작 대기 중... (최대 5분)${NC}"
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ vLLM 서버 준비 완료${NC}"
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

# Gradio 앱 확인
if curl -s http://localhost:7860/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Gradio 앱 실행 중${NC}"
else
    echo -e "${YELLOW}⚠️  Gradio 앱 아직 준비 중...${NC}"
fi

# 컨테이너 상태 출력
echo ""
echo -e "${BLUE}컨테이너 상태:${NC}"
docker-compose ps

# 완료 메시지
echo ""
echo "======================================================================"
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo "======================================================================"
echo ""
echo "📊 접속 정보:"
echo "   - Gradio UI: http://localhost:7860"
echo "   - vLLM API: http://localhost:8000/v1"
echo ""
echo "📝 유용한 명령어:"
echo "   - 로그 확인: docker-compose logs -f"
echo "   - vLLM 로그: docker-compose logs -f vllm-server"
echo "   - 앱 로그: docker-compose logs -f hint-app"
echo "   - 재시작: docker-compose restart"
echo "   - 중지: docker-compose down"
echo ""
echo "🌐 RunPod 환경에서는 포트 7860을 외부에 노출하세요."
echo ""
