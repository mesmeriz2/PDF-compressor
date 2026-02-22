"""데이터베이스 초기화 스크립트"""
import logging
from app.models.database import engine, Base
from app.models.job import Job  # 모델 import 필수

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """데이터베이스 테이블 생성"""
    try:
        logger.info("데이터베이스 테이블 생성 시작...")
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
        return True
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        return False


if __name__ == "__main__":
    init_db()





