from typing import Optional
from app.config import settings


def validate_clinical_text(text: Optional[str]) -> str:
    """Validates submitted clinical text.
    
    Raises ValueError with specific user-friendly message.
    """
    if not text or not text.strip():
        raise ValueError("Please enter clinical text before submitting.")
    
    cleaned = text.strip()
    if len(cleaned) < 5:
        raise ValueError("Please provide sufficient clinical text to review (at least 5 characters).")
    
    return cleaned


def validate_file_upload(
    filename: Optional[str],
    content: bytes,
    content_type: Optional[str] = None
) -> str:
    """Validates uploaded document file (PDF or Image).
    
    Validates file size, non-empty content, allowed extension, and magic byte signature.
    Returns normalized document format: 'pdf', 'png', 'jpg', or 'jpeg'.
    """
    if not filename:
        raise ValueError("Filename is missing.")
    
    # 1. Empty check
    if not content or len(content) == 0:
        raise ValueError("Uploaded file is empty.")
    
    # 2. File size check
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise ValueError(f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB.")
    
    # 3. Extension check
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Please upload PDF, PNG, JPG or JPEG.")
    
    # 4. Magic bytes validation (do not trust extension alone)
    if ext == "pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Corrupted or invalid PDF file header.")
    elif ext == "png":
        if not content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Corrupted or invalid PNG image file.")
    elif ext in ["jpg", "jpeg"]:
        if not (content.startswith(b"\xff\xd8\xff") or content.startswith(b"\xff\xd8")):
            raise ValueError("Corrupted or invalid JPEG image file.")
            
    return ext
