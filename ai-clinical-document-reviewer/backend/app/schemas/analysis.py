from datetime import datetime
from typing import Optional, Generic, TypeVar, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.report import StructuredClinicalReport

T = TypeVar("T")


class APIError(BaseModel):
    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[APIError] = None


class AnalysisTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw clinical text to review")


class AnalysisListItem(BaseModel):
    id: str
    input_type: str
    original_filename: Optional[str] = None
    status: str
    report_summary: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    id: str
    input_type: str
    original_filename: Optional[str] = None
    raw_text: Optional[str] = None
    status: str
    report_summary: Optional[str] = None
    structured_report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
