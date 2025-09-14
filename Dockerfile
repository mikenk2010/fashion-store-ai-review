# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_md

# Copy source code
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
COPY main.py .

# Copy data and create necessary directories
COPY data/ ./data/
COPY models/ ./models/
COPY static/ ./static/
COPY migrate/ ./migrate/
RUN mkdir -p logs

# Expose port
EXPOSE 6600

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6600/ || exit 1

# Start application
CMD ["python", "main.py"]