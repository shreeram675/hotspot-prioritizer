FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# Install CPU-only torch first
RUN pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .

# Pre-download the model to bake it into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "9001"]
