# pptx_extractor.py
# --------------------------------------------------------------------------
# This file is responsible for ONE job: reading text out of a PowerPoint
# (.pptx) file. It uses the python-pptx library.
#
# IMPORTANT: python-pptx can only read the NEWER .pptx format.
# It CANNOT read the old .ppt format. We handle that politely elsewhere.
# --------------------------------------------------------------------------

import io
from pptx import Presentation


def extract_text_from_pptx(file_bytes: bytes) -> list:
    """
    Read every slide in a .pptx file and pull out its text.

    Parameter:
        file_bytes : the raw bytes of the uploaded file.

    Returns:
        A list of dictionaries, one per slide, like:
        [{"slide_number": 1, "text": "..."}, {"slide_number": 2, "text": "..."}]
    """
    # Wrap the raw bytes in a file-like object so python-pptx can open it.
    presentation = Presentation(io.BytesIO(file_bytes))

    slides_data = []

    # Loop over every slide. enumerate(..., start=1) gives us slide numbers.
    for slide_number, slide in enumerate(presentation.slides, start=1):
        lines = []

        # Each slide is made of "shapes" (text boxes, titles, tables, etc.)
        for shape in slide.shapes:

            # 1) Normal text boxes / titles
            if shape.has_text_frame:
                text = shape.text_frame.text
                if text and text.strip():
                    lines.append(text.strip())

            # 2) Tables (slides often contain tables of data)
            if shape.has_table:
                for row in shape.table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    row_text = " | ".join(c for c in cells if c)
                    if row_text:
                        lines.append(row_text)

        # Join all the pieces of this slide into one block of text.
        slide_text = "\n".join(lines)

        slides_data.append({
            "slide_number": slide_number,
            "text": slide_text,
        })

    return slides_data


def combine_slides_text(slides_data: list) -> str:
    """
    Turn the list of slide dictionaries into ONE big string.
    This combined string is what we feed to the AI.
    """
    parts = []
    for slide in slides_data:
        if slide["text"]:
            parts.append(f"--- Slide {slide['slide_number']} ---\n{slide['text']}")
    return "\n\n".join(parts)