FROM python:3.13.1-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for model cache
RUN mkdir -p /app/models

# Pre-download the translation model during build
# This avoids downloading at runtime
RUN python -c "from transformers import pipeline; \
    import torch; \
    print('Downloading translation model...'); \
    model = pipeline('translation', \
        model='facebook/nllb-200-distilled-600M', \
        device=-1, \
        model_kwargs={'cache_dir': '/app/models'}); \
    print('Model downloaded successfully')"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]