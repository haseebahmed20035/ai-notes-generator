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

import fitz  # PyMuPDF
from ocr import ocr_image_bytes


def extract_text_from_pdf(file_bytes: bytes) -> list:
    """
    Read every page in a PDF and pull out its text (using OCR if needed).

    Returns:
        A list of dictionaries, one per page, like:
        [{"number": 1, "text": "..."}, {"number": 2, "text": "..."}]
    """
    pages_data = []

    # Open the PDF straight from the uploaded bytes.
    with fitz.open(stream=file_bytes, filetype="pdf") as document:

        for page_number, page in enumerate(document, start=1):

            # STEP 1: try to read the real text on the page.
            text = (page.get_text() or "").strip()

            # STEP 2: if there's no real text, the page is an image, so OCR it.
            if not text:
                # Render the page to a picture at a readable resolution.
                pixmap = page.get_pixmap(dpi=200)
                image_bytes = pixmap.tobytes("png")
                text = ocr_image_bytes(image_bytes)

            pages_data.append({
                "number": page_number,
                "text": text,
            })

    return pages_data