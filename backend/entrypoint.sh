#!/bin/bash
set -e

echo "=== PDF Compressor Backend 시작 ==="

# 데이터베이스 초기화
echo "[1/2] 데이터베이스 테이블 생성..."
python3 -m app.init_db

# 서버 시작
echo "[2/2] FastAPI 서버 시작..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000





