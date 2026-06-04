# pdf_extractor.py
# --------------------------------------------------------------------------
# This file reads text out of a PDF file, one page at a time.
# It uses the pypdf library.
#
# NOTE: This only works for PDFs that contain real text. A PDF that is just
# scanned images of pages has no text to extract (that would need OCR).
# --------------------------------------------------------------------------

import io
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> list:
    """
    Read every page in a PDF and pull out its text.

    Parameter:
        file_bytes : the raw bytes of the uploaded file.

    Returns:
        A list of dictionaries, one per page, like:
        [{"number": 1, "text": "..."}, {"number": 2, "text": "..."}]
    """
    reader = PdfReader(io.BytesIO(file_bytes))

    pages_data = []

    # Loop over every page. enumerate(..., start=1) gives us page numbers.
    for page_number, page in enumerate(reader.pages, start=1):
        # extract_text() can return None if the page has no text, so we
        # use "or ''" to safely turn that into an empty string.
        text = page.extract_text() or ""

        pages_data.append({
            "number": page_number,
            "text": text.strip(),
        })

    return pages_data