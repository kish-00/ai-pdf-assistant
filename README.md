# AI-Powered PDF Assistant

Upload PDF documents and ask natural language questions about their content. Powered by LangChain, OpenAI, and FAISS vector search with a modern React frontend and FastAPI backend.

## Features

- **PDF Upload & Parsing** — Drag-and-drop PDF upload with automatic text extraction and chunking
- **Natural Language Q&A** — Ask questions in plain English, get AI-generated answers with page citations
- **One-Click Summarization** — Generate a concise summary of any uploaded document
- **Vector Search** — FAISS-powered similarity search finds the most relevant document sections
- **Source Citations** — Every answer includes page references so you can verify the source
- **Multi-Document Support** — Upload and switch between multiple PDFs
- **Dockerized Setup** — One command to run the entire stack

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   React Frontend│────▶│  FastAPI Backend │────▶│  OpenAI API  │
│   (Vite + JSX)  │     │  (Python 3.11)  │     │  (GPT-3.5)   │
└─────────────────┘     └────────┬────────┘     └──────────────┘
                                 │
                        ┌────────▼────────┐
                        │  FAISS Vector    │
                        │  Store (In-Mem)  │
                        └─────────────────┘
```

**Data Flow:**
1. User uploads a PDF → PyPDF2 extracts text → RecursiveCharacterTextSplitter chunks it → FAISS indexes embeddings
2. User asks a question → FAISS retrieves top-4 similar chunks → LangChain QA chain generates answer with sources
3. User clicks Summarize → Full document text sent to GPT-3.5-turbo for summarization

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Vite, Lucide Icons | UI with drag-drop, chat interface |
| Backend | FastAPI, Uvicorn | REST API with async support |
| AI/LLM | LangChain, OpenAI GPT-3.5-turbo | Question answering & summarization |
| Vector DB | FAISS (in-memory) | Similarity search over document chunks |
| PDF Processing | PyPDF2 | Text extraction from PDF files |
| Containerization | Docker, Docker Compose, Nginx | Production-ready deployment |

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/kish-00/ai-pdf-assistant.git
cd ai-pdf-assistant

# Set your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Build and run
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000)

### Option 2: Local Development

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pdf/upload` | Upload a PDF file |
| `GET` | `/api/pdf/documents` | List all uploaded documents |
| `DELETE` | `/api/pdf/{doc_id}` | Delete a document |
| `POST` | `/api/chat/ask` | Ask a question about a document |
| `POST` | `/api/chat/summarize/{doc_id}` | Generate a document summary |
| `GET` | `/api/health` | Health check |

### Example Requests

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/api/pdf/upload \
  -F "file=@document.pdf"
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "your-doc-id", "question": "What are the key findings?"}'
```

## Project Structure

```
ai-pdf-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── pdf.py           # PDF upload/delete endpoints
│   │   │   └── chat.py          # Q&A and summarization endpoints
│   │   └── services/
│   │       └── vector_store.py  # FAISS indexing & LangChain QA
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app with state management
│   │   ├── components/
│   │   │   ├── Header.jsx       # App header
│   │   │   ├── UploadZone.jsx   # Drag-and-drop PDF upload
│   │   │   ├── DocumentList.jsx # Sidebar document list
│   │   │   └── ChatPanel.jsx    # Chat Q&A interface
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   └── styles/
│   │       └── global.css       # App styles
│   ├── index.html
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Your OpenAI API key (required) |
| `UPLOAD_DIR` | `./uploads` | Directory for uploaded PDFs |
| `MAX_FILE_SIZE_MB` | `20` | Maximum PDF file size |

## Future Enhancements

- [ ] Persistent vector storage (ChromaDB/Pinecone) for documents across restarts
- [ ] Support for multiple file formats (DOCX, TXT, CSV)
- [ ] Conversation memory for follow-up questions
- [ ] Streaming responses via Server-Sent Events
- [ ] User authentication and document ownership
- [ ] Batch document upload and cross-document Q&A

## License

MIT
