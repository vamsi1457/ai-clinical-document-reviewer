import pytest
from app.utils.validators import validate_clinical_text, validate_file_upload
from app.config import settings


def test_validate_clinical_text_valid():
    """Valid text should return normalized trimmed text."""
    text = "  Patient presents with fever and cough for two days.  "
    result = validate_clinical_text(text)
    assert result == "Patient presents with fever and cough for two days."


def test_validate_clinical_text_empty():
    """Empty or whitespace text must raise specific validation error."""
    with pytest.raises(ValueError, match="Please enter clinical text before submitting."):
        validate_clinical_text("")

    with pytest.raises(ValueError, match="Please enter clinical text before submitting."):
        validate_clinical_text("   \n   \t  ")


def test_validate_clinical_text_too_short():
    """Text with fewer than 5 characters should raise error."""
    with pytest.raises(ValueError, match="at least 5 characters"):
        validate_clinical_text("pain")


def test_validate_file_upload_unsupported_type():
    """Unsupported extensions should be rejected."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        validate_file_upload("medical_report.docx", b"some binary data")


def test_validate_file_upload_empty_file():
    """Empty file bytes should be rejected."""
    with pytest.raises(ValueError, match="Uploaded file is empty"):
        validate_file_upload("document.pdf", b"")


def test_validate_file_upload_file_too_large():
    """Files exceeding size limit must be rejected."""
    oversized = b"0" * (settings.MAX_FILE_SIZE_MB * 1024 * 1024 + 100)
    with pytest.raises(ValueError, match="File size exceeds maximum limit"):
        validate_file_upload("scan.png", oversized)


def test_validate_file_upload_corrupted_pdf_header():
    """PDF with invalid magic header bytes should be rejected."""
    with pytest.raises(ValueError, match="Corrupted or invalid PDF"):
        validate_file_upload("document.pdf", b"INVALID_HEADER_DATA_12345")


def test_validate_file_upload_valid_pdf_signature():
    """Valid PDF magic header should pass validation."""
    valid_pdf_bytes = b"%PDF-1.4\n%synthetic test content"
    ext = validate_file_upload("valid_record.pdf", valid_pdf_bytes)
    assert ext == "pdf"


def test_validate_file_upload_valid_png_signature():
    """Valid PNG magic header should pass validation."""
    valid_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    ext = validate_file_upload("scan.png", valid_png_bytes)
    assert ext == "png"
