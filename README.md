---
title: AI Notes Generator
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: streamlit
app_file: app.py
pinned: false
---

# 📝 AI Notes Generator

Upload a PowerPoint (.pptx) file and turn it into study notes, summaries,
exam questions, and MCQs, using a free AI model hosted on Hugging Face.

## Files
- `app.py` – the Streamlit interface (the Space runs this)
- `agent.py` – decides file type and which AI task to run
- `pptx_extractor.py` – reads text from .pptx slides
- `ai_engine.py` – calls the hosted Hugging Face model
- `prompts.py` – the prompts sent to the AI
- `requirements.txt` – Python packages

## Important
This Space needs a **Secret** named `HF_TOKEN` (your Hugging Face access
token with inference permission). Set it in:
Settings → Variables and secrets → New secret.

## Run locally (optional)
```
pip install -r requirements.txt
set HF_TOKEN=your_token_here   # Windows PowerShell:  $env:HF_TOKEN="your_token_here"
streamlit run app.py
```