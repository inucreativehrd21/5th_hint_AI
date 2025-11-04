#!/bin/bash
# RunPod 환경에서 안정적으로 의존성 설치하는 스크립트
# 사용법: bash install_dependencies.sh

echo "========================================="
echo "Installing hint-system dependencies"
echo "========================================="

# 0) 기존 충돌 패키지 정리 (깨끗한 설치 보장)
echo "Step 0/6: Cleaning up conflicting packages..."
pip uninstall -y gradio tomlkit pyairports transformers openai outlines 2>/dev/null || true
echo "✅ Cleanup complete (outlines removed to avoid guided_decoding hang)"

# 1) pip 업그레이드
echo "Step 1/6: Upgrading pip..."
pip install --upgrade pip setuptools wheel

# 2) vLLM 먼저 설치 (torch 2.4.0 포함)
echo "Step 2/6: Installing vLLM with torch 2.4.0 (5-10 minutes)..."
pip install --no-cache-dir vllm==0.6.3

# 3) pyairports 문제 해결 (airportsdata 설치)
echo "Step 3/6: Fixing pyairports import error..."
pip uninstall pyairports -y 2>/dev/null || true
pip install airportsdata

# 4) 나머지 의존성 설치
echo "Step 4/6: Installing remaining requirements..."
pip install --no-cache-dir --timeout=300 -r requirements.txt

# 5) 검증
echo "Step 5/6: Verifying installation..."
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
