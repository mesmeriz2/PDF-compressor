"""Celery 애플리케이션"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    'pdf_compressor',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # 작업 설정
    task_track_started=True,
    task_time_limit=settings.TASK_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.TASK_TIMEOUT_SECONDS - 60,
    
    # 재시도 설정
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 동시성
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    
    # 결과 만료
    result_expires=3600 * 24,  # 24시간

    # Celery 6.0 대비 브로커 재연결 설정
    broker_connection_retry_on_startup=True,
)


















