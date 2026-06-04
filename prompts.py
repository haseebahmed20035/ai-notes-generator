# prompts.py
# --------------------------------------------------------------------------
# This file holds the "instructions" (prompts) we send to the AI model.
# Keeping prompts in one place makes them easy to read and tweak later.
# Each function takes the slide text and returns a complete prompt string.
# --------------------------------------------------------------------------


def notes_prompt(text: str) -> str:
    """Ask the AI to write detailed, well-organised study notes."""
    return f"""You are a helpful study assistant for a student.

Read the following slide content and write clear, DETAILED study notes.
Rules:
- Organise the notes with simple headings.
- Use bullet points where helpful.
- Explain ideas in plain, easy language.
- Do NOT invent facts that are not related to the content.

SLIDE CONTENT:
\"\"\"
{text}
\"\"\"

Now write the study notes:"""


def summary_prompt(text: str) -> str:
    """Ask the AI for a short, simple summary."""
    return f"""You are a helpful study assistant.

Summarise the following slide content in a SHORT, simple way.
Rules:
- Use 5 to 8 sentences only.
- Plain, beginner-friendly language.
- Capture only the most important ideas.

SLIDE CONTENT:
\"\"\"
{text}
\"\"\"

Now write the short summary:"""


def questions_prompt(text: str) -> str:
    """Ask the AI for important exam-style questions."""
    return f"""You are an experienced teacher creating an exam.

Based on the slide content below, write 8 to 10 IMPORTANT exam questions
that a student should be able to answer after studying this material.
Rules:
- Mix easy and harder questions.
- Number each question (1, 2, 3, ...).
- Do NOT include the answers.

SLIDE CONTENT:
\"\"\"
{text}
\"\"\"

Now write the exam questions:"""


def mcq_prompt(text: str) -> str:
    """Ask the AI for multiple-choice questions WITH answers."""
    return f"""You are a teacher creating a multiple-choice quiz.

Based on the slide content below, create 5 multiple-choice questions (MCQs).
Rules for EACH question:
- Write the question.
- Give 4 options labelled A, B, C, D.
- On a new line write "Answer:" followed by the correct option letter.
- Keep the language simple.

SLIDE CONTENT:
\"\"\"
{text}
\"\"\"

Now write the MCQs:"""