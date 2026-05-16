from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base
from datetime import datetime, UTC

class Detection(Base):
    __tablename__ = "detections"
    
    user_id = Column(String, index=True)
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True)
    status = Column(String, default="QUEUED")
    image_url = Column(String, nullable=True)
    cam_url = Column(String, nullable=True)
    total_count = Column(Integer, default=0)
    thin_pest_count = Column(Integer, default=0)
    round_pest_count = Column(Integer, default=0)
    big_pest_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))