# prompts.py
# --------------------------------------------------------------------------
# This file holds the "instructions" (prompts) we send to the AI model.
# Each function takes the content text and returns a complete prompt string.
# --------------------------------------------------------------------------


def notes_prompt(text: str) -> str:
    """Ask the AI to write detailed, well-organised study notes."""
    return f"""You are a helpful study assistant for a student.

Read the following content and write clear, DETAILED study notes.
Rules:
- Organise the notes with simple headings.
- Use bullet points where helpful.
- Explain ideas in plain, easy language.
- Do NOT invent facts that are not related to the content.

CONTENT:
\"\"\"
{text}
\"\"\"

Now write the study notes:"""


def summary_prompt(text: str) -> str:
    """Ask the AI for a short, simple summary."""
    return f"""You are a helpful study assistant.

Summarise the following content in a SHORT, simple way.
Rules:
- Use 5 to 8 sentences only.
- Plain, beginner-friendly language.
- Capture only the most important ideas.

CONTENT:
\"\"\"
{text}
\"\"\"

Now write the short summary:"""


def questions_prompt(text: str) -> str:
    """Ask the AI for important exam-style questions (without answers)."""
    return f"""You are an experienced teacher creating an exam.

Based on the content below, write 8 to 10 IMPORTANT exam questions
that a student should be able to answer after studying this material.
Rules:
- Mix easy and harder questions.
- Number each question (1, 2, 3, ...).
- Do NOT include the answers.

CONTENT:
\"\"\"
{text}
\"\"\"

Now write the exam questions:"""


def case_scenario_prompt(text: str) -> str:
    """Ask the AI for exam-style case scenarios WITH solved answers."""
    return f"""You are an experienced teacher creating exam-style CASE SCENARIOS.

Based on the content below, create 3 to 4 realistic case scenarios that
test how well a student can APPLY the ideas (not just memorise them).

For EACH case scenario, use exactly this layout:
Scenario: <a short, realistic situation that uses the concepts>
Question: <one or two exam-style questions about that scenario>
Solution: <a clear, step-by-step solved answer / model solution>

Rules:
- Keep the language simple and clear.
- Make the solutions complete so a student can learn from them.
- Base everything on the content provided.

CONTENT:
\"\"\"
{text}
\"\"\"

Now write the solved case scenarios:"""