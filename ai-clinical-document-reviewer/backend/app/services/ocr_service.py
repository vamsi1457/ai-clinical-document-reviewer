import os
import shutil
from typing import Tuple, List, Optional
from PIL import Image
import numpy as np
from app.config import settings
from app.utils.logger import logger

# Try configuring Tesseract path if available
TESSERACT_AVAILABLE = False
try:
    import pytesseract

    # Check specified custom path, or common Windows paths, or system PATH
    candidates = [
        settings.TESSERACT_CMD,
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        shutil.which("tesseract"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            pytesseract.pytesseract.tesseract_cmd = c
            TESSERACT_AVAILABLE = True
            logger.info(f"Tesseract OCR found at: {c}")
            break
    if not TESSERACT_AVAILABLE and shutil.which("tesseract"):
        TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None

# RapidOCR / PaddleOCR ONNX engine
RAPID_OCR_ENGINE = None
try:
    from rapidocr import RapidOCR
    RAPID_OCR_ENGINE = RapidOCR()
    logger.info("RapidOCR (PaddleOCR ONNX engine) initialized successfully.")
except Exception as e:
    logger.warning(f"RapidOCR initialization notice: {str(e)}")


def extract_text_from_image(image: Image.Image) -> Tuple[str, float, List[str]]:
    """Extracts text from a PIL Image using available OCR engines.
    
    Returns:
        (extracted_text, confidence_score_0_to_1, warnings_list)
    """
    warnings: List[str] = []
    text = ""
    confidence = 0.0

    # Engine selection preference based on settings or availability
    preferred = settings.OCR_ENGINE.lower()
    
    # 1. RapidOCR / PaddleOCR attempt
    if (preferred in ["auto", "rapidocr", "paddleocr"] and RAPID_OCR_ENGINE is not None) or not TESSERACT_AVAILABLE:
        try:
            img_np = np.array(image.convert("RGB"))
            out = RAPID_OCR_ENGINE(img_np)
            if out and hasattr(out, "txts") and out.txts:
                text_lines = [t.strip() for t in out.txts if t and t.strip()]
                text = "\n".join(text_lines)
                if hasattr(out, "scores") and out.scores:
                    scores = [float(s) for s in out.scores if s is not None]
                    confidence = float(np.mean(scores)) if scores else 0.85
                else:
                    confidence = 0.85
                logger.info(f"RapidOCR extracted {len(text_lines)} lines, avg confidence: {confidence:.2f}")
                return text, confidence, warnings
        except Exception as e:
            logger.warning(f"RapidOCR extraction failed: {str(e)}, attempting fallback if available.")
            warnings.append(f"RapidOCR engine warning: {str(e)}")

    # 2. PyTesseract attempt
    if TESSERACT_AVAILABLE and pytesseract is not None:
        try:
            # Extract text
            raw_text = pytesseract.image_to_string(image)
            text = raw_text.strip()
            
            # Extract word confidences via image_to_data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confs = [float(c) for c in data.get("conf", []) if str(c).replace("-", "").isdigit() and float(c) > 0]
            confidence = (sum(confs) / (len(confs) * 100.0)) if confs else (0.75 if text else 0.0)
            
            logger.info(f"Tesseract OCR extracted {len(text)} characters, confidence: {confidence:.2f}")
            return text, confidence, warnings
        except Exception as e:
            logger.warning(f"Tesseract OCR execution error: {str(e)}")
            warnings.append(f"Tesseract OCR execution warning: {str(e)}")

    # 3. If neither engine produced usable text
    if not text:
        warnings.append("OCR produced no usable text. The document may be blank, illegible, or degraded.")
        return "", 0.0, warnings

    return text, confidence, warnings
