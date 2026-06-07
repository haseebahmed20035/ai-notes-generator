# pdf_extractor.py
# --------------------------------------------------------------------------
# This file reads text out of a PDF, one page at a time.
#
# It is smart about it:
#   1. First it tries to grab the real text from the page.
#   2. If the page has NO real text (a scanned / image page), it turns the
#      page into an image and runs OCR on it.
#
# It uses PyMuPDF (imported as "fitz") which is fast and reliable.
# --------------------------------------------------------------------------

import fitz
from ocr import ocr_image_bytes


def extract_text_from_pdf(file_bytes: bytes, enable_ocr: bool = True) -> list:
    pages_data = []

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page_number, page in enumerate(document, start=1):
            text = (page.get_text() or "").strip()

            if enable_ocr and not text:
                pixmap = page.get_pixmap(dpi=200)
                image_bytes = pixmap.tobytes("png")
                text = ocr_image_bytes(image_bytes)

            pages_data.append({
                "number": page_number,
                "text": text,
            })

    return pages_data