import os
import pytest
from app.services.document_processor import document_processor
from app.services.pdf_processor import process_pdf
from app.services.image_processor import process_image

SAMPLE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "sample_data")
)


def test_text_document_processing():
    """Valid text document processing should return standardized payload."""
    raw = "Patient: Jane Doe, Age: 34.\nSymptoms: Persistent cough and low-grade fever."
    result = document_processor.process_text(raw)
    assert result["source_type"] == "text"
    assert result["confidence"] == 1.0
    assert "Jane Doe" in result["text"]
    assert len(result["warnings"]) == 0


def test_pdf_extraction_real_sample():
    """Verify PyMuPDF text extraction from synthetic PDF sample."""
    pdf_path = os.path.join(SAMPLE_DIR, "synthetic_clinical_report.pdf")
    assert os.path.exists(pdf_path), "synthetic_clinical_report.pdf must exist"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    result = process_pdf(pdf_bytes, "synthetic_clinical_report.pdf")
    assert result["source_type"] == "pdf"
    assert result["confidence"] > 0.8
    assert "Sarah Jenkins" in result["text"]
    assert "Sumatriptan" in result["text"]


def test_pdf_corrupted_handling():
    """Corrupted PDF stream should raise clear ValueError."""
    corrupted_bytes = b"%PDF-1.4 but then completely corrupted non-pdf data"
    with pytest.raises(ValueError, match="Corrupted or unreadable PDF"):
        process_pdf(corrupted_bytes, "corrupted.pdf")


def test_image_ocr_real_sample():
    """Verify Image OCR extraction from synthetic image sample."""
    img_path = os.path.join(SAMPLE_DIR, "synthetic_clinical_image.png")
    assert os.path.exists(img_path), "synthetic_clinical_image.png must exist"

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    result = process_image(img_bytes, "synthetic_clinical_image.png")
    assert result["source_type"] == "image"
    assert result["confidence"] > 0.0
    # OCR should capture main terms from generated image
    extracted_lower = result["text"].lower()
    assert any(term in extracted_lower for term in ["robert", "martinez", "edema", "vitals", "furosemide", "blood"])


def test_image_corrupted_handling():
    """Corrupted image bytes should raise ValueError."""
    with pytest.raises(ValueError, match="Corrupted image file"):
        process_image(b"\x89PNG\r\n\x1a\ncorrupted_image_data_here", "corrupt.png")
