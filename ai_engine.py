# ai_engine.py  (Hugging Face hosted version)
# --------------------------------------------------------------------------
# This version does NOT use Ollama. Instead it calls a free AI model hosted
# on Hugging Face, so the app can run online on a Hugging Face Space.
#
# It reads your Hugging Face token from an environment variable called
# HF_TOKEN. On a Space you set this as a "Secret" (never put it in the code).
# --------------------------------------------------------------------------

import os
from huggingface_hub import InferenceClient

# The model to use. This one is free, strong, and does NOT require accepting
# a special license. You can swap it for another (see notes at the bottom).
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"


def _get_client() -> InferenceClient:
    """Create the Hugging Face client using the secret token."""
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "No HF_TOKEN found. Add your Hugging Face token as a Secret "
            "named HF_TOKEN (on a Space) or as an environment variable "
            "(when running locally)."
        )
    return InferenceClient(api_key=token)


def is_ai_ready() -> tuple:
    """
    Check that we have a token to talk to the AI.

    Returns:
        (True, None)        if a token is present.
        (False, error_msg)  if the token is missing.
    """
    token = os.environ.get("HF_TOKEN")
    if not token:
        return False, "HF_TOKEN is not set."
    return True, None


def ask_ai(prompt: str, model: str = MODEL_NAME, max_tokens: int = 1200) -> str:
    """
    Send a prompt to the hosted AI model and return its text answer.

    Raises:
        RuntimeError with a friendly message if something goes wrong.
    """
    try:
        client = _get_client()

        # This uses the same style as OpenAI's chat API.
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,   # how long the answer can be
        )

        # The reply text lives inside choices[0].message.content.
        return completion.choices[0].message.content.strip()

    except Exception as error:
        raise RuntimeError(
            "The AI request failed. This can happen if the token is wrong, "
            "the free rate limit was hit, or the model is busy. "
            f"Technical detail: {error}"
        )

# --------------------------------------------------------------------------
# WANT A DIFFERENT MODEL?
# Just change MODEL_NAME above. Some free options:
#   "Qwen/Qwen2.5-7B-Instruct"            (default, no license needed)
#   "HuggingFaceH4/zephyr-7b-beta"        (no license needed)
#   "meta-llama/Meta-Llama-3-8B-Instruct" (real Llama 3, but you must click
#                                          "Agree" on its model page first)
# If a model gives an error, try one of the others.
# --------------------------------------------------------------------------