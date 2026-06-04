# agent.py
# --------------------------------------------------------------------------
# This file is the "brain" of the project, the AGENT.
#
# An agent follows a simple loop:  PERCEIVE  ->  DECIDE  ->  ACT
#   PERCEIVE : look at the uploaded file (what type is it?)
#   DECIDE   : choose what to do (which extractor? which AI task?)
#   ACT      : run the extraction and the chosen AI task
# --------------------------------------------------------------------------

import os

from ai_engine import ask_ai
from pptx_extractor import extract_text_from_pptx
from pdf_extractor import extract_text_from_pdf
from prompts import (
    notes_prompt,
    summary_prompt,
    questions_prompt,
    case_scenario_prompt,
)

# File types we can read. We now support BOTH PowerPoint and PDF.
SUPPORTED_EXTENSIONS = (".pptx", ".pdf")

# The set of tasks the agent knows how to perform.
TASK_TO_PROMPT = {
    "Detailed Notes": notes_prompt,
    "Short Summary": summary_prompt,
    "Exam Questions": questions_prompt,
    "Solved Case Scenarios": case_scenario_prompt,
}


# ---------------------------- PERCEIVE -----------------------------------

def detect_file_type(filename: str) -> str:
    """Return the lowercase file extension, e.g. '.pptx' or '.pdf'."""
    _, extension = os.path.splitext(filename)
    return extension.lower()


def is_supported(filename: str) -> bool:
    """Decide whether we are able to read this file type."""
    return detect_file_type(filename) in SUPPORTED_EXTENSIONS


# --------------------------- DECIDE + ACT (extraction) -------------------

def extract_content(filename: str, file_bytes: bytes) -> tuple:
    """
    The agent looks at the file type and DECIDES which extractor to use.

    Returns:
        items        : list of {"number": int, "text": str}
        combined_text: all the text joined into one string for the AI
        label        : "Slide" for PowerPoint, "Page" for PDF
    """
    extension = detect_file_type(filename)

    if extension == ".pptx":
        items = extract_text_from_pptx(file_bytes)
        label = "Slide"
    elif extension == ".pdf":
        items = extract_text_from_pdf(file_bytes)
        label = "Page"
    else:
        # Should not happen because we check is_supported() first.
        raise ValueError(f"Cannot extract from file type '{extension}'.")

    combined_text = combine_items_text(items, label)
    return items, combined_text, label


def combine_items_text(items: list, label: str) -> str:
    """Join all slides/pages into ONE string to send to the AI."""
    parts = []
    for item in items:
        if item["text"]:
            parts.append(f"--- {label} {item['number']} ---\n{item['text']}")
    return "\n\n".join(parts)


# --------------------------- DECIDE + ACT (AI task) ----------------------

def run_task(task_name: str, content_text: str) -> str:
    """
    The agent picks the correct prompt for the chosen task, then asks the AI.
    """
    prompt_builder = TASK_TO_PROMPT.get(task_name)

    if prompt_builder is None:
        raise ValueError(f"Unknown task: '{task_name}'.")

    prompt = prompt_builder(content_text)
    return ask_ai(prompt)