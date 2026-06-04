# agent.py
# --------------------------------------------------------------------------
# This file is the "brain" of the project, the AGENT.
#
# An agent follows a simple loop:  PERCEIVE  ->  DECIDE  ->  ACT
#   PERCEIVE : look at the uploaded file (what type is it?)
#   DECIDE   : choose what to do (extract? which AI task?)
#   ACT      : run the extraction and the chosen AI task
#
# All of those decisions live here, separated from the user interface.
# --------------------------------------------------------------------------

import os

from ai_engine import ask_ai
from prompts import (
    notes_prompt,
    summary_prompt,
    questions_prompt,
    mcq_prompt,
)

# File types we can actually read. python-pptx only supports .pptx.
SUPPORTED_EXTENSIONS = (".pptx",)

# The set of tasks the agent knows how to perform.
# We map a friendly task name to the prompt-builder function for it.
TASK_TO_PROMPT = {
    "Detailed Notes": notes_prompt,
    "Short Summary": summary_prompt,
    "Exam Questions": questions_prompt,
    "MCQs with Answers": mcq_prompt,
}


# ---------------------------- PERCEIVE -----------------------------------

def detect_file_type(filename: str) -> str:
    """Return the lowercase file extension, e.g. '.pptx'."""
    _, extension = os.path.splitext(filename)
    return extension.lower()


def is_supported(filename: str) -> bool:
    """Decide whether we are able to read this file type."""
    return detect_file_type(filename) in SUPPORTED_EXTENSIONS


# ----------------------------- DECIDE + ACT ------------------------------

def run_task(task_name: str, slide_text: str) -> str:
    """
    The agent decides which prompt to build based on the chosen task,
    then asks the AI to perform it.

    Parameters:
        task_name  : one of the keys in TASK_TO_PROMPT.
        slide_text : the combined text from all slides.

    Returns:
        The AI-generated result as a string.
    """
    # DECIDE: pick the correct prompt builder for the requested task.
    prompt_builder = TASK_TO_PROMPT.get(task_name)

    if prompt_builder is None:
        # The agent does not know this task; fail clearly.
        raise ValueError(f"Unknown task: '{task_name}'.")

    # Build the full prompt with the slide text inserted.
    prompt = prompt_builder(slide_text)

    # ACT: send the prompt to the AI and return its answer.
    return ask_ai(prompt)