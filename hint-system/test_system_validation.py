"""
시스템 임포트 및 구성 검증 스크립트
Docker 컨테이너 내에서 실행되어야 합니다.
"""
import sys
import os
from pathlib import Path

def check_imports():
    """필수 임포트 검증"""
    print("=" * 60)
    print("📦 Python 패키지 임포트 검증")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 필수 패키지
    required_packages = {
        'gradio': 'UI 프레임워크',
        'openai': 'vLLM 클라이언트',
        'requests': 'HTTP 요청',
        'json': '데이터 파싱',
        'os': '운영체제 인터페이스',
        'sys': '시스템 파라미터',
        'time': '시간 관련',
        'argparse': 'CLI 파서',
        'pathlib': '경로 관리',
    }
    
    print("\n필수 패키지:")
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package:20s} - {description}")
        except ImportError as e:
            print(f"  ❌ {package:20s} - {description}")
            errors.append(f"{package}: {e}")
    
    # 선택적 패키지
    optional_packages = {
        'dotenv': '환경 변수 로딩',
        'transformers': 'HuggingFace 모델 (선택)',
        'torch': 'PyTorch (선택)',
    }
    
    print("\n선택적 패키지:")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package:20s} - {description}")
        except ImportError:
            print(f"  ⚠️  {package:20s} - {description} (없음, 정상)")
            warnings.append(package)
    
    return errors, warnings


def check_project_imports():
    """프로젝트 모듈 임포트 검증"""
    print("\n" + "=" * 60)
    print("🔧 프로젝트 모듈 임포트 검증")
    print("=" * 60)
    
    errors = []
    
    # 작업 디렉토리를 sys.path에 추가
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    modules = [
        ('config', 'Config'),
        ('models.model_inference', 'VLLMInference'),
        ('models.model_inference', 'ModelInference'),
    ]
    
    print()
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")
            errors.append(f"{module_name}.{class_name}: {e}")
        except AttributeError as e:
            print(f"  ❌ {module_name}.{class_name}: 클래스 없음")
            errors.append(f"{module_name}.{class_name}: {e}")
    
    return errors


def check_environment():
    """환경 변수 검증"""
    print("\n" + "=" * 60)
    print("🌍 환경 변수 검증")
    print("=" * 60)
    
    required_vars = {
        'VLLM_SERVER_URL': 'vLLM 서버 URL',
        'DATA_FILE_PATH': '데이터 파일 경로',
    }
    
    optional_vars = {
        'GRADIO_SERVER_NAME': 'Gradio 서버 호스트',
        'GRADIO_SERVER_PORT': 'Gradio 서버 포트',
        'VLLM_MODEL': '사용 모델',
        'DEFAULT_TEMPERATURE': '기본 temperature',
    }
    
    errors = []
    warnings = []
    
    print("\n필수 환경 변수:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # 값이 너무 길면 축약
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var:25s} = {display_value}")
        else:
            print(f"  ❌ {var:25s} - {description} (설정 필요)")
            errors.append(f"{var}: 설정되지 않음")
    
    print("\n선택적 환경 변수:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var:25s} = {display_value}")
        else:
            print(f"  ⚠️  {var:25s} - {description} (기본값 사용)")
            warnings.append(var)
    
    return errors, warnings


def check_files():
    """필수 파일 존재 검증"""
    print("\n" + "=" * 60)
    print("📁 필수 파일 검증")
    print("=" * 60)
    
    errors = []
    
    # 데이터 파일 경로들
    data_paths = [
        os.getenv('DATA_FILE_PATH', 'data/problems_multi_solution.json'),
        'data/problems_multi_solution.json',
        '/app/data/problems_multi_solution.json',
    ]
    
    print("\n데이터 파일:")
    found = False
    for path in data_paths:
        if path and Path(path).exists():
            print(f"  ✅ {path}")
            found = True
            
            # JSON 파싱 검증
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"     📊 문제 수: {len(data)}개")
            except Exception as e:
                print(f"     ❌ JSON 파싱 오류: {e}")
                errors.append(f"JSON 파싱 실패: {path}")
            break
    
    if not found:
        print(f"  ❌ 데이터 파일을 찾을 수 없음")
        for path in data_paths:
            print(f"     시도: {path}")
        errors.append("데이터 파일 없음")
    
    # 프로젝트 파일들
    print("\n프로젝트 파일:")
    project_files = [
        'app.py',
        'config.py',
        'models/model_inference.py',
        'models/__init__.py',
    ]
    
    for file_path in project_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            errors.append(f"파일 없음: {file_path}")
    
    return errors


def check_vllm_connection():
    """vLLM 서버 연결 검증"""
    print("\n" + "=" * 60)
    print("🔗 vLLM 서버 연결 검증")
    print("=" * 60)
    
    import requests
    
    vllm_url = os.getenv('VLLM_SERVER_URL', 'http://localhost:8000/v1')
    health_url = vllm_url.replace('/v1', '/health')
    
    print(f"\nvLLM URL: {vllm_url}")
    print(f"Health URL: {health_url}")
    
    errors = []
    
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print(f"  ✅ 헬스체크 성공 (HTTP {response.status_code})")
        else:
            print(f"  ⚠️  헬스체크 응답 이상 (HTTP {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 연결 실패: 서버가 실행 중인지 확인")
        errors.append("vLLM 서버 연결 실패")
    except requests.exceptions.Timeout:
        print(f"  ❌ 타임아웃: 서버 응답 없음")
        errors.append("vLLM 서버 타임아웃")
    except Exception as e:
        print(f"  ❌ 예외 발생: {e}")
        errors.append(f"vLLM 연결 오류: {e}")
    
    return errors


def main():
    """메인 검증 프로세스"""
    print("\n" + "=" * 60)
    print("🔍 vLLM Docker 힌트 시스템 검증")
    print("=" * 60)
    
    all_errors = []
    all_warnings = []
    
    # 1. 패키지 임포트 검증
    errors, warnings = check_imports()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # 2. 프로젝트 모듈 검증
    errors = check_project_imports()
    all_errors.extend(errors)
    
    # 3. 환경 변수 검증
    errors, warnings = check_environment()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # 4. 파일 검증
    errors = check_files()
    all_errors.extend(errors)
    
    # 5. vLLM 연결 검증 (선택)
    try:
        errors = check_vllm_connection()
        all_errors.extend(errors)
    except Exception as e:
        print(f"\n⚠️  vLLM 연결 검증 건너뜀: {e}")
        all_warnings.append("vLLM 연결 검증 실패")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 검증 결과")
    print("=" * 60)
    print(f"\n  에러: {len(all_errors)}개")
    print(f"  경고: {len(all_warnings)}개")
    
    if all_errors:
        print("\n❌ 검증 실패:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print("\n💡 문제 해결:")
        print("  1. Docker 컨테이너 내에서 실행 중인지 확인")
        print("  2. requirements-app.txt 패키지 설치 확인")
        print("  3. .env 파일 설정 확인")
        print("  4. docker-compose up -d 로 서비스 시작")
        return 1
    else:
        print("\n✅ 모든 검증 통과!")
        if all_warnings:
            print(f"\n⚠️  {len(all_warnings)}개 경고 (선택 사항):")
            for i, warning in enumerate(all_warnings, 1):
                print(f"  {i}. {warning}")
        return 0


if __name__ == '__main__':
    sys.exit(main())
