import unicodedata
from typing import Dict, Any, Optional
from app.utils.validators import validate_clinical_text, validate_file_upload
from app.services.pdf_processor import process_pdf
from app.services.image_processor import process_image
from app.utils.logger import logger


def normalize_text(text: str) -> str:
    """Normalizes unicode characters, line breaks, and trailing whitespaces."""
    # Normalize unicode (NFKC)
    normalized = unicodedata.normalize("NFKC", text)
    # Standardize line endings
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    # Clean up repetitive excessive empty lines
    lines = [line.strip() for line in normalized.split("\n")]
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
    return "\n".join(cleaned_lines).strip()


class DocumentProcessor:
    """Central document processing service for text, PDF, and image documents."""

    @staticmethod
    def process_text(text: str) -> Dict[str, Any]:
        """Processes and normalizes raw clinical text input."""
        logger.info(f"Processing clinical text input ({len(text)} characters)")
        validated = validate_clinical_text(text)
        normalized = normalize_text(validated)
        return {
            "text": normalized,
            "source_type": "text",
            "confidence": 1.0,
            "warnings": [],
        }

    @staticmethod
    def process_file(file_content: bytes, filename: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Processes an uploaded file (PDF or Image)."""
        logger.info(f"Routing document file for processing: {filename}")
        doc_format = validate_file_upload(filename, file_content, content_type)

        if doc_format == "pdf":
            result = process_pdf(file_content, filename)
        elif doc_format in ["png", "jpg", "jpeg"]:
            result = process_image(file_content, filename)
        else:
            raise ValueError(f"Unsupported document format: {doc_format}")

        result["text"] = normalize_text(result["text"])
        return result


document_processor = DocumentProcessor()
