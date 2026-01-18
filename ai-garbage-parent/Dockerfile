# Reuse the already built image that has PyTorch installed
FROM citizen-ai-system-ai-pothole-parent:latest

WORKDIR /app

COPY requirements.txt .
# Install CPU-only torch specifically (much smaller/faster)
RUN pip install --no-cache-dir --default-timeout=2000 torch --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
RUN pip install --no-cache-dir --default-timeout=2000 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8004

CMD ["python", "main.py"]
