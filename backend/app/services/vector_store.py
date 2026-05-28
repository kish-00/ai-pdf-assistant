import os
from typing import Optional, List

from fastembed import TextEmbedding
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

QA_PROMPT_TEMPLATE = """Use the following pieces of context from the PDF document to answer the user's question.
If you don't know the answer based on the context, say "I couldn't find that information in the document."
Always cite which page(s) the information comes from.

Context:
{context}

Question: {question}

Answer:"""

SUMMARY_PROMPT_TEMPLATE = """Provide a concise summary of the following document content.
Include the main topics, key findings, and important details.

Content:
{text}

Summary:"""


class LocalEmbeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = TextEmbedding(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return list(self.model.embed(texts))

    def embed_query(self, text: str) -> List[float]:
        return list(self.model.embed(text))[0]


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
            self._embeddings = LocalEmbeddings()
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            self._api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            self._initialized = True

    def _call_llm(self, prompt: str, max_tokens: int = 512) -> str:
        if not self._api_token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set")

        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self._api_token,
        )
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0,
        )
        return response.choices[0].message.content

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
            context = "\n\n".join(doc.page_content for doc in docs)
            prompt = QA_PROMPT_TEMPLATE.format(context=context, question=question)
            answer = self._call_llm(prompt)

            sources = list({
                f"Page {doc.metadata.get('page', 'unknown')}"
                for doc in docs
            })

            return {
                "answer": answer,
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
            prompt = SUMMARY_PROMPT_TEMPLATE.format(text=truncated)
            return self._call_llm(prompt)
        except Exception as e:
            return f"Unable to generate summary: {str(e)}"

    def remove_document(self, doc_id: str) -> None:
        self._stores.pop(doc_id, None)
        self._raw_texts.pop(doc_id, None)
