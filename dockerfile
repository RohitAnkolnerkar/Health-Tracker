# Use official Python image
FROM python:3.12.3

# Set working directory
WORKDIR /app

# Install system dependencies including Tesseract for pytesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        gfortran \
        libffi-dev \
        libssl-dev \
        tesseract-ocr \
        libtesseract-dev \
        && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the ports for Flask + FastAPI
EXPOSE 5000
EXPOSE 8000

# Run your app
CMD ["python", "run.py"]
