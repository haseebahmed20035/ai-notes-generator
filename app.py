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

PPTX_EXTENSIONS = (".pptx",)
PDF_EXTENSIONS = (".pdf",)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")
SUPPORTED_EXTENSIONS = PPTX_EXTENSIONS + PDF_EXTENSIONS + IMAGE_EXTENSIONS

TASK_TO_PROMPT = {
    "Detailed Notes": notes_prompt,
    "Short Summary": summary_prompt,
    "Exam Questions": questions_prompt,
    "Solved Case Scenarios": case_scenario_prompt,
}

MAX_CHARS_PER_CHUNK = 14000


def detect_file_type(filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return extension.lower()


def is_supported(filename: str) -> bool:
    return detect_file_type(filename) in SUPPORTED_EXTENSIONS


def extract_content(filename: str, file_bytes: bytes, enable_ocr: bool = True) -> tuple:
    extension = detect_file_type(filename)

    if extension in PPTX_EXTENSIONS:
        items = extract_text_from_pptx(file_bytes, enable_ocr=enable_ocr)
        label = "Slide"

    elif extension in PDF_EXTENSIONS:
        items = extract_text_from_pdf(file_bytes, enable_ocr=enable_ocr)
        label = "Page"

    elif extension in IMAGE_EXTENSIONS:
        items = extract_text_from_image(file_bytes)
        label = "Image"

    else:
        raise ValueError(f"Cannot extract from file type '{extension}'.")

    combined_text = combine_items_text(items, label)
    return items, combined_text, label


def combine_items_text(items: list, label: str) -> str:
    parts = []

    for item in items:
        if item["text"]:
            parts.append(f"--- {label} {item['number']} ---\n{item['text']}")

    return "\n\n".join(parts)


def split_into_chunks(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> list:
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


def _run_single(task_name: str, text: str) -> str:
    prompt_builder = TASK_TO_PROMPT.get(task_name)

    if prompt_builder is None:
        raise ValueError(f"Unknown task: '{task_name}'.")

    return ask_ai(prompt_builder(text))


def run_task(task_name: str, content_text: str, on_progress=None) -> str:
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