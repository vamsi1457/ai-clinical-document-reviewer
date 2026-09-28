import io
from typing import Dict, Any, List
import fitz  # PyMuPDF
from PIL import Image
from app.services.ocr_service import extract_text_from_image
from app.utils.logger import logger


def process_pdf(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Processes an uploaded PDF using PyMuPDF.
    
    First attempts native text extraction. If pages appear scanned or have
    insufficient text, falls back to OCR rendering on page pixmaps.
    
    Handles:
    - Empty PDF
    - Corrupted PDF
    - Password-protected PDF
    - Scanned pages
    """
    logger.info(f"Processing PDF document: {filename} ({len(file_content)} bytes)")
    warnings: List[str] = []

    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
    except Exception as e:
        logger.error(f"Failed to open PDF {filename}: {str(e)}")
        raise ValueError("Corrupted or unreadable PDF document.")

    # 1. Password-protected check
    if doc.is_encrypted or doc.needs_pass:
        doc.close()
        raise ValueError("Password-protected PDF files cannot be processed.")

    # 2. Empty PDF check
    page_count = doc.page_count
    if page_count == 0:
        doc.close()
        raise ValueError("PDF document is empty (0 pages).")

    # 3. Native digital text extraction attempt
    page_texts: List[str] = []
    scanned_pages: List[int] = []

    for page_idx in range(page_count):
        try:
            page = doc.load_page(page_idx)
            text = page.get_text("text").strip()
            if len(text) >= 40:
                page_texts.append(text)
            else:
                scanned_pages.append(page_idx)
        except Exception as e:
            logger.warning(f"Error reading page {page_idx + 1}: {str(e)}")
            scanned_pages.append(page_idx)

    total_chars = sum(len(t) for t in page_texts)
    
    # If all or most pages provided sufficient native digital text
    if len(scanned_pages) == 0 and total_chars > 50:
        full_text = "\n\n".join(page_texts)
        doc.close()
        logger.info(f"PDF native text extracted successfully: {page_count} pages, {total_chars} chars.")
        return {
            "text": full_text,
            "source_type": "pdf",
            "confidence": 1.0,
            "warnings": warnings,
        }

    # 4. Scanned PDF or mixed document - execute OCR on scanned pages
    logger.info(f"PDF contains scanned or low-text pages ({len(scanned_pages)}/{page_count}). Initiating OCR...")
    warnings.append("Document appears scanned or has rasterized pages; text was extracted using OCR.")

    ocr_page_texts: List[str] = []
    confidences: List[float] = []

    for page_idx in range(page_count):
        if page_idx not in scanned_pages and page_idx < len(page_texts):
            ocr_page_texts.append(page_texts[page_idx])
            confidences.append(1.0)
        else:
            try:
                page = doc.load_page(page_idx)
                # Render page at 200 DPI for high OCR accuracy
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_ocr_text, page_conf, page_warns = extract_text_from_image(img)
                if page_ocr_text.strip():
                    ocr_page_texts.append(page_ocr_text.strip())
                confidences.append(page_conf)
                warnings.extend(page_warns)
            except Exception as e:
                logger.error(f"Failed to OCR page {page_idx + 1}: {str(e)}")
                warnings.append(f"Failed to extract text from page {page_idx + 1}: {str(e)}")

    doc.close()

    full_text = "\n\n".join(ocr_page_texts).strip()
    avg_confidence = (sum(confidences) / len(confidences)) if confidences else 0.0

    if not full_text:
        warnings.append("The document contains insufficient readable information.")
        avg_confidence = 0.0
    elif avg_confidence < 0.6:
        warnings.append("We could not reliably extract text from this document.")

    logger.info(f"PDF processing completed: {len(full_text)} characters, confidence: {avg_confidence:.2f}")

    return {
        "text": full_text,
        "source_type": "pdf",
        "confidence": avg_confidence,
        "warnings": list(set(warnings)),
    }
