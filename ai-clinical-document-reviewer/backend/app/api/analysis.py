import time
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus, InputType
from app.schemas.analysis import (
    APIResponse,
    APIError,
    AnalysisResponse,
    AnalysisListItem,
)
from app.services.document_processor import document_processor
from app.services.ai_service import (
    ai_service,
    AIAnalysisError,
    AIServiceUnavailableError,
    AIRateLimitError,
    AITimeoutError,
    AIMalformedResponseError,
)
from app.services.report_service import report_service
from app.utils.logger import logger

router = APIRouter()


@router.post(
    "/analyses",
    response_model=APIResponse[AnalysisResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit clinical text or document for AI review"
)
async def create_analysis(
    request: Request,
    db: Session = Depends(get_db)
):
    """Accepts either plain text OR a document file (PDF, PNG, JPG, JPEG).
    Validates, extracts text / runs OCR, analyzes clinical contents via AI,
    persists the structured report to PostgreSQL, and returns the full analysis.
    """
    start_time = time.time()
    content_type = request.headers.get("content-type", "")

    input_text: Optional[str] = None
    uploaded_file: Optional[UploadFile] = None
    file_bytes: Optional[bytes] = None
    filename: Optional[str] = None

    # Parse input based on request content type
    if "application/json" in content_type:
        try:
            body = await request.json()
            input_text = body.get("text")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_JSON", "message": "Invalid JSON payload."}
            )
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        input_text = form.get("text")
        raw_file = form.get("file")
        if raw_file and hasattr(raw_file, "filename") and raw_file.filename:
            uploaded_file = raw_file
            filename = uploaded_file.filename
            read_fn = getattr(uploaded_file, "read", None)
            if callable(read_fn):
                read_res = read_fn()
                file_bytes = await read_res if hasattr(read_res, "__await__") else read_res
    else:
        # Fallback check for raw text
        body_bytes = await request.body()
        if body_bytes:
            input_text = body_bytes.decode("utf-8", errors="ignore")

    # Validate that either text or file is provided
    has_text = bool(input_text and str(input_text).strip())
    has_file = bool(uploaded_file is not None and filename is not None)

    if not has_text and not has_file:
        return APIResponse(
            success=False,
            error=APIError(
                code="VALIDATION_ERROR",
                message="Please enter clinical text before submitting."
            )
        )

    # Determine input type
    if has_file and filename:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        determined_type = InputType.PDF.value if ext == "pdf" else InputType.IMAGE.value
    else:
        determined_type = InputType.TEXT.value

    # Create initial database record in PROCESSING state
    analysis_id = str(uuid.uuid4())
    analysis_record = Analysis(
        id=analysis_id,
        input_type=determined_type,
        original_filename=filename if has_file else None,
        status=AnalysisStatus.PROCESSING.value,
        raw_text=input_text if has_text else None,
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    logger.info(f"Initiated analysis {analysis_id} for input type: {determined_type}")

    # Process Document (Extraction / OCR)
    extracted_text = ""
    processing_metadata = {}
    try:
        if has_file and file_bytes is not None and filename is not None:
            proc_result = document_processor.process_file(
                file_content=file_bytes,
                filename=filename,
                content_type=uploaded_file.content_type if uploaded_file else None
            )
        else:
            proc_result = document_processor.process_text(input_text or "")

        extracted_text = proc_result["text"]
        processing_metadata = {
            "source_type": proc_result["source_type"],
            "confidence": proc_result["confidence"],
            "warnings": proc_result["warnings"],
        }
        analysis_record.raw_text = extracted_text
        db.commit()
    except ValueError as val_err:
        elapsed = time.time() - start_time
        err_msg = str(val_err)
        report_service.mark_failed_report(db, analysis_id, err_msg, elapsed)
        return APIResponse(
            success=False,
            error=APIError(code="INVALID_INPUT", message=err_msg)
        )
    except Exception as proc_err:
        elapsed = time.time() - start_time
        err_msg = f"Document processing failed: {str(proc_err)}"
        report_service.mark_failed_report(db, analysis_id, err_msg, elapsed)
        return APIResponse(
            success=False,
            error=APIError(code="PROCESSING_ERROR", message=err_msg)
        )

    # Check for empty extracted text
    if not extracted_text.strip():
        elapsed = time.time() - start_time
        err_msg = "The document contains insufficient readable information."
        report_service.mark_failed_report(db, analysis_id, err_msg, elapsed)
        return APIResponse(
            success=False,
            error=APIError(code="INSUFFICIENT_TEXT", message=err_msg)
        )

    # AI Clinical Analysis
    try:
        structured_report = ai_service.analyze_clinical_document(
            document_text=extracted_text,
            source_metadata=processing_metadata
        )
    except AIServiceUnavailableError as ai_unavail:
        elapsed = time.time() - start_time
        report_service.mark_failed_report(db, analysis_id, ai_unavail.message, elapsed, extracted_text)
        return APIResponse(
            success=False,
            error=APIError(code=ai_unavail.code, message=ai_unavail.message)
        )
    except (AIRateLimitError, AITimeoutError, AIMalformedResponseError) as ai_err:
        elapsed = time.time() - start_time
        report_service.mark_failed_report(db, analysis_id, ai_err.message, elapsed, extracted_text)
        return APIResponse(
            success=False,
            error=APIError(code=ai_err.code, message=ai_err.message)
        )
    except Exception as unk_ai_err:
        elapsed = time.time() - start_time
        err_msg = f"Clinical review service error: {str(unk_ai_err)}"
        report_service.mark_failed_report(db, analysis_id, err_msg, elapsed, extracted_text)
        return APIResponse(
            success=False,
            error=APIError(code="AI_ERROR", message=err_msg)
        )

    # Persist and Finalize Report
    try:
        elapsed = time.time() - start_time
        completed_record = report_service.save_completed_report(
            db=db,
            analysis_id=analysis_id,
            structured_report=structured_report,
            elapsed_seconds=elapsed,
            raw_text=extracted_text
        )
        return APIResponse(
            success=True,
            data=AnalysisResponse.model_validate(completed_record)
        )
    except Exception as db_err:
        elapsed = time.time() - start_time
        err_msg = f"Failed to persist report: {str(db_err)}"
        report_service.mark_failed_report(db, analysis_id, err_msg, elapsed, extracted_text)
        return APIResponse(
            success=False,
            error=APIError(code="DATABASE_ERROR", message=err_msg)
        )


@router.get(
    "/analyses",
    response_model=APIResponse[List[AnalysisListItem]],
    summary="List previous clinical document reviews"
)
def list_analyses(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Returns list of previous clinical analyses with pagination and optional search."""
    query = db.query(Analysis)

    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(Analysis.status == status_filter.upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Analysis.original_filename.ilike(term),
                Analysis.report_summary.ilike(term),
                Analysis.id.ilike(term)
            )
        )

    query = query.order_by(desc(Analysis.created_at))
    items = query.offset(offset).limit(limit).all()

    return APIResponse(
        success=True,
        data=[AnalysisListItem.model_validate(item) for item in items]
    )


@router.get(
    "/analyses/{analysis_id}",
    response_model=APIResponse[AnalysisResponse],
    summary="Get full clinical review report by ID"
)
def get_analysis_by_id(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves complete report by analysis ID."""
    record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not record:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Clinical report not found.")
        )

    return APIResponse(
        success=True,
        data=AnalysisResponse.model_validate(record)
    )


@router.delete(
    "/analyses/{analysis_id}",
    response_model=APIResponse[dict],
    summary="Delete clinical review report by ID"
)
def delete_analysis_by_id(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Deletes an analysis record by ID."""
    record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not record:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Clinical report not found.")
        )

    try:
        db.delete(record)
        db.commit()
        logger.info(f"Deleted clinical report {analysis_id}")
        return APIResponse(
            success=True,
            data={"message": "Clinical report deleted successfully.", "id": analysis_id}
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting report {analysis_id}: {str(e)}")
        return APIResponse(
            success=False,
            error=APIError(code="DATABASE_ERROR", message="Failed to delete clinical report.")
        )
