import fitz
from ocr import ocr_image_bytes


OCR_DPI = 120


def extract_text_from_pdf(file_bytes: bytes) -> list:
    pages_data = []

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        total_pages = len(document)

        for page_number, page in enumerate(document, start=1):
            text = (page.get_text() or "").strip()

            # OCR only if page has no selectable text
            if not text:
                pixmap = page.get_pixmap(dpi=OCR_DPI)
                image_bytes = pixmap.tobytes("png")
                text = ocr_image_bytes(image_bytes)

            pages_data.append(
                {
                    "number": page_number,
                    "text": text,
                }
            )

    return pages_data