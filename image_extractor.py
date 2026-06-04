# image_extractor.py
# --------------------------------------------------------------------------
# This file handles when the user uploads a plain image (a photo or
# screenshot of a slide/notes). It simply runs OCR on the whole image.
# --------------------------------------------------------------------------

from ocr import ocr_image_bytes


def extract_text_from_image(file_bytes: bytes) -> list:
    """
    Read text out of a single uploaded image.

    Returns:
        A list with one dictionary (one "page"), like:
        [{"number": 1, "text": "..."}]
    """
    text = ocr_image_bytes(file_bytes)
    return [{"number": 1, "text": text}]