# Dockerfile
# --------------------------------------------------------------------------
# This tells Hugging Face how to build and run your app.
# The key extra step is installing "tesseract-ocr", the engine that reads
# text out of images and scanned PDFs.
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

# Install the Python packages first (this layer is cached for faster rebuilds).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's files.
COPY . .

# Streamlit serves on port 8501.
EXPOSE 8501

# Start the app.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]