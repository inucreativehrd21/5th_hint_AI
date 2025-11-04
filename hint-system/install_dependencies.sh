#!/bin/bash
# RunPod 환경에서 안정적으로 의존성 설치하는 스크립트
# 사용법: bash install_dependencies.sh

echo "========================================="
echo "Installing hint-system dependencies"
echo "========================================="

# 1) pip 업그레이드
echo "Step 1/6: Upgrading pip..."
pip install --upgrade pip setuptools wheel

# 2) 충돌 해결: tomlkit 먼저 업그레이드
echo "Step 2/6: Fixing dependency conflicts..."
pip install --upgrade tomlkit

# 3) vLLM 먼저 설치 (torch 2.4.0 포함)
echo "Step 3/6: Installing vLLM with torch 2.4.0 (5-10 minutes)..."
pip install --no-cache-dir vllm==0.6.3

# 4) pyairports 문제 해결 (airportsdata로 대체)
echo "Step 4/6: Fixing pyairports import error..."
pip uninstall pyairports -y 2>/dev/null || true
pip install airportsdata

# 5) 나머지 의존성 설치
echo "Step 5/6: Installing remaining requirements..."
pip install --no-cache-dir --timeout=300 -r requirements.txt

# 6) 검증
echo "Step 6/6: Verifying installation..."
python -c "import torch; import vllm; import gradio; print('✅ All imports successful')"

echo "========================================="
echo "Installation complete!"
echo "========================================="
echo "Installed packages:"
pip list | grep -E "torch|transformers|accelerate|vllm|gradio|airportsdata"

echo ""
echo "✅ Ready to run vLLM server!"
echo "Run: python vllm_server.py"
