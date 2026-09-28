import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Float, DateTime, Index
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InputType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    input_type = Column(String(20), nullable=False)  # 'text', 'pdf', 'image'
    original_filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=AnalysisStatus.PENDING.value, index=True)
    report_summary = Column(Text, nullable=True)
    # Use JSONB on PostgreSQL if available, otherwise JSON
    structured_report = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # elapsed seconds
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_analyses_status_created", "status", "created_at"),
    )

    def __repr__(self):
        return f"<Analysis id={self.id} status={self.status} input_type={self.input_type}>"
