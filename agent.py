# agent.py
# --------------------------------------------------------------------------
# This file is the "brain" of the project, the AGENT.
#
# An agent follows a simple loop:  PERCEIVE  ->  DECIDE  ->  ACT
#   PERCEIVE : look at the uploaded file (what type is it?)
#   DECIDE   : choose which reader to use, and which AI task to run
#   ACT      : run the extraction and the chosen AI task
#
# For LARGE files, the agent breaks the text into smaller parts ("chunks")
# and runs the AI on each part, so nothing gets skipped.
# --------------------------------------------------------------------------

import os

from ai_engine import ask_ai
from pptx_extractor import extract_text_from_pptx
from pdf_extractor import extract_text_from_pdf
from image_extractor import extract_text_from_image
from prompts import (
    notes_prompt,
    summary_prompt,
    questions_prompt,
    case_scenario_prompt,
)

# File types we can read: PowerPoint, PDF, and common image formats.
PPTX_EXTENSIONS = (".pptx",)
PDF_EXTENSIONS = (".pdf",)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")
SUPPORTED_EXTENSIONS = PPTX_EXTENSIONS + PDF_EXTENSIONS + IMAGE_EXTENSIONS

# The set of tasks the agent knows how to perform.
TASK_TO_PROMPT = {
    "Detailed Notes": notes_prompt,
    "Short Summary": summary_prompt,
    "Exam Questions": questions_prompt,
    "Solved Case Scenarios": case_scenario_prompt,
}

# How big each "chunk" of text can be before we split it.
MAX_CHARS_PER_CHUNK = 14000


# ---------------------------- PERCEIVE -----------------------------------

def detect_file_type(filename: str) -> str:
    """Return the lowercase file extension, e.g. '.pptx', '.pdf', '.png'."""
    _, extension = os.path.splitext(filename)
    return extension.lower()


def is_supported(filename: str) -> bool:
    """Decide whether we are able to read this file type."""
    return detect_file_type(filename) in SUPPORTED_EXTENSIONS


# --------------------------- DECIDE + ACT (extraction) -------------------

def extract_content(
    filename: str,
    file_bytes: bytes,
    enable_ocr: bool = True,
) -> tuple:
    """
    The agent looks at the file type and DECIDES which reader to use.

    Parameter:
        enable_ocr:
            True  = also read text inside images/scanned pages
            False = only read normal selectable text, faster

    Returns:
        items        : list of {"number": int, "text": str}
        combined_text: all the text joined into one string
        label        : "Slide", "Page", or "Image"
    """
    extension = detect_file_type(filename)

    if extension in PPTX_EXTENSIONS:
        items = extract_text_from_pptx(
            file_bytes,
            enable_ocr=enable_ocr,
        )
        label = "Slide"

    elif extension in PDF_EXTENSIONS:
        items = extract_text_from_pdf(
            file_bytes,
            enable_ocr=enable_ocr,
        )
        label = "Page"

    elif extension in IMAGE_EXTENSIONS:
        # Image files always need OCR because image has no selectable text.
        items = extract_text_from_image(file_bytes)
        label = "Image"

    else:
        raise ValueError(f"Cannot extract from file type '{extension}'.")

    combined_text = combine_items_text(items, label)
    return items, combined_text, label


def combine_items_text(items: list, label: str) -> str:
    """Join all slides/pages/images into ONE string."""
    parts = []

    for item in items:
        if item["text"]:
            parts.append(f"--- {label} {item['number']} ---\n{item['text']}")

    return "\n\n".join(parts)


# --------------------------- CHUNKING (for large files) ------------------

def split_into_chunks(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> list:
    """
    Split the text into smaller chunks without breaking slides/pages apart.
    """
    blocks = text.split("\n\n")
    chunks = []
    current = ""

    for block in blocks:
        if current and (len(current) + len(block) + 2) > max_chars:
            chunks.append(current)
            current = block
        else:
            current = block if not current else current + "\n\n" + block

    if current:
        chunks.append(current)

    return chunks


# --------------------------- DECIDE + ACT (AI task) ----------------------

def _run_single(task_name: str, text: str) -> str:
    """Run one AI task on one piece of text."""
    prompt_builder = TASK_TO_PROMPT.get(task_name)

    if prompt_builder is None:
        raise ValueError(f"Unknown task: '{task_name}'.")

    return ask_ai(prompt_builder(text))


def run_task(task_name: str, content_text: str, on_progress=None) -> str:
    """
    Run the chosen AI task on the content.

    For small content, this is a single AI call.
    For large content, it splits into chunks, runs each one, and combines them.
    """
    chunks = split_into_chunks(content_text)

    if len(chunks) <= 1:
        if on_progress:
            on_progress(1, 1)

        return _run_single(task_name, content_text)

    parts = []
    total = len(chunks)

    for index, chunk in enumerate(chunks, start=1):
        if on_progress:
            on_progress(index, total)

        try:
            result = _run_single(task_name, chunk)
            parts.append(result)

        except Exception as error:
            parts.append(f"[Part {index} could not be generated: {error}]")

    combined = "\n\n".join(parts)

    if task_name == "Short Summary":
        try:
            return _run_single("Short Summary", combined)
        except Exception:
            return combined

    return combined