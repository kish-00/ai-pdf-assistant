import os
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter


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
        self._embeddings = OllamaEmbeddings(model="llama3")
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

        llm = ChatOllama(model="llama3", temperature=0)
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

    def summarize_document(self, doc_id: str) -> Optional[str]:
        if doc_id not in self._raw_texts:
            return None

        text = self._raw_texts[doc_id]
        truncated = text[:8000]

        llm = ChatOllama(model="llama3", temperature=0)
        chain = load_qa_chain(llm, chain_type="stuff", prompt=SUMMARY_PROMPT)
        response = chain(
            {"input_documents": [Document(page_content=truncated)], "question": "Summarize"}
        )

        return response["output_text"]

    def remove_document(self, doc_id: str) -> None:
        self._stores.pop(doc_id, None)
        self._raw_texts.pop(doc_id, None)
