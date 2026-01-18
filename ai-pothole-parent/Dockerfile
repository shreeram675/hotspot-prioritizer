FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=2000 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8003

CMD ["python", "main.py"]
