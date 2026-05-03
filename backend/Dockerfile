# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Tesseract + English/Arabic language packs for OCR fallback on image-based
# financial statement pages. poppler-utils provides pdftoppm which pdf2image
# uses to rasterize PDF pages before OCR.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker caches this layer — re-installs only if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code into the container
COPY . .

# Fix Windows line endings (CRLF → LF) and make the script executable
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Flask runs on port 5000
EXPOSE 5000

# Run the startup script when the container starts
ENTRYPOINT ["./entrypoint.sh"]
