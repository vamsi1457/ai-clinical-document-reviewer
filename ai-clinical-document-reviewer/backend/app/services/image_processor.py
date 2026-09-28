import io
from typing import Dict, Any, List
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
from app.services.ocr_service import extract_text_from_image
from app.utils.logger import logger


def preprocess_image_for_ocr(img: Image.Image) -> Image.Image:
    """Applies clean preprocessing to enhance text readability for OCR."""
    # Convert RGBA, P, or CMYK to RGB
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Resize if too small (OCR accuracy degrades on low-DPI images)
    w, h = img.size
    if w < 600 or h < 600:
        scale = max(600 / w, 600 / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    elif w > 3500 or h > 3500:
        # Downscale excessively large images to conserve memory
        scale = min(3500 / w, 3500 / h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    # Convert to grayscale for contrast adjustment
    gray = img.convert("L")
    
    # Mild contrast enhancement
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.4)
    
    return enhanced


def process_image(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Processes an uploaded clinical image, applies preprocessing, and runs OCR.
    
    Returns:
        {
            "text": str,
            "source_type": "image",
            "confidence": float,
            "warnings": list[str]
        }
    """
    logger.info(f"Processing image document: {filename} ({len(file_content)} bytes)")
    warnings: List[str] = []

    try:
        image = Image.open(io.BytesIO(file_content))
        image.load()  # Force load image data to catch truncation or corruption
    except (UnidentifiedImageError, OSError, ValueError) as e:
        logger.error(f"Corrupted or invalid image: {filename} - {str(e)}")
        raise ValueError("Corrupted image file. Unable to read image content.")

    # Image preprocessing
    try:
        processed_image = preprocess_image_for_ocr(image)
    except Exception as e:
        logger.warning(f"Image preprocessing warning: {str(e)}. Proceeding with original image.")
        warnings.append(f"Image preprocessing warning: {str(e)}")
        processed_image = image

    # Run OCR extraction
    text, confidence, ocr_warnings = extract_text_from_image(processed_image)
    warnings.extend(ocr_warnings)

    if not text.strip():
        warnings.append("OCR could not detect legible clinical text from the image.")
        confidence = 0.0

    logger.info(f"Image processing completed: {filename}, extracted {len(text)} chars, confidence: {confidence:.2f}")

    return {
        "text": text,
        "source_type": "image",
        "confidence": confidence,
        "warnings": warnings,
    }
