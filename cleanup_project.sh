#!/bin/bash
# ============================================================================
# 프로젝트 정리 스크립트
# 불필요한 파일 및 중복 문서 정리
# ============================================================================

set -e

echo "🧹 프로젝트 정리 시작..."
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 삭제할 파일 목록
FILES_TO_DELETE=(
    # hint-system: 구버전 파일들
    "hint-system/app_old.py"
    "hint-system/app_vllm.py"
    "hint-system/vllm_server.py"
    "hint-system/start_vllm.bat"
    "hint-system/test_imports.py"
    "hint-system/test_vllm_integration.py"
    "hint-system/test_runpod.sh"
    "hint-system/deploy_runpod.sh"
    "hint-system/pre_deployment_check.sh"
    "hint-system/install_dependencies.sh"
    
    # hint-system: 중복 README
    "hint-system/README.md"
    
    # 루트: 중복/구버전 문서들
    "DEPLOYMENT_SUMMARY.md"
    "FINAL_DEPLOYMENT_READY.md"
    "RUNPOD_DEPLOYMENT_FINAL.md"
    "RUNPOD_QUICKSTART.md"
    "SETUP_GUIDE.md"
    "UPLOAD_READY.md"
    
    # 루트: 불필요한 설정 파일
    ".env.example"
    "config.py"
)

# 디렉토리 삭제 목록
DIRS_TO_DELETE=(
    "hint-system/pyairports"
    "hint-system/__pycache__"
    "hint-system/models/__pycache__"
    "__pycache__"
    "logs"
)

# 파일 삭제
echo -e "${YELLOW}📄 불필요한 파일 삭제 중...${NC}"
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  🗑️  삭제: $file"
        rm "$file"
    else
        echo "  ⚠️  없음: $file"
    fi
done

echo ""
echo -e "${YELLOW}📁 불필요한 디렉토리 삭제 중...${NC}"
for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        echo "  🗑️  삭제: $dir"
        rm -rf "$dir"
    else
        echo "  ⚠️  없음: $dir"
    fi
done

echo ""
echo -e "${GREEN}✅ 정리 완료!${NC}"
echo ""
echo "📁 정리된 프로젝트 구조:"
echo ""
tree -L 2 -I 'venv|__pycache__|.git|node_modules' .

echo ""
echo "📝 다음 단계:"
echo "  1. git status로 변경 사항 확인"
echo "  2. git add -A로 변경 사항 스테이징"
echo "  3. git commit -m 'chore: 프로젝트 정리 - 불필요한 파일 제거'"
