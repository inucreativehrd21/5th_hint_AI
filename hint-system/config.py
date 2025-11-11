"""
Configuration management for Hint Generation System
Loads settings from .env file and provides project-wide configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# First check in hint-system directory, then parent directory
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
if not env_path.exists():
    env_path = current_dir.parent / ".env"

load_dotenv(env_path)


class Config:
    """Central configuration class for the application"""

    # ============================================================================
    # Project Paths
    # ============================================================================
    PROJECT_ROOT = Path(__file__).parent  # hint-system directory

    # Data file path
    DATA_FILE_PATH = PROJECT_ROOT / "data" / "problems_multi_solution.json"
    data_env = os.getenv("DATA_FILE_PATH")
    if data_env:
        DATA_FILE_PATH = Path(data_env) if Path(data_env).is_absolute() else PROJECT_ROOT.parent / data_env

    # Evaluation results directory
    EVALUATION_RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"
    eval_env = os.getenv("EVALUATION_RESULTS_DIR")
    if eval_env:
        EVALUATION_RESULTS_DIR = Path(eval_env) if Path(eval_env).is_absolute() else PROJECT_ROOT.parent / eval_env

    # Crawler output directory
    CRAWLER_OUTPUT_DIR = PROJECT_ROOT / "crawler" / "output"
    crawler_env = os.getenv("CRAWLER_OUTPUT_DIR")
    if crawler_env:
        CRAWLER_OUTPUT_DIR = Path(crawler_env) if Path(crawler_env).is_absolute() else PROJECT_ROOT.parent / crawler_env

    # Logs directory
    LOG_FILE = PROJECT_ROOT / "logs" / "app.log"
    log_env = os.getenv("LOG_FILE")
    if log_env:
        LOG_FILE = Path(log_env) if Path(log_env).is_absolute() else PROJECT_ROOT.parent / log_env

    # ============================================================================
    # vLLM Server Configuration
    # ============================================================================
    VLLM_SERVER_URL = os.getenv("VLLM_SERVER_URL", "")
    VLLM_MODEL = os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")
    VLLM_PORT = int(os.getenv("VLLM_PORT", "8000"))
    VLLM_GPU_MEMORY_UTILIZATION = float(os.getenv("VLLM_GPU_MEMORY_UTILIZATION", "0.9"))
    VLLM_MAX_MODEL_LEN = int(os.getenv("VLLM_MAX_MODEL_LEN", "4096"))
    VLLM_TENSOR_PARALLEL_SIZE = int(os.getenv("VLLM_TENSOR_PARALLEL_SIZE", "1"))

    # ============================================================================
    # Model Configuration
    # ============================================================================
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")

    # ============================================================================
    # Generation Parameters
    # ============================================================================
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    MAX_HINT_TOKENS = int(os.getenv("MAX_HINT_TOKENS", "512"))
    NUM_HINTS_PER_REQUEST = int(os.getenv("NUM_HINTS_PER_REQUEST", "1"))

    # ============================================================================
    # Logging
    # ============================================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # ============================================================================
    # Advanced Settings
    # ============================================================================
    SEQUENTIAL_MODEL_LOAD = os.getenv("SEQUENTIAL_MODEL_LOAD", "true").lower() == "true"

    # ============================================================================
    # Crawler Configuration (optional)
    # ============================================================================
    SOLVED_AC_API_KEY = os.getenv("SOLVED_AC_API_KEY", "")

    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "=" * 60)
        print("📋 Configuration Settings")
        print("=" * 60)
        print(f"Project Root:        {cls.PROJECT_ROOT}")
        print(f"Data File:           {cls.DATA_FILE_PATH}")
        print(f"Evaluation Dir:      {cls.EVALUATION_RESULTS_DIR}")
        print(f"vLLM Server URL:     {cls.VLLM_SERVER_URL or '(disabled - using HuggingFace)'}")
        if cls.VLLM_SERVER_URL:
            print(f"vLLM Model:          {cls.VLLM_MODEL}")
        print(f"Default Temperature: {cls.DEFAULT_TEMPERATURE}")
        print(f"Log Level:           {cls.LOG_LEVEL}")
        print("=" * 60 + "\n")

    @classmethod
    def get_relative_path(cls, path: Path) -> str:
        """Get path relative to project root"""
        try:
            return str(path.relative_to(cls.PROJECT_ROOT))
        except ValueError:
            return str(path)

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.EVALUATION_RESULTS_DIR,
            cls.CRAWLER_OUTPUT_DIR,
            cls.LOG_FILE.parent,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
