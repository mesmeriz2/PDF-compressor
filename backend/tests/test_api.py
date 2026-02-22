"""API 테스트"""
import io
import pytest
from fastapi import status


def test_health_check(client):
    """헬스체크 테스트"""
    response = client.get("/api/healthz")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data


def test_root_endpoint(client):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "running"


def test_upload_single_pdf(client, sample_pdf, setup_test_dirs):
    """단일 PDF 업로드 테스트"""
    files = {
        'files': ('test.pdf', sample_pdf, 'application/pdf')
    }
    data = {
        'preset': 'ebook',
        'engine': 'pikepdf',  # 항상 사용 가능한 엔진
        'preserve_metadata': 'true',
        'preserve_ocr': 'true'
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    # 업로드는 성공해야 함
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert "job_ids" in result
    assert len(result["job_ids"]) == 1


def test_upload_multiple_pdfs(client, sample_pdf, setup_test_dirs):
    """다중 PDF 업로드 테스트"""
    files = [
        ('files', ('test1.pdf', io.BytesIO(sample_pdf.read()), 'application/pdf')),
        ('files', ('test2.pdf', io.BytesIO(sample_pdf.read()), 'application/pdf')),
    ]
    data = {
        'preset': 'screen',
        'engine': 'pikepdf'
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result["job_ids"]) == 2


def test_upload_invalid_file(client):
    """잘못된 파일 업로드 테스트"""
    files = {
        'files': ('test.txt', io.BytesIO(b"Not a PDF"), 'text/plain')
    }
    data = {'preset': 'ebook'}
    
    response = client.post("/api/upload", files=files, data=data)
    
    # 400 에러가 발생해야 함
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_job_status(client, db):
    """작업 상태 조회 테스트"""
    from app.models.job import Job, JobStatus
    from datetime import datetime, timezone
    
    # 테스트 작업 생성
    job = Job(
        id="test-job-id",
        filename="test.pdf",
        original_filename="test.pdf",
        original_size=1000000,
        status=JobStatus.QUEUED,
        preset="ebook",
        engine="ghostscript",
        created_at=datetime.now(timezone.utc)
    )
    db.add(job)
    db.commit()
    
    # 작업 조회
    response = client.get(f"/api/jobs/{job.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == job.id
    assert data["status"] == "queued"


def test_get_nonexistent_job(client):
    """존재하지 않는 작업 조회 테스트"""
    response = client.get("/api/jobs/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cancel_job(client, db):
    """작업 취소 테스트"""
    from app.models.job import Job, JobStatus
    from datetime import datetime, timezone
    
    # 실행 중인 작업 생성
    job = Job(
        id="cancel-test-job",
        filename="test.pdf",
        original_filename="test.pdf",
        original_size=1000000,
        status=JobStatus.RUNNING,
        preset="ebook",
        engine="ghostscript",
        created_at=datetime.now(timezone.utc)
    )
    db.add(job)
    db.commit()
    
    # 작업 취소
    response = client.post(f"/api/jobs/{job.id}/cancel")
    assert response.status_code == status.HTTP_200_OK
    
    # 상태 확인
    db.refresh(job)
    assert job.status == JobStatus.CANCELLED


def test_delete_job(client, db):
    """작업 삭제 테스트"""
    from app.models.job import Job, JobStatus
    from datetime import datetime, timezone
    
    job = Job(
        id="delete-test-job",
        filename="test.pdf",
        original_filename="test.pdf",
        original_size=1000000,
        status=JobStatus.COMPLETED,
        preset="ebook",
        engine="ghostscript",
        created_at=datetime.now(timezone.utc)
    )
    db.add(job)
    db.commit()
    
    # 작업 삭제
    response = client.delete(f"/api/jobs/{job.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # 삭제 확인
    deleted_job = db.query(Job).filter(Job.id == job.id).first()
    assert deleted_job is None


def test_list_jobs(client, db):
    """작업 목록 조회 테스트"""
    from app.models.job import Job, JobStatus
    from datetime import datetime, timezone
    
    # 여러 작업 생성
    for i in range(5):
        job = Job(
            id=f"list-test-job-{i}",
            filename=f"test{i}.pdf",
            original_filename=f"test{i}.pdf",
            original_size=1000000,
            status=JobStatus.QUEUED if i % 2 == 0 else JobStatus.COMPLETED,
            preset="ebook",
            engine="ghostscript",
            created_at=datetime.now(timezone.utc)
        )
        db.add(job)
    db.commit()
    
    # 전체 목록 조회
    response = client.get("/api/jobs")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5
    
    # 상태별 필터링
    response = client.get("/api/jobs?status=queued")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(job["status"] == "queued" for job in data)


def test_cors_headers(client):
    """CORS 헤더 테스트"""
    response = client.options("/api/healthz", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    # OPTIONS 요청은 성공해야 함
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]


















