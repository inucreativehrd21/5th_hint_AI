#!/bin/bash
# ============================================================================
# 시스템 검증 스크립트
# 모든 의존성, 임포트, 변수 등을 검증
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "======================================================================"
echo "  🔍 시스템 검증 스크립트"
echo "======================================================================"
echo ""

ERRORS=0
WARNINGS=0

# 1. Python 임포트 검증
echo -e "${BLUE}[1/6] Python 임포트 검증...${NC}"

cat > /tmp/test_imports.py << 'EOF'
import sys

errors = []
warnings = []

# 필수 임포트
required_imports = [
    'gradio',
    'openai',
    'requests',
    'json',
    'os',
    'sys',
    'time',
    'argparse',
]

# 선택적 임포트
optional_imports = [
    'dotenv',
    'pathlib',
]

print("필수 패키지 확인:")
for module in required_imports:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")
        errors.append(f"Missing required module: {module}")

print("\n선택적 패키지 확인:")
for module in optional_imports:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ⚠️  {module}: {e}")
        warnings.append(f"Missing optional module: {module}")

# app.py 임포트 테스트
print("\napp.py 모듈 임포트:")
sys.path.insert(0, '/app')
try:
    from config import Config
    print("  ✅ config.Config")
except ImportError as e:
    print(f"  ❌ config.Config: {e}")
    errors.append("Cannot import Config")

try:
    from models.model_inference import VLLMInference
    print("  ✅ models.model_inference.VLLMInference")
except ImportError as e:
    print(f"  ❌ models.model_inference.VLLMInference: {e}")
    errors.append("Cannot import VLLMInference")

print(f"\n에러: {len(errors)}, 경고: {len(warnings)}")
sys.exit(len(errors))
EOF

if docker-compose exec -T hint-app python /tmp/test_imports.py; then
    echo -e "${GREEN}✅ Python 임포트 검증 통과${NC}"
else
    echo -e "${RED}❌ Python 임포트 검증 실패${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 2. 환경 변수 검증
echo ""
echo -e "${BLUE}[2/6] 환경 변수 검증...${NC}"

check_env_var() {
    local var_name=$1
    local required=$2
    
    if docker-compose exec -T hint-app printenv "$var_name" > /dev/null 2>&1; then
        local value=$(docker-compose exec -T hint-app printenv "$var_name")
        echo -e "${GREEN}✅ $var_name: $value${NC}"
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ $var_name: 설정되지 않음 (필수)${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${YELLOW}⚠️  $var_name: 설정되지 않음 (선택)${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
}

check_env_var "VLLM_SERVER_URL" "true"
check_env_var "DATA_FILE_PATH" "true"
check_env_var "GRADIO_SERVER_NAME" "false"
check_env_var "GRADIO_SERVER_PORT" "false"
check_env_var "VLLM_MODEL" "false"

# 3. 데이터 파일 검증
echo ""
echo -e "${BLUE}[3/6] 데이터 파일 검증...${NC}"

if docker-compose exec -T hint-app test -f /app/data/problems_multi_solution.json; then
    echo -e "${GREEN}✅ problems_multi_solution.json 존재${NC}"
    
    # JSON 파싱 검증
    if docker-compose exec -T hint-app python -c "import json; json.load(open('/app/data/problems_multi_solution.json'))" 2>/dev/null; then
        echo -e "${GREEN}✅ JSON 파싱 성공${NC}"
    else
        echo -e "${RED}❌ JSON 파싱 실패${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ problems_multi_solution.json 없음${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 4. vLLM 서버 연결 검증
echo ""
echo -e "${BLUE}[4/6] vLLM 서버 연결 검증...${NC}"

if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ vLLM 헬스체크 통과${NC}"
    
    # 모델 API 확인
    if curl -s http://localhost:8000/v1/models > /dev/null; then
        echo -e "${GREEN}✅ vLLM 모델 API 접근 가능${NC}"
        echo "   모델 목록:"
        curl -s http://localhost:8000/v1/models | python -m json.tool 2>/dev/null | grep '"id"' | head -3
    else
        echo -e "${YELLOW}⚠️  vLLM 모델 API 접근 실패${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ vLLM 서버 연결 실패${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 5. Gradio 앱 연결 검증
echo ""
echo -e "${BLUE}[5/6] Gradio 앱 연결 검증...${NC}"

if curl -s http://localhost:7860/ > /dev/null; then
    echo -e "${GREEN}✅ Gradio 앱 접근 가능${NC}"
else
    echo -e "${RED}❌ Gradio 앱 연결 실패${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 6. 컨테이너 상태 검증
echo ""
echo -e "${BLUE}[6/6] 컨테이너 상태 검증...${NC}"

check_container() {
    local container=$1
    if docker-compose ps | grep -q "$container.*Up"; then
        echo -e "${GREEN}✅ $container: 실행 중${NC}"
    else
        echo -e "${RED}❌ $container: 중지됨 또는 오류${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

check_container "vllm-hint-server"
check_container "hint-gradio-app"

# 최종 결과
echo ""
echo "======================================================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 검증 완료: 모든 테스트 통과${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}   경고 ${WARNINGS}개 (선택 사항)${NC}"
    fi
    echo "======================================================================"
    exit 0
else
    echo -e "${RED}❌ 검증 실패: $ERRORS 개 오류, $WARNINGS 개 경고${NC}"
    echo "======================================================================"
    echo ""
    echo "🔧 문제 해결 방법:"
    echo "   1. 로그 확인: docker-compose logs"
    echo "   2. 재시작: docker-compose restart"
    echo "   3. 재빌드: docker-compose down && docker-compose up --build -d"
    exit 1
fi
