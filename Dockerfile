# Dockerfile
# --------------------------------------------------------------------------
# This tells Hugging Face how to build and run your app.
# It installs the OCR engine (tesseract) and starts Streamlit.
# --------------------------------------------------------------------------

# Start from a small Python image.
FROM python:3.11-slim

# Install the OCR engine (system software, not a Python package).
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Folder where the app lives inside the container.
WORKDIR /app
ENV HOME=/app

# Install the Python packages first (cached layer = faster rebuilds).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's files.
COPY . .

# Streamlit serves on port 8501.
EXPOSE 8501

# Start the app.
# The two "enable...false" flags are needed so that file uploads work
# when the app runs behind Hugging Face's proxy (they fix the 403 error).
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false", "--server.enableCORS=false"]