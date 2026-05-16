import os
from celery import Celery
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.detection import Detection
from services.model_service import predict_image
from services.cloudinary_service import upload_image
from utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

@celery_app.task(name="predict_task")
def predict_task(db_record_id: int, image_path: str):
    logger.info(f"Task started - record_id={db_record_id}")

    db: Session = SessionLocal()
    output_img_path = None

    try:
        prediction = predict_image(image_path)
        output_img_path = prediction["output_img_path"]

        image_url = upload_image(output_img_path)
        logger.info(f"Uploaded to Cloudinary: {image_url}")

        record = db.query(Detection).filter(Detection.id == db_record_id).first()

        if record:
            record.status = "FINISHED"
            record.image_url = image_url
            record.total_count = prediction["total_count"]
            record.thin_pest_count  = prediction["counts"]["thin_pest"]
            record.round_pest_count = prediction["counts"]["round_pest"]
            record.big_pest_count   = prediction["counts"]["big_pest"]
            db.commit()
            logger.info(f"Task finished. Total = {prediction['total_count']}")
    except Exception as e:
        logger.exception(f"Task failed - record_id={db_record_id}")
        db.rollback()
        record = db.query(Detection).filter(Detection.id == db_record_id).first()
        if record:
            record.status = "FAILED"
            db.commit()

    finally:
        for path in [image_path, output_img_path]:
            if path and os.path.exists(path):
                os.remove(path)
                logger.debug(f"Removed temp file: {path}")
        db.close()