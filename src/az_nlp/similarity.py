"""
Cross-lingual text similarity for Azerbaijani.

Uses multilingual sentence-transformers to compute semantic similarity
between texts in Azerbaijani, English, Russian, and Turkish.
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Union

import numpy as np


# Default model -- multilingual, supports 50+ languages including AZ, EN, RU, TR
_DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class CrossLingualSimilarity:
    """Cross-lingual semantic similarity using sentence-transformers.

    Supports Azerbaijani (az), English (en), Russian (ru), Turkish (tr),
    and 50+ other languages via multilingual sentence embeddings.
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Args:
            model_name: Sentence-transformer model name or path.
                Defaults to 'paraphrase-multilingual-MiniLM-L12-v2'.
            device: Device for inference ('cpu', 'cuda', 'mps').
                If None, auto-detects.
        """
        self._model_name = model_name or _DEFAULT_MODEL
        self._model = None
        self._device = device

    def _load_model(self):
        """Lazy-load the sentence-transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for similarity features. "
                    "Install it with: pip install sentence-transformers"
                )
            kwargs = {}
            if self._device:
                kwargs["device"] = self._device
            self._model = SentenceTransformer(self._model_name, **kwargs)

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode texts into dense vector embeddings.

        Args:
            texts: A single string or list of strings.

        Returns:
            Numpy array of shape (n, embedding_dim).
        """
        self._load_model()
        if isinstance(texts, str):
            texts = [texts]
        return self._model.encode(texts, convert_to_numpy=True)

    def similarity(self, text_a: str, text_b: str) -> float:
        """Compute cosine similarity between two texts.

        The texts can be in different languages (e.g., AZ and EN).

        Args:
            text_a: First text.
            text_b: Second text.

        Returns:
            Cosine similarity score in [-1, 1].
        """
        embeddings = self.encode([text_a, text_b])
        return float(self._cosine_similarity(embeddings[0], embeddings[1]))

    def pairwise_similarity(
        self,
        texts_a: List[str],
        texts_b: List[str],
    ) -> List[float]:
        """Compute pairwise cosine similarity between two lists of texts.

        Args:
            texts_a: First list of texts.
            texts_b: Second list of texts (same length as texts_a).

        Returns:
            List of cosine similarity scores.

        Raises:
            ValueError: If the two lists have different lengths.
        """
        if len(texts_a) != len(texts_b):
            raise ValueError(
                f"Lists must have equal length, got {len(texts_a)} and {len(texts_b)}"
            )

        emb_a = self.encode(texts_a)
        emb_b = self.encode(texts_b)

        scores = []
        for i in range(len(texts_a)):
            scores.append(float(self._cosine_similarity(emb_a[i], emb_b[i])))
        return scores

    def most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Find the most similar candidates to a query text.

        Args:
            query: The query text (in any supported language).
            candidates: List of candidate texts to rank.
            top_k: Number of top results to return.

        Returns:
            List of (candidate_text, similarity_score) tuples,
            sorted by similarity descending.
        """
        query_emb = self.encode(query)
        cand_embs = self.encode(candidates)

        scores = [
            float(self._cosine_similarity(query_emb[0], cand_embs[i]))
            for i in range(len(candidates))
        ]

        ranked = sorted(
            zip(candidates, scores), key=lambda x: x[1], reverse=True
        )
        return ranked[:top_k]

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
