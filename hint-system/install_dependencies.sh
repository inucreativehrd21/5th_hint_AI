#!/bin/bash
# RunPod 환경에서 안정적으로 의존성 설치하는 스크립트
# 사용법: bash install_dependencies.sh

set -e  # 에러 발생 시 중단

echo "========================================="
echo "Installing hint-system dependencies"
echo "========================================="

# 1) pip 업그레이드
echo "Step 1/5: Upgrading pip..."
pip install --upgrade pip setuptools wheel

# 2) PyTorch 먼저 설치 (CUDA 12.1)
echo "Step 2/5: Installing PyTorch (CUDA 12.1)..."
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu121

# 3) 나머지 의존성 설치 (vLLM 제외)
echo "Step 3/5: Installing requirements.txt..."
pip install --no-cache-dir --timeout=300 -r requirements.txt

# 4) vLLM 설치 (필수)
echo "Step 4/5: Installing vLLM (this may take 5-10 minutes)..."
pip install --no-cache-dir vllm==0.6.3

# 5) pyairports 재설치 (vLLM이 설치한 0.0.1 버전 제거)
echo "Step 5/5: Fixing pyairports (replacing 0.0.1 with 2.1.3)..."
pip uninstall pyairports -y
pip install pyairports==2.1.3

echo "========================================="
echo "Installation complete!"
echo "========================================="
echo "Installed packages:"
pip list | grep -E "torch|transformers|accelerate|vllm|gradio|pyairports"

echo ""
echo "✅ Ready to run vLLM server!"
echo "Run: python vllm_server.py"
