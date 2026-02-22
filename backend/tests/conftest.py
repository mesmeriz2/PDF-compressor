"""Pytest 설정"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db
from app.core.config import settings

# 테스트 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """테스트 데이터베이스 세션"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """테스트 클라이언트"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf():
    """샘플 PDF 파일 생성"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # 여러 페이지 생성
    for i in range(10):
        c.drawString(100, 750, f"Test PDF - Page {i+1}")
        c.drawString(100, 700, "This is a test PDF file for compression testing.")
        c.drawString(100, 650, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        c.showPage()
    
    c.save()
    buffer.seek(0)
    
    return buffer


@pytest.fixture
def large_pdf():
    """대용량 PDF 파일 생성 (더미)"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from PIL import Image
    import io
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # 이미지가 포함된 큰 PDF 생성
    for i in range(50):
        c.drawString(100, 750, f"Large PDF - Page {i+1}")
        
        # 더미 이미지 추가
        img = Image.new('RGB', (800, 600), color=(i*5 % 255, 100, 150))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        c.drawImage(img_buffer, 100, 200, width=400, height=300)
        c.showPage()
    
    c.save()
    buffer.seek(0)
    
    return buffer


@pytest.fixture
def setup_test_dirs():
    """테스트 디렉토리 설정"""
    test_dirs = ['./test_data/uploads', './test_data/results', './test_data/temp']
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    yield
    
    # 정리
    import shutil
    if os.path.exists('./test_data'):
        shutil.rmtree('./test_data')


















