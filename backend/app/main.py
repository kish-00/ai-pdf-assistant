import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import pdf, chat

load_dotenv()


@asynccontextmanager
async def lifespan(application: FastAPI):
    os.makedirs(os.getenv("UPLOAD_DIR", "./uploads"), exist_ok=True)
    yield


app = FastAPI(
    title="AI PDF Assistant",
    description="Upload PDFs and ask questions about their content using AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
