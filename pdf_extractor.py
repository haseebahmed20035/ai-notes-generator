import fitz
from ocr import ocr_image_bytes


OCR_DPI = 110
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 200


def extract_text_from_pdf(file_bytes: bytes, enable_ocr: bool = True) -> list:
    pages_data = []

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page_number, page in enumerate(document, start=1):
            parts = []

            normal_text = (page.get_text() or "").strip()

            if normal_text:
                parts.append(normal_text)

            if enable_ocr:
                for image_info in page.get_images(full=True):
                    try:
                        xref = image_info[0]
                        image_data = document.extract_image(xref)
                        image_bytes = image_data["image"]

                        width = image_data.get("width", 0)
                        height = image_data.get("height", 0)

                        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                            continue

                        image_text = ocr_image_bytes(image_bytes)

                        if image_text:
                            parts.append("[Image OCR]\n" + image_text)

                    except Exception:
                        pass

            if not normal_text and enable_ocr and not parts:
                try:
                    pixmap = page.get_pixmap(dpi=OCR_DPI)
                    image_bytes = pixmap.tobytes("png")

                    scanned_text = ocr_image_bytes(image_bytes)

                    if scanned_text:
                        parts.append(scanned_text)

                except Exception:
                    pass

            pages_data.append({
                "number": page_number,
                "text": "\n\n".join(parts).strip(),
            })

    return pages_data