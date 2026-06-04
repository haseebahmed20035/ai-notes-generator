# ocr.py
# --------------------------------------------------------------------------
# This file does ONE job: take an image and read the text out of it (OCR).
# "OCR" = Optical Character Recognition. It uses the Tesseract engine,
# which is installed by the Dockerfile.
#
# Several other files use this helper (PDFs, PowerPoints, and plain images),
# so we keep it in one place.
# --------------------------------------------------------------------------

import io
import pytesseract
from PIL import Image


def ocr_image_bytes(image_bytes: bytes) -> str:
    """
    Read text out of an image.

    Parameter:
        image_bytes : the raw bytes of an image (PNG, JPG, etc.)

    Returns:
        The text found in the image (may be empty if none was found).
    """
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text.strip()