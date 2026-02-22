"""Pydantic 스키마"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.job import JobStatus, CompressionPreset


class CompressionOptions(BaseModel):
    """압축 옵션"""
    preset: CompressionPreset = CompressionPreset.EBOOK
    engine: Optional[str] = "ghostscript"
    
    # 이미지 설정
    downsample_dpi: Optional[int] = None
    jpeg_quality: Optional[int] = None
    
    # 폰트 설정
    compress_fonts: bool = True
    subset_fonts: bool = True
    
    # 구조 최적화
    linearize: bool = True
    remove_duplicates: bool = True
    compress_objects: bool = True
    
    # 메타데이터
    preserve_metadata: bool = True
    preserve_ocr: bool = True
    
    # 커스텀
    custom_options: Optional[Dict[str, Any]] = None


class JobCreate(BaseModel):
    """작업 생성 요청"""
    filename: str
    original_filename: str
    file_hash: Optional[str] = None
    original_size: int
    user_session: Optional[str] = None
    options: CompressionOptions = Field(default_factory=CompressionOptions)


class JobResponse(BaseModel):
    """작업 응답"""
    id: str
    filename: str
    original_filename: str
    status: JobStatus
    progress: float
    eta_seconds: Optional[int] = None
    
    # 파일 정보
    original_size: int
    compressed_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    compression_percentage: Optional[float] = None
    saved_bytes: Optional[int] = None
    page_count: Optional[int] = None
    image_count: Optional[int] = None
    
    # 결과
    result_url: Optional[str] = None
    
    # 에러
    error_message: Optional[str] = None
    
    # 타임스탬프
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """업로드 응답"""
    job_ids: list[str]
    message: str = "Files uploaded successfully"


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    version: str
    timestamp: datetime
    redis_connected: bool
    worker_count: int


class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

















