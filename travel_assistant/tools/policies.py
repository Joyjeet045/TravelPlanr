import re
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.tools import tool

response = requests.get(
    "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)
response.raise_for_status()
faq_text = response.text
docs = [{"page_content": txt.strip()} for txt in re.split(r"(?=\n##)", faq_text) if txt.strip()]

class VectorStoreRetriever:
    def __init__(self, docs: list, vectors: np.ndarray):
        self._arr = vectors
        self._docs = docs
    @classmethod
    def from_docs(cls, docs: list, embedder: SentenceTransformer):
        texts = [doc["page_content"] for doc in docs]
        vectors = embedder.encode(texts, normalize_embeddings=True)
        return cls(docs, vectors)
    def query(self, query: str, k: int = 5) -> list[dict]:
        query_vec = embedder.encode([query], normalize_embeddings=True)[0]
        scores = np.dot(self._arr, query_vec)
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [
            {**self._docs[idx], "similarity": float(scores[idx])}
            for idx in top_k_idx_sorted
        ]

embedder = SentenceTransformer("all-MiniLM-L6-v2")
retriever = VectorStoreRetriever.from_docs(docs, embedder)

@tool
def lookup_policy(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Args:
        query (str): The user's policy-related question or search query.
    Returns:
        String containing the most relevant policy text(s) from the company manual.
    """
    docs = retriever.query(query, k=2)
    return "\n\n".join([doc["page_content"] for doc in docs]) 