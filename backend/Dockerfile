FROM python:3.11-slim

# Install Ollama dependencies
RUN apt-get update && apt-get install -y \
    curl \
    zstd \
    && curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/uploads

# Pre-pull the model to avoid runtime delays
RUN ollama pull llama2:7b

CMD ["sh", "-c", "ollama serve & sleep 3 && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
