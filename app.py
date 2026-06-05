import streamlit as st

# Import our own helper files.
from agent import (
    is_supported,
    detect_file_type,
    extract_content,
    run_task,
    TASK_TO_PROMPT,
)
from ai_engine import is_ai_ready, MODEL_NAME


# ----------------------------- PAGE SETUP --------------------------------

st.set_page_config(page_title="AI Notes Generator", page_icon="📝")
st.title("📝 AI Notes Generator")
st.write(
    "Upload a PowerPoint (.pptx), PDF, or image file and turn it into study "
    "notes, summaries, exam questions, or solved case scenarios. Scanned files and pictures are read automatically "
    "using OCR."
)

if "content_text" not in st.session_state:
    st.session_state.content_text = ""
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
    "Upload your file (.pptx, .pdf, or an image)",
    type=["pptx", "pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff", "ppt"],
)

# ERROR CASE 1: No file uploaded yet.
if uploaded_file is None:
    st.info("👆 Please upload a .pptx or .pdf file to get started.")
    st.stop()

# ERROR CASE 2: Unsupported file type (e.g. the old .ppt format).
if not is_supported(uploaded_file.name):
    file_type = detect_file_type(uploaded_file.name)
    st.error(
        f"Sorry, the file type '{file_type}' is not supported. "
        "This app can read **.pptx** (PowerPoint), **.pdf**, and image "
        "files (.png, .jpg, etc.).\n\n"
        "If you have an old **.ppt** file, open it in PowerPoint or "
        "Google Slides and save it as **.pptx**, then upload again."
    )
    st.stop()


# --------------------------- EXTRACT THE TEXT ----------------------------

try:
    file_bytes = uploaded_file.getvalue()
    # The agent decides which reader to use based on the file type.
    # For scanned files or images this runs OCR, which can take a moment.
    with st.spinner("Reading your file... (scanned files use OCR and may take a little longer)"):
        items, combined_text, label = extract_content(uploaded_file.name, file_bytes)
except Exception as error:
    st.error(
        "Something went wrong while reading the file. "
        "It may be corrupted or not a real .pptx / .pdf file.\n\n"
        f"Technical detail: {error}"
    )
    st.stop()

# ERROR CASE 3: The file opened fine but contained no readable text.
if not combined_text.strip():
    st.warning(
        "We read the file but couldn't find any text, even with OCR. "
        "This can happen if the image is blurry, very low quality, or "
        "handwritten. Try a clearer file."
    )
    st.stop()

st.session_state.content_text = combined_text
st.success(f"✅ Extracted text from {len(items)} {label.lower()}(s).")


# --------------------------- SHOW EXTRACTED TEXT -------------------------

with st.expander(f"🔍 View extracted {label.lower()} text"):
    for item in items:
        st.markdown(f"**{label} {item['number']}**")
        if item["text"]:
            st.write(item["text"])
        else:
            st.caption(f"(no text on this {label.lower()})")
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
    ready, error = is_ai_ready()
    if not ready:
        st.error(
            "Cannot reach the AI model because the HF_TOKEN secret is missing. "
            "Add it in this Space's Settings and try again."
        )
        st.stop()

    try:
        progress = st.progress(0.0, text="Starting...")

        def on_progress(current, total):
            progress.progress(
                current / total,
                text=f"Generating {task_name}... part {current} of {total}",
            )

        result = run_task(task_name, st.session_state.content_text, on_progress)
        progress.empty()

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