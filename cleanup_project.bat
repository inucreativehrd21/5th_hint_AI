@echo off
REM ============================================================================
REM 프로젝트 정리 스크립트 (Windows)
REM 불필요한 파일 및 중복 문서 정리
REM ============================================================================

echo 🧹 프로젝트 정리 시작...
echo.

REM hint-system: 구버전 파일들
echo 📄 hint-system 구버전 파일 삭제 중...
if exist "hint-system\app_old.py" del /f "hint-system\app_old.py" && echo   🗑️  삭제: app_old.py
if exist "hint-system\app_vllm.py" del /f "hint-system\app_vllm.py" && echo   🗑️  삭제: app_vllm.py
if exist "hint-system\vllm_server.py" del /f "hint-system\vllm_server.py" && echo   🗑️  삭제: vllm_server.py
if exist "hint-system\start_vllm.bat" del /f "hint-system\start_vllm.bat" && echo   🗑️  삭제: start_vllm.bat
if exist "hint-system\test_imports.py" del /f "hint-system\test_imports.py" && echo   🗑️  삭제: test_imports.py
if exist "hint-system\test_vllm_integration.py" del /f "hint-system\test_vllm_integration.py" && echo   🗑️  삭제: test_vllm_integration.py
if exist "hint-system\test_runpod.sh" del /f "hint-system\test_runpod.sh" && echo   🗑️  삭제: test_runpod.sh
if exist "hint-system\deploy_runpod.sh" del /f "hint-system\deploy_runpod.sh" && echo   🗑️  삭제: deploy_runpod.sh
if exist "hint-system\pre_deployment_check.sh" del /f "hint-system\pre_deployment_check.sh" && echo   🗑️  삭제: pre_deployment_check.sh
if exist "hint-system\install_dependencies.sh" del /f "hint-system\install_dependencies.sh" && echo   🗑️  삭제: install_dependencies.sh

REM hint-system: 중복 README
echo.
echo 📄 중복 README 삭제 중...
if exist "hint-system\README.md" del /f "hint-system\README.md" && echo   🗑️  삭제: hint-system\README.md

REM 루트: 중복/구버전 문서들
echo.
echo 📄 루트 중복 문서 삭제 중...
if exist "DEPLOYMENT_SUMMARY.md" del /f "DEPLOYMENT_SUMMARY.md" && echo   🗑️  삭제: DEPLOYMENT_SUMMARY.md
if exist "FINAL_DEPLOYMENT_READY.md" del /f "FINAL_DEPLOYMENT_READY.md" && echo   🗑️  삭제: FINAL_DEPLOYMENT_READY.md
if exist "RUNPOD_DEPLOYMENT_FINAL.md" del /f "RUNPOD_DEPLOYMENT_FINAL.md" && echo   🗑️  삭제: RUNPOD_DEPLOYMENT_FINAL.md
if exist "RUNPOD_QUICKSTART.md" del /f "RUNPOD_QUICKSTART.md" && echo   🗑️  삭제: RUNPOD_QUICKSTART.md
if exist "SETUP_GUIDE.md" del /f "SETUP_GUIDE.md" && echo   🗑️  삭제: SETUP_GUIDE.md
if exist "UPLOAD_READY.md" del /f "UPLOAD_READY.md" && echo   🗑️  삭제: UPLOAD_READY.md

REM 루트: 불필요한 설정 파일
echo.
echo 📄 루트 불필요한 설정 파일 삭제 중...
if exist ".env.example" del /f ".env.example" && echo   🗑️  삭제: .env.example
if exist "config.py" del /f "config.py" && echo   🗑️  삭제: config.py

REM 디렉토리 삭제
echo.
echo 📁 불필요한 디렉토리 삭제 중...
if exist "hint-system\pyairports" rmdir /s /q "hint-system\pyairports" && echo   🗑️  삭제: hint-system\pyairports
if exist "hint-system\__pycache__" rmdir /s /q "hint-system\__pycache__" && echo   🗑️  삭제: hint-system\__pycache__
if exist "hint-system\models\__pycache__" rmdir /s /q "hint-system\models\__pycache__" && echo   🗑️  삭제: hint-system\models\__pycache__
if exist "__pycache__" rmdir /s /q "__pycache__" && echo   🗑️  삭제: __pycache__
if exist "logs" rmdir /s /q "logs" && echo   🗑️  삭제: logs

echo.
echo ✅ 정리 완료!
echo.
echo 📝 다음 단계:
echo   1. git status로 변경 사항 확인
echo   2. git add -A로 변경 사항 스테이징
echo   3. git commit -m "chore: 프로젝트 정리 - 불필요한 파일 제거"
echo.
pause
