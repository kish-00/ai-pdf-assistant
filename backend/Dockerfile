FROM python:3.11-slim

# Install Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/uploads

# Start Ollama in background and pull model
CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull llama3 && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
