# agent.py
# --------------------------------------------------------------------------
# This file is the "brain" of the project, the AGENT.
#
# An agent follows a simple loop:  PERCEIVE  ->  DECIDE  ->  ACT
#   PERCEIVE : look at the uploaded file (what type is it?)
#   DECIDE   : choose which reader to use, and which AI task to run
#   ACT      : run the extraction and the chosen AI task
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


# ---------------------------- PERCEIVE -----------------------------------

def detect_file_type(filename: str) -> str:
    """Return the lowercase file extension, e.g. '.pptx', '.pdf', '.png'."""
    _, extension = os.path.splitext(filename)
    return extension.lower()


def is_supported(filename: str) -> bool:
    """Decide whether we are able to read this file type."""
    return detect_file_type(filename) in SUPPORTED_EXTENSIONS


# --------------------------- DECIDE + ACT (extraction) -------------------

def extract_content(filename: str, file_bytes: bytes) -> tuple:
    """
    The agent looks at the file type and DECIDES which reader to use.

    Returns:
        items        : list of {"number": int, "text": str}
        combined_text: all the text joined into one string for the AI
        label        : "Slide", "Page", or "Image"
    """
    extension = detect_file_type(filename)

    if extension in PPTX_EXTENSIONS:
        items = extract_text_from_pptx(file_bytes)
        label = "Slide"
    elif extension in PDF_EXTENSIONS:
        items = extract_text_from_pdf(file_bytes)
        label = "Page"
    elif extension in IMAGE_EXTENSIONS:
        items = extract_text_from_image(file_bytes)
        label = "Image"
    else:
        raise ValueError(f"Cannot extract from file type '{extension}'.")

    combined_text = combine_items_text(items, label)
    return items, combined_text, label


def combine_items_text(items: list, label: str) -> str:
    """Join all slides/pages/images into ONE string to send to the AI."""
    parts = []
    for item in items:
        if item["text"]:
            parts.append(f"--- {label} {item['number']} ---\n{item['text']}")
    return "\n\n".join(parts)


# --------------------------- DECIDE + ACT (AI task) ----------------------

def run_task(task_name: str, content_text: str) -> str:
    """The agent picks the right prompt for the task, then asks the AI."""
    prompt_builder = TASK_TO_PROMPT.get(task_name)
    if prompt_builder is None:
        raise ValueError(f"Unknown task: '{task_name}'.")
    prompt = prompt_builder(content_text)
    return ask_ai(prompt)