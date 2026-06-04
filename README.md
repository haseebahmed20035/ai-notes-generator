---
title: AI Notes Generator
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8501
pinned: false
---

# 📝 AI Notes Generator

Upload a PowerPoint (.pptx), PDF, or image file and turn it into study
notes, summaries, exam questions, or solved case scenarios. Scanned files
and pictures are read automatically using OCR (Tesseract). The AI runs on a
free model hosted by Hugging Face.

## How it runs
This Space uses the **Docker** SDK so it can install the OCR engine.
The `Dockerfile` installs `tesseract-ocr` and starts the Streamlit app.

## Required secret
Add a secret named `HF_TOKEN` (your Hugging Face access token with the
"Make calls to Inference Providers" permission) in:
Settings → Variables and secrets → New secret.

## Files
- `app.py` – the Streamlit interface
- `agent.py` – decides which reader and AI task to use
- `pptx_extractor.py` – reads PowerPoint text (and OCRs pictures)
- `pdf_extractor.py` – reads PDF text (and OCRs scanned pages)
- `image_extractor.py` – OCRs uploaded images
- `ocr.py` – shared OCR helper
- `ai_engine.py` – calls the hosted AI model
- `prompts.py` – the prompts sent to the AI
- `requirements.txt` – Python packages
- `Dockerfile` – build instructions (installs OCR)