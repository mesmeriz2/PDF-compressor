"""Celery 워커"""
from app.workers.celery_app import celery_app
from app.workers.tasks import compress_pdf_task

__all__ = ['celery_app', 'compress_pdf_task']


















