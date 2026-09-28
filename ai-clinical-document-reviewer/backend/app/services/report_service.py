import time
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.report import StructuredClinicalReport
from app.schemas.analysis import AnalysisResponse
from app.utils.logger import logger


class ReportService:
    """Service to normalize, assemble, and persist clinical reports in the database."""

    @staticmethod
    def normalize_report(report: StructuredClinicalReport) -> StructuredClinicalReport:
        """Ensures all clinical report fields are properly defaulted and normalized."""
        # Ensure summary is present and concise
        if not report.report_summary or not report.report_summary.strip():
            concerns = ", ".join(report.clinical_concerns[:2]) if report.clinical_concerns else "None documented"
            diag = ", ".join([d.condition for d in report.diagnoses[:2]]) if report.diagnoses else "None documented"
            report.report_summary = f"Clinical review completed. Primary diagnoses: {diag}. Primary concerns: {concerns}."

        # Ensure allergy consistency rule: if allergies empty, add Not documented entry
        if not report.allergies:
            from app.schemas.report import AllergyItem
            report.allergies = [AllergyItem(allergy="Not documented", reaction="Not documented")]

        return report

    @staticmethod
    def save_completed_report(
        db: Session,
        analysis_id: str,
        structured_report: StructuredClinicalReport,
        elapsed_seconds: float,
        raw_text: Optional[str] = None
    ) -> Analysis:
        """Persists a successful clinical report to the database."""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ValueError(f"Analysis record {analysis_id} not found.")

            normalized = ReportService.normalize_report(structured_report)
            analysis.status = AnalysisStatus.COMPLETED.value
            analysis.structured_report = normalized.model_dump()
            analysis.report_summary = normalized.report_summary
            analysis.processing_time = round(elapsed_seconds, 2)
            analysis.error_message = None
            if raw_text:
                analysis.raw_text = raw_text

            db.commit()
            db.refresh(analysis)
            logger.info(f"Analysis {analysis_id} successfully marked COMPLETED in {analysis.processing_time}s.")
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist completed report for {analysis_id}: {str(e)}")
            raise

    @staticmethod
    def mark_failed_report(
        db: Session,
        analysis_id: str,
        error_message: str,
        elapsed_seconds: float = 0.0,
        raw_text: Optional[str] = None
    ) -> Analysis:
        """Marks an analysis record as FAILED with the error reason."""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                logger.error(f"Cannot mark failed: Analysis {analysis_id} not found.")
                return None

            analysis.status = AnalysisStatus.FAILED.value
            analysis.error_message = error_message
            analysis.processing_time = round(elapsed_seconds, 2)
            if raw_text:
                analysis.raw_text = raw_text

            db.commit()
            db.refresh(analysis)
            logger.warning(f"Analysis {analysis_id} marked FAILED: {error_message}")
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record failure for analysis {analysis_id}: {str(e)}")
            raise


report_service = ReportService()
