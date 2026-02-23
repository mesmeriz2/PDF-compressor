"""PDF 압축 엔진 - 전략 패턴"""
import os
import logging
import subprocess
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import pikepdf
from app.models.job import CompressionPreset
from app.core.config import settings

logger = logging.getLogger(__name__)


class CompressionEngine(ABC):
    """압축 엔진 추상 클래스"""
    
    @abstractmethod
    def compress(
        self, 
        input_path: str, 
        output_path: str, 
        preset: CompressionPreset,
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        PDF 압축
        
        Args:
            input_path: 입력 파일 경로
            output_path: 출력 파일 경로
            preset: 압축 프리셋
            options: 추가 옵션
            progress_callback: 진행률 콜백
            
        Returns:
            압축 결과 정보
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """엔진 사용 가능 여부"""
        pass
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """PDF 메타데이터 추출"""
        try:
            with pikepdf.open(pdf_path) as pdf:
                page_count = len(pdf.pages)

                # 이미지 개수 추정
                image_count = 0
                for page in pdf.pages[:10]:  # 처음 10페이지만 샘플링
                    if '/XObject' in page.Resources:
                        xobjects = page.Resources.XObject
                        for obj in xobjects:
                            if xobjects[obj].Subtype == '/Image':
                                image_count += 1

                # 전체 추정
                if page_count > 10:
                    image_count = int(image_count * (page_count / 10))

                # 비밀번호 없이 열렸으면 압축 가능한 파일로 처리.
                # Owner 비밀번호만 있는 권한 제한 PDF는 is_encrypted=True를 반환하지만
                # 실제로는 비밀번호 없이 열리므로 암호화된 것으로 취급하지 않는다.
                return {
                    'page_count': page_count,
                    'image_count': image_count,
                    'encrypted': False
                }
        except pikepdf.PasswordError:
            # User 비밀번호가 필요한 진짜 암호화 PDF
            logger.warning(f"암호화된 PDF (비밀번호 필요): {pdf_path}")
            return {
                'page_count': 0,
                'image_count': 0,
                'encrypted': True
            }
        except Exception as e:
            logger.error(f"PDF 정보 추출 실패: {e}")
            return {
                'page_count': 0,
                'image_count': 0,
                'encrypted': False
            }


class GhostscriptEngine(CompressionEngine):
    """Ghostscript 압축 엔진"""
    
    # 프리셋별 설정
    PRESET_SETTINGS = {
        CompressionPreset.SCREEN: {
            'pdfsettings': '/screen',
            'dpi': 72,
            'jpeg_quality': 30
        },
        CompressionPreset.EBOOK: {
            'pdfsettings': '/ebook',
            'dpi': 150,
            'jpeg_quality': 60
        },
        CompressionPreset.PRINTER: {
            'pdfsettings': '/printer',
            'dpi': 300,
            'jpeg_quality': 80
        },
        CompressionPreset.PREPRESS: {
            'pdfsettings': '/prepress',
            'dpi': 300,
            'jpeg_quality': 90
        }
    }
    
    def is_available(self) -> bool:
        """Ghostscript 사용 가능 여부"""
        gs_command = 'gs' if os.name != 'nt' else 'gswin64c'
        return shutil.which(gs_command) is not None
    
    def compress(
        self, 
        input_path: str, 
        output_path: str, 
        preset: CompressionPreset,
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Ghostscript로 PDF 압축"""
        
        if not self.is_available():
            raise RuntimeError("Ghostscript가 설치되어 있지 않습니다")
        
        options = options or {}
        preset_config = self.PRESET_SETTINGS.get(preset, self.PRESET_SETTINGS[CompressionPreset.EBOOK])
        
        # DPI 및 품질 설정
        dpi = options.get('downsample_dpi', preset_config['dpi'])
        jpeg_quality = options.get('jpeg_quality', preset_config['jpeg_quality'])
        
        # Ghostscript 명령 구성
        gs_command = 'gs' if os.name != 'nt' else 'gswin64c'
        
        cmd = [
            gs_command,
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.5',
            f"-dPDFSETTINGS={preset_config['pdfsettings']}",
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            '-dDownsampleColorImages=true',
            f'-dColorImageResolution={dpi}',
            '-dDownsampleGrayImages=true',
            f'-dGrayImageResolution={dpi}',
            '-dDownsampleMonoImages=true',
            f'-dMonoImageResolution={dpi}',
            f'-dJPEGQ={jpeg_quality}',
            '-dDetectDuplicateImages=true',
        ]
        
        # 폰트 설정
        if options.get('compress_fonts', True):
            cmd.append('-dCompressFonts=true')
        if options.get('subset_fonts', True):
            cmd.append('-dSubsetFonts=true')
        
        # 오브젝트 압축
        if options.get('compress_objects', True):
            cmd.append('-dCompressPages=true')
        
        cmd.extend([
            f'-sOutputFile={output_path}',
            input_path
        ])
        
        logger.info(f"Ghostscript 명령 실행: {' '.join(cmd)}")
        
        try:
            # 진행률 콜백
            if progress_callback:
                progress_callback(0.3)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.TASK_TIMEOUT_SECONDS,
                check=True
            )
            
            if progress_callback:
                progress_callback(0.9)
            
            # 결과 확인
            if not os.path.exists(output_path):
                raise RuntimeError("출력 파일이 생성되지 않았습니다")
            
            output_size = os.path.getsize(output_path)
            input_size = os.path.getsize(input_path)
            
            logger.info(f"압축 완료: {input_size} -> {output_size} bytes")
            
            return {
                'success': True,
                'engine': 'ghostscript',
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': output_size / input_size if input_size > 0 else 1.0
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Ghostscript 타임아웃")
            raise RuntimeError("압축 작업 시간 초과")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ghostscript 실패: {e.stderr}")
            raise RuntimeError(f"Ghostscript 압축 실패: {e.stderr}")
        except Exception as e:
            logger.error(f"압축 중 오류: {e}")
            raise


class QPDFEngine(CompressionEngine):
    """qpdf 최적화 엔진"""
    
    def is_available(self) -> bool:
        """qpdf 사용 가능 여부"""
        return shutil.which('qpdf') is not None
    
    def compress(
        self, 
        input_path: str, 
        output_path: str, 
        preset: CompressionPreset,
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """qpdf로 PDF 최적화"""
        
        if not self.is_available():
            raise RuntimeError("qpdf가 설치되어 있지 않습니다")
        
        options = options or {}
        
        # qpdf 명령 구성
        cmd = [
            'qpdf',
            '--optimize-images',
            '--compression-level=9',
        ]
        
        # 선형화 (웹 최적화)
        if options.get('linearize', True):
            cmd.append('--linearize')
        
        # 오브젝트 스트림
        if options.get('compress_objects', True):
            cmd.append('--object-streams=generate')
        
        # 중복 제거
        if options.get('remove_duplicates', True):
            cmd.append('--remove-unreferenced-resources=yes')
        
        cmd.extend([input_path, output_path])
        
        logger.info(f"qpdf 명령 실행: {' '.join(cmd)}")
        
        try:
            if progress_callback:
                progress_callback(0.3)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.TASK_TIMEOUT_SECONDS,
                check=True
            )
            
            if progress_callback:
                progress_callback(0.9)
            
            if not os.path.exists(output_path):
                raise RuntimeError("출력 파일이 생성되지 않았습니다")
            
            output_size = os.path.getsize(output_path)
            input_size = os.path.getsize(input_path)
            
            logger.info(f"최적화 완료: {input_size} -> {output_size} bytes")
            
            return {
                'success': True,
                'engine': 'qpdf',
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': output_size / input_size if input_size > 0 else 1.0
            }
            
        except subprocess.TimeoutExpired:
            logger.error("qpdf 타임아웃")
            raise RuntimeError("최적화 작업 시간 초과")
        except subprocess.CalledProcessError as e:
            logger.error(f"qpdf 실패: {e.stderr}")
            raise RuntimeError(f"qpdf 최적화 실패: {e.stderr}")
        except Exception as e:
            logger.error(f"최적화 중 오류: {e}")
            raise


class PikePDFEngine(CompressionEngine):
    """pikepdf 기반 경량 압축 엔진"""
    
    def is_available(self) -> bool:
        """항상 사용 가능 (Python 패키지)"""
        return True
    
    def compress(
        self, 
        input_path: str, 
        output_path: str, 
        preset: CompressionPreset,
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """pikepdf로 기본 압축"""
        
        options = options or {}
        
        try:
            if progress_callback:
                progress_callback(0.2)
            
            with pikepdf.open(input_path) as pdf:
                if progress_callback:
                    progress_callback(0.5)
                
                # 메타데이터 제거 옵션
                if not options.get('preserve_metadata', True):
                    pdf.docinfo.clear()
                
                # 저장 옵션
                save_options = {
                    'compress_streams': True,
                    'stream_decode_level': pikepdf.StreamDecodeLevel.generalized,
                    'object_stream_mode': pikepdf.ObjectStreamMode.generate,
                }
                
                if options.get('linearize', False):
                    save_options['linearize'] = True
                
                pdf.save(output_path, **save_options)
            
            if progress_callback:
                progress_callback(0.9)
            
            output_size = os.path.getsize(output_path)
            input_size = os.path.getsize(input_path)
            
            logger.info(f"pikepdf 압축 완료: {input_size} -> {output_size} bytes")
            
            return {
                'success': True,
                'engine': 'pikepdf',
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': output_size / input_size if input_size > 0 else 1.0
            }
            
        except Exception as e:
            logger.error(f"pikepdf 압축 실패: {e}")
            raise RuntimeError(f"pikepdf 압축 실패: {e}")


def get_engine(engine_name: str) -> CompressionEngine:
    """엔진 인스턴스 반환"""
    engines = {
        'ghostscript': GhostscriptEngine(),
        'qpdf': QPDFEngine(),
        'pikepdf': PikePDFEngine(),
    }
    
    engine = engines.get(engine_name.lower())
    if not engine:
        raise ValueError(f"알 수 없는 엔진: {engine_name}")
    
    if not engine.is_available():
        logger.warning(f"엔진 {engine_name}을 사용할 수 없습니다")
        
        # 폴백 엔진 찾기
        if settings.ENABLE_ENGINE_FALLBACK:
            for fallback_name, fallback_engine in engines.items():
                if fallback_engine.is_available():
                    logger.info(f"폴백 엔진 사용: {fallback_name}")
                    return fallback_engine
            
            # 모두 실패하면 pikepdf 사용 (항상 사용 가능)
            return PikePDFEngine()
        else:
            raise RuntimeError(f"엔진 {engine_name}을 사용할 수 없습니다")
    
    return engine


















