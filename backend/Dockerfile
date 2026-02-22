# 멀티 스테이지 빌드
FROM python:3.11-slim as base

# 환경 변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    qpdf \
    libmagic1 \
    libmagic-dev \
    file \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./app ./app

# Entrypoint 스크립트 복사
COPY entrypoint.sh /entrypoint.sh
COPY worker-entrypoint.sh /worker-entrypoint.sh
COPY beat-entrypoint.sh /beat-entrypoint.sh

# 데이터 디렉토리 생성 (루트 권한으로)
RUN mkdir -p /data/uploads /data/results /data/temp

# 비루트 사용자 생성 및 권한 설정
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /data && \
    chmod +x /entrypoint.sh && \
    chmod +x /worker-entrypoint.sh && \
    chmod +x /beat-entrypoint.sh
USER appuser

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/healthz')"

# 포트
EXPOSE 8000

# 실행
ENTRYPOINT ["/entrypoint.sh"]










