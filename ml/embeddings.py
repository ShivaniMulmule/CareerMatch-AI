"""
Semantic Vector Embeddings Engine for CareerMatch AI.
Utilizes pretrained Sentence-BERT ('sentence-transformers/all-MiniLM-L6-v2')
to compute dense semantic representations and cosine similarities.
Zero keyword counting - true semantic vector understanding.
"""

from typing import List, Union, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import torch


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticEmbeddingEngine:
    _instance = None

    def __new__(cls, model_name: str = DEFAULT_MODEL_NAME):
        if cls._instance is None:
            cls._instance = super(SemanticEmbeddingEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        if self._initialized:
            return
        print(f"[*] Initializing Sentence-BERT Embedding Engine ({model_name})...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._initialized = True
        print(f"[+] Sentence-BERT Engine loaded on {device.upper()} (Embedding Dim: {self.get_embedding_dimension()})")

    def get_embedding_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single string with in-memory caching."""
        clean_text = text.strip()
        if not clean_text:
            return np.zeros(self.get_embedding_dimension(), dtype=np.float32)
        if clean_text in self._embedding_cache:
            return self._embedding_cache[clean_text]

        embedding = self.model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)
        if len(self._embedding_cache) < 20000:
            self._embedding_cache[clean_text] = embedding
        return embedding

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """Batch encode strings into normalized dense vectors."""
        cleaned = [t.strip() if t.strip() else " " for t in texts]
        embeddings = self.model.encode(
            cleaned,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two 1D normalized embeddings.
        Since embeddings are L2 normalized, dot product == cosine similarity.
        """
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        similarity = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
        # Clip to valid range [-1.0, 1.0] to guard against precision issues
        return float(np.clip(similarity, -1.0, 1.0))

    @staticmethod
    def batch_cosine_similarity(matrix_a: np.ndarray, matrix_b: np.ndarray) -> np.ndarray:
        """
        Computes pairwise cosine similarity matrix between matrix_a (N x D) and matrix_b (M x D).
        """
        # Normalize matrices
        norm_a = np.linalg.norm(matrix_a, axis=1, keepdims=True)
        norm_b = np.linalg.norm(matrix_b, axis=1, keepdims=True)
        norm_a[norm_a == 0] = 1e-10
        norm_b[norm_b == 0] = 1e-10
        a_norm = matrix_a / norm_a
        b_norm = matrix_b / norm_b
        return np.dot(a_norm, b_norm.T)


# Global singleton access
_engine_instance = None

def get_embedding_engine(model_name: str = DEFAULT_MODEL_NAME) -> SemanticEmbeddingEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SemanticEmbeddingEngine(model_name)
    return _engine_instance
