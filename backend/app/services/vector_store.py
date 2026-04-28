import os
from typing import Optional, List

from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document
from langchain_community.llms import HuggingFaceHub
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
import time


QA_PROMPT = PromptTemplate(
    template="""Use the following pieces of context from the PDF document to answer the user's question.
If you don't know the answer based on the context, say "I couldn't find that information in the document."
Always cite which page(s) the information comes from.

Context:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"],
)

SUMMARY_PROMPT = PromptTemplate(
    template="""Provide a concise summary of the following document content.
Include the main topics, key findings, and important details.

Content:
{text}

Summary:""",
    input_variables=["text"],
)


class HFEmbeddings:
    """Custom embeddings using HuggingFace Inference API with retry logic."""
    def __init__(self, model="sentence-transformers/all-MiniLM-L6-v2", api_token: Optional[str] = None, max_retries: int = 3):
        self.model = model
        self.api_token = api_token or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
        self.max_retries = max_retries
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}

    def _call_with_retry(self, payload: dict) -> Optional[list]:
        """Make API call with exponential backoff retry."""
        if not self.api_token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set")

        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:  # Model loading
                    wait = (attempt + 1) * 5  # 5, 10, 15 seconds
                    time.sleep(wait)
                else:
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Failed to get embeddings after {self.max_retries} retries: {e}")
                time.sleep((attempt + 1) * 2)
        return None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Bulk embed all texts at once (API supports batch)
        result = self._call_with_retry({"inputs": texts})
        if result is None:
            raise RuntimeError("Failed to get embeddings from HuggingFace after retries")
        return result

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class VectorStoreService:
    _instance = None
    _stores: dict[str, FAISS] = {}
    _raw_texts: dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._embeddings = HFEmbeddings()
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            self._initialized = True

    def index_document(self, doc_id: str, text: str) -> None:
        chunks = self._text_splitter.split_text(text)

        page_numbers = []
        for chunk in chunks:
            page_marker = "--- Page "
            if page_marker in chunk:
                start = chunk.index(page_marker) + len(page_marker)
                end = chunk.index(" ---", start)
                page_numbers.append(chunk[start:end])
            else:
                page_numbers.append("unknown")

        documents = [
            Document(page_content=chunk, metadata={"page": page_numbers[i], "doc_id": doc_id})
            for i, chunk in enumerate(chunks)
        ]

        vectorstore = FAISS.from_documents(documents, self._embeddings)
        self._stores[doc_id] = vectorstore
        self._raw_texts[doc_id] = text

    def query_document(self, doc_id: str, question: str) -> Optional[dict]:
        if doc_id not in self._stores:
            return None

        vectorstore = self._stores[doc_id]
        docs = vectorstore.similarity_search(question, k=4)

        if not docs:
            return {
                "answer": "I couldn't find relevant information in the document.",
                "sources": [],
            }

        try:
            llm = HuggingFaceHub(
                repo_id="google/flan-t5-large",
                model_kwargs={"temperature": 0, "max_length": 512},
            )
            chain = load_qa_chain(llm, chain_type="stuff", prompt=QA_PROMPT)
            response = chain({"input_documents": docs, "question": question})

            sources = list({
                f"Page {doc.metadata.get('page', 'unknown')}"
                for doc in docs
            })

            return {
                "answer": response["output_text"],
                "sources": sources,
            }
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error while processing your question: {str(e)}. Please try again.",
                "sources": [],
            }

    def summarize_document(self, doc_id: str) -> Optional[str]:
        if doc_id not in self._raw_texts:
            return None

        text = self._raw_texts[doc_id]
        truncated = text[:8000]

        try:
            llm = HuggingFaceHub(
                repo_id="google/flan-t5-large",
                model_kwargs={"temperature": 0, "max_length": 512},
            )
            chain = load_qa_chain(llm, chain_type="stuff", prompt=SUMMARY_PROMPT)
            response = chain(
                {"input_documents": [Document(page_content=truncated)], "question": "Summarize"}
            )
            return response["output_text"]
        except Exception as e:
            return f"Unable to generate summary: {str(e)}"

    def remove_document(self, doc_id: str) -> None:
        self._stores.pop(doc_id, None)
        self._raw_texts.pop(doc_id, None)
