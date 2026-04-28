FROM ollama/ollama:latest

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/uploads

EXPOSE 8000

CMD ["sh", "-c", "ollama serve & sleep 3 && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]