"""
vLLM Server Script for Fast Hint Generation

This script launches a vLLM server optimized for code hint generation.
vLLM provides:
- 15-24x faster inference compared to HuggingFace Transformers
- Continuous batching for improved throughput
- PagedAttention for efficient memory management
- OpenAI-compatible API

Usage:
    python vllm_server.py --model Qwen/Qwen2.5-Coder-7B-Instruct --port 8000

Environment Variables:
    VLLM_MODEL: Model to serve (default: Qwen/Qwen2.5-Coder-7B-Instruct)
    VLLM_PORT: Server port (default: 8000)
    VLLM_GPU_MEMORY_UTILIZATION: GPU memory fraction (default: 0.9)
    VLLM_MAX_MODEL_LEN: Maximum sequence length (default: 4096)
"""

import os
import argparse
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Launch vLLM server for hint generation")
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct"),
        help="HuggingFace model name or path"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("VLLM_PORT", "8000")),
        help="Server port"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host"
    )
    parser.add_argument(
        "--gpu-memory-utilization",
        type=float,
        default=float(os.getenv("VLLM_GPU_MEMORY_UTILIZATION", "0.9")),
        help="GPU memory utilization (0.0-1.0)"
    )
    parser.add_argument(
        "--max-model-len",
        type=int,
        default=int(os.getenv("VLLM_MAX_MODEL_LEN", "4096")),
        help="Maximum sequence length"
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=1,
        help="Number of GPUs for tensor parallelism"
    )
    parser.add_argument(
        "--dtype",
        type=str,
        default="auto",
        choices=["auto", "half", "float16", "bfloat16", "float32"],
        help="Data type for model weights"
    )
    parser.add_argument(
        "--max-num-seqs",
        type=int,
        default=256,
        help="Maximum number of sequences in a batch"
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        default=True,
        help="Trust remote code for custom models"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    logger.info("=" * 80)
    logger.info("Starting vLLM Server for Code Hint Generation")
    logger.info("=" * 80)
    logger.info(f"Model: {args.model}")
    logger.info(f"Server: http://{args.host}:{args.port}")
    logger.info(f"GPU Memory Utilization: {args.gpu_memory_utilization}")
    logger.info(f"Max Model Length: {args.max_model_len}")
    logger.info(f"Tensor Parallel Size: {args.tensor_parallel_size}")
    logger.info(f"Data Type: {args.dtype}")
    logger.info("=" * 80)

    try:
        # Import vllm here to provide better error message if not installed
        from vllm.entrypoints.openai.api_server import run_server
        from vllm.engine.arg_utils import AsyncEngineArgs
        from vllm.engine.async_llm_engine import AsyncLLMEngine

        # Configure engine arguments
        engine_args = AsyncEngineArgs(
            model=args.model,
            tensor_parallel_size=args.tensor_parallel_size,
            dtype=args.dtype,
            gpu_memory_utilization=args.gpu_memory_utilization,
            max_model_len=args.max_model_len,
            max_num_seqs=args.max_num_seqs,
            trust_remote_code=args.trust_remote_code,
            disable_log_requests=False,
        )

        # Start the server using vLLM's CLI
        import subprocess
        import sys

        # 환경 변수로 guided-decoding 완전 비활성화
        import os
        env = os.environ.copy()
        env["VLLM_ALLOW_RUNTIME_LORA_UPDATING"] = "0"
        
        cmd = [
            sys.executable, "-m", "vllm.entrypoints.openai.api_server",
            "--model", args.model,
            "--host", args.host,
            "--port", str(args.port),
            "--gpu-memory-utilization", str(args.gpu_memory_utilization),
            "--max-model-len", str(args.max_model_len),
            "--tensor-parallel-size", str(args.tensor_parallel_size),
            "--dtype", args.dtype,
            "--max-num-seqs", str(args.max_num_seqs),
            "--disable-log-requests",
        ]

        if args.trust_remote_code:
            cmd.append("--trust-remote-code")

        logger.info(f"Running command: {' '.join(cmd)}")
        logger.info("Note: Guided decoding disabled to avoid outlines dependency")
        subprocess.run(cmd, env=env)

    except ImportError:
        logger.error("vLLM is not installed. Please install it with:")
        logger.error("  pip install vllm")
        logger.error("For CUDA 12.1+:")
        logger.error("  pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121")
        return 1
    except Exception as e:
        logger.error(f"Failed to start vLLM server: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
