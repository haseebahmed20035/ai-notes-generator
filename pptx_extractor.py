# pptx_extractor.py
# --------------------------------------------------------------------------
# This file reads text out of a PowerPoint (.pptx) file, one slide at a time.
# It uses the python-pptx library.
#
# IMPORTANT: python-pptx can only read the NEWER .pptx format.
# It CANNOT read the old .ppt format.
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
        [{"number": 1, "text": "..."}, {"number": 2, "text": "..."}]
    """
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

        slides_data.append({
            "number": slide_number,
            "text": "\n".join(lines),
        })

    return slides_data