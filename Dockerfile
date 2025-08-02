FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip

COPY . .

ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/.cache/transformers
ENV TORCH_HOME=/app/.cache/torch

RUN mkdir -p /app/.cache/transformers /app/.cache/torch

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 