# Gradio 힌트 생성 앱용 경량 Dockerfile
# vLLM 서버는 별도 컨테이너로 실행되므로, 이 컨테이너는 Gradio UI만 제공
FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치 (최소화)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements-app.txt .

# Python 패키지 설치 (vLLM 서버 클라이언트만 필요)
RUN pip install --no-cache-dir -r requirements-app.txt

# 애플리케이션 파일 복사
COPY app.py .
COPY config.py .
COPY models/ ./models/

# 데이터 및 평가 디렉토리 (볼륨으로 마운트됨)
RUN mkdir -p /app/data /app/evaluation

# 환경 변수 기본값
ENV VLLM_SERVER_URL=http://vllm-server:8000/v1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV DATA_FILE_PATH=/app/data/problems_multi_solution.json

# Gradio 포트 노출
EXPOSE 7860

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# 애플리케이션 실행
CMD ["python", "app.py"]
