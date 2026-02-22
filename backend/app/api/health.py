"""헬스체크 API"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from redis import Redis

from app.core.config import settings
from app.core.schemas import HealthResponse
from app.workers.celery_app import celery_app

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """
    헬스체크 엔드포인트
    """
    # Redis 연결 확인만 수행 (워커는 선택적)
    redis_connected = False
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        redis_client.ping()
        redis_connected = True
    except Exception as e:
        logger.error(f"Redis 연결 실패: {e}")
    finally:
        redis_client.close()
    
    return HealthResponse(
        status="healthy" if redis_connected else "degraded",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
        redis_connected=redis_connected,
        worker_count=0
    )


@router.get("/readyz")
async def readiness_check():
    """
    준비 상태 확인
    """
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"준비 상태 확인 실패: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"서비스 준비되지 않음: {str(e)}")
    finally:
        redis_client.close()


















