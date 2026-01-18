FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies
RUN apt-get update --fix-missing && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=2000 --retries 10 -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the service
CMD ["python", "main.py"]
