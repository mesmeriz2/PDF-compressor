"""압축 엔진 테스트"""
import os
import pytest
from app.services.compression_engine import (
    GhostscriptEngine, 
    QPDFEngine, 
    PikePDFEngine,
    get_engine
)
from app.models.job import CompressionPreset


def test_pikepdf_engine_available():
    """PikePDF 엔진 사용 가능 확인"""
    engine = PikePDFEngine()
    assert engine.is_available() is True


def test_get_engine_pikepdf():
    """엔진 가져오기 - PikePDF"""
    engine = get_engine('pikepdf')
    assert isinstance(engine, PikePDFEngine)


def test_get_engine_fallback():
    """엔진 폴백 테스트"""
    # 존재하지 않는 엔진 요청 시 폴백
    engine = get_engine('nonexistent-engine')
    # 최소한 PikePDF로 폴백되어야 함
    assert engine.is_available()


def test_pikepdf_compression(sample_pdf, setup_test_dirs):
    """PikePDF 압축 테스트"""
    engine = PikePDFEngine()
    
    # 입력 파일 저장
    input_path = './test_data/uploads/input.pdf'
    output_path = './test_data/results/output.pdf'
    
    with open(input_path, 'wb') as f:
        f.write(sample_pdf.read())
    
    # 압축 실행
    result = engine.compress(
        input_path=input_path,
        output_path=output_path,
        preset=CompressionPreset.EBOOK,
        options={'linearize': True}
    )
    
    assert result['success'] is True
    assert os.path.exists(output_path)
    assert result['output_size'] > 0
    assert result['compression_ratio'] <= 1.0


def test_pdf_info_extraction(sample_pdf, setup_test_dirs):
    """PDF 정보 추출 테스트"""
    engine = PikePDFEngine()
    
    input_path = './test_data/uploads/info_test.pdf'
    with open(input_path, 'wb') as f:
        f.write(sample_pdf.read())
    
    info = engine.get_pdf_info(input_path)
    
    assert 'page_count' in info
    assert info['page_count'] > 0
    assert 'image_count' in info
    assert 'encrypted' in info


def test_compression_presets():
    """압축 프리셋 테스트"""
    presets = [
        CompressionPreset.SCREEN,
        CompressionPreset.EBOOK,
        CompressionPreset.PRINTER,
        CompressionPreset.PREPRESS
    ]
    
    for preset in presets:
        assert preset.value in ['screen', 'ebook', 'printer', 'prepress']


@pytest.mark.skipif(not GhostscriptEngine().is_available(), reason="Ghostscript not available")
def test_ghostscript_engine(sample_pdf, setup_test_dirs):
    """Ghostscript 엔진 테스트 (설치된 경우만)"""
    engine = GhostscriptEngine()
    
    input_path = './test_data/uploads/gs_input.pdf'
    output_path = './test_data/results/gs_output.pdf'
    
    with open(input_path, 'wb') as f:
        f.write(sample_pdf.read())
    
    result = engine.compress(
        input_path=input_path,
        output_path=output_path,
        preset=CompressionPreset.SCREEN
    )
    
    assert result['success'] is True
    assert os.path.exists(output_path)


@pytest.mark.skipif(not QPDFEngine().is_available(), reason="qpdf not available")
def test_qpdf_engine(sample_pdf, setup_test_dirs):
    """qpdf 엔진 테스트 (설치된 경우만)"""
    engine = QPDFEngine()
    
    input_path = './test_data/uploads/qpdf_input.pdf'
    output_path = './test_data/results/qpdf_output.pdf'
    
    with open(input_path, 'wb') as f:
        f.write(sample_pdf.read())
    
    result = engine.compress(
        input_path=input_path,
        output_path=output_path,
        preset=CompressionPreset.EBOOK
    )
    
    assert result['success'] is True
    assert os.path.exists(output_path)


















