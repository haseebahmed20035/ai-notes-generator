# app.py  (Hugging Face hosted version)
# --------------------------------------------------------------------------
# This is the MAIN file the Space runs. Same app as before, but the AI now
# runs on Hugging Face's servers instead of local Ollama.
# --------------------------------------------------------------------------

import streamlit as st

# Import our own helper files.
from agent import is_supported, detect_file_type, run_task, TASK_TO_PROMPT
from pptx_extractor import extract_text_from_pptx, combine_slides_text
from ai_engine import is_ai_ready, MODEL_NAME


# ----------------------------- PAGE SETUP --------------------------------

st.set_page_config(page_title="AI Notes Generator", page_icon="📝")
st.title("📝 AI Notes Generator")
st.write(
    "Upload a PowerPoint (.pptx) file and turn it into study notes, "
    "summaries, exam questions, or MCQs, all powered by a free AI model."
)

# Streamlit re-runs the whole script on every click. To remember things
# (like extracted text and generated results) we use st.session_state.
if "slide_text" not in st.session_state:
    st.session_state.slide_text = ""
if "result" not in st.session_state:
    st.session_state.result = ""
if "result_label" not in st.session_state:
    st.session_state.result_label = ""


# --------------------------- SIDEBAR: STATUS -----------------------------

with st.sidebar:
    st.header("⚙️ Status")
    ready, error = is_ai_ready()
    if ready:
        st.success(f"AI is ready. Model: {MODEL_NAME}")
    else:
        st.error("AI token is missing.")
        st.caption(
            "Add your Hugging Face token as a Secret named HF_TOKEN "
            "in this Space's Settings."
        )


# ----------------------------- FILE UPLOAD -------------------------------

uploaded_file = st.file_uploader(
    "Upload your PowerPoint file",
    type=["pptx", "ppt"],   # the picker shows these, but we validate again below
)

# ERROR CASE 1: No file uploaded yet. Stop here politely.
if uploaded_file is None:
    st.info("👆 Please upload a .pptx file to get started.")
    st.stop()

# ERROR CASE 2: Unsupported file type (e.g. the old .ppt format).
if not is_supported(uploaded_file.name):
    file_type = detect_file_type(uploaded_file.name)
    st.error(
        f"Sorry, the file type '{file_type}' is not supported. "
        "This app can only read the newer **.pptx** format.\n\n"
        "If you have an old **.ppt** file, open it in PowerPoint or "
        "Google Slides and save it as **.pptx**, then upload again."
    )
    st.stop()


# --------------------------- EXTRACT THE TEXT ----------------------------

try:
    file_bytes = uploaded_file.getvalue()
    slides_data = extract_text_from_pptx(file_bytes)
    combined_text = combine_slides_text(slides_data)
except Exception as error:
    st.error(
        "Something went wrong while reading the PowerPoint file. "
        "It may be corrupted or not a real .pptx file.\n\n"
        f"Technical detail: {error}"
    )
    st.stop()

# ERROR CASE 3: The file opened fine but every slide was empty.
if not combined_text.strip():
    st.warning(
        "We opened the file but found **no readable text**. "
        "The slides may contain only images. Try a file that has text."
    )
    st.stop()

st.session_state.slide_text = combined_text
st.success(f"✅ Extracted text from {len(slides_data)} slide(s).")


# --------------------------- SHOW EXTRACTED TEXT -------------------------

with st.expander("🔍 View extracted slide text"):
    for slide in slides_data:
        st.markdown(f"**Slide {slide['slide_number']}**")
        if slide["text"]:
            st.write(slide["text"])
        else:
            st.caption("(no text on this slide)")
        st.divider()


# ----------------------------- CHOOSE A TASK -----------------------------

st.subheader("What would you like to generate?")

task_name = st.radio(
    "Choose one:",
    options=list(TASK_TO_PROMPT.keys()),
    horizontal=False,
)

generate_clicked = st.button("🚀 Generate", type="primary")


# ----------------------------- RUN THE AGENT -----------------------------

if generate_clicked:
    # Re-check the token right before we use it.
    ready, error = is_ai_ready()
    if not ready:
        st.error(
            "Cannot reach the AI model because the HF_TOKEN secret is missing. "
            "Add it in this Space's Settings and try again."
        )
        st.stop()

    # ERROR CASE 4 + 5: AI request might fail for many reasons.
    try:
        with st.spinner(f"Generating {task_name}... this can take a moment."):
            result = run_task(task_name, st.session_state.slide_text)

        st.session_state.result = result
        st.session_state.result_label = task_name

    except Exception as error:
        st.error(
            "The AI was unable to generate a response. "
            "Please try again in a moment.\n\n"
            f"Technical detail: {error}"
        )
        st.stop()


# --------------------------- SHOW + DOWNLOAD RESULT ----------------------

if st.session_state.result:
    st.subheader(f"📄 {st.session_state.result_label}")
    st.write(st.session_state.result)

    safe_label = st.session_state.result_label.replace(" ", "_")
    file_name = f"{safe_label}.txt"

    st.download_button(
        label="⬇️ Download as TXT",
        data=st.session_state.result,
        file_name=file_name,
        mime="text/plain",
    )