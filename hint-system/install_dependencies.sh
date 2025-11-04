#!/bin/bash
# RunPod 환경에서 안정적으로 의존성 설치하는 스크립트
# 사용법: bash install_dependencies.sh

echo "========================================="
echo "Installing hint-system dependencies"
echo "========================================="

# 0) 기존 충돌 패키지 완전 정리 (깨끗한 설치 보장)
echo "Step 0/7: Deep cleaning conflicting packages..."
pip uninstall -y vllm torch torchvision torchaudio gradio tomlkit pyairports transformers openai outlines xformers 2>/dev/null || true
pip cache purge 2>/dev/null || true
echo "✅ Deep cleanup complete"

# 1) pip 업그레이드
echo "Step 1/7: Upgrading pip..."
pip install --upgrade pip setuptools wheel

# 2) torch 먼저 설치 (vLLM 호환 버전)
echo "Step 2/7: Installing PyTorch 2.4.0+cu121..."
pip install --no-cache-dir torch==2.4.0 --index-url https://download.pytorch.org/whl/cu121

# 3) vLLM 설치 (torch 이미 설치됨)
echo "Step 3/7: Installing vLLM 0.6.3..."
pip install --no-cache-dir vllm==0.6.3 --no-deps
pip install --no-cache-dir xformers psutil numpy ray

# 4) pyairports 문제 해결 (airportsdata 설치)
echo "Step 4/7: Fixing pyairports import error..."
pip uninstall pyairports -y 2>/dev/null || true
pip install --no-cache-dir airportsdata

# 5) 나머지 의존성 설치
echo "Step 5/7: Installing remaining requirements..."
pip install --no-cache-dir --timeout=300 -r requirements.txt

# 6) vLLM 의존성 재확인
echo "Step 6/7: Verifying vLLM dependencies..."
pip install --no-cache-dir --upgrade msgspec fastapi uvicorn pydantic

# 7) 검증
echo "Step 7/7: Verifying installation..."
echo "Testing core imports..."
python -c "
import sys
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

try:
    import torch
    print('✅ torch:', torch.__version__)
    
    import vllm
    print('✅ vllm: OK (version warning is normal)')
    
    import gradio
    print('✅ gradio:', gradio.__version__)
    
    import airportsdata
    print('✅ airportsdata: OK')
    
    print('\n✅ All critical imports successful!')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

echo "========================================="
echo "Installation complete!"
echo "========================================="
echo "Installed packages:"
pip list | grep -E "torch|transformers|accelerate|vllm|gradio|airportsdata"

echo ""
echo "✅ Ready to run vLLM server!"
echo "Run: python vllm_server.py"
