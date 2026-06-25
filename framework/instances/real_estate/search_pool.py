"""
framework/instances/real_estate/search_pool.py
────────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — ponto flexível 5.

Estende AbstractSearchPool para busca por linguagem natural em imóveis.
Usa EmbeddingService (ponto fixo do framework) para cosine similarity.
"""

from __future__ import annotations
from typing import Any, List

from apps.search.embeddings import EmbeddingService
from framework.abstract_search_pool import AbstractSearchPool
from framework.instances.real_estate.attribute_set import RealEstateAttributeSet


class RealEstateSearchPool(AbstractSearchPool):
    """
    Pool de busca para a Plataforma Imobiliária.

    - Atributos indexáveis: todos os tokens do RealEstateAttributeSet
      (exceto estilos arquitetônicos, que são muito granulares para busca).
    - Ranking: cosine similarity entre o embedding da query e o embedding
      do imóvel (campo Properties.embedding, gerado por
      PropertyEmbeddingDocumentBuilder).
    """

    def __init__(self) -> None:
        self._attribute_set = RealEstateAttributeSet()

    # ── AbstractSearchPool interface ──────────────────────────────────────────

    def getSearchableAttrs(self) -> List[str]:
        """
        Retorna o subconjunto padrão de tokens (sem estilos arquitetônicos)
        que entram no índice de busca semântica.
        """
        return self._attribute_set.getDefaultSet()

    def rank(self, query: str, posts: List[Any]) -> List[Any]:
        """
        Ordena imóveis por similaridade de cosseno entre o embedding da
        query e o embedding pré-calculado de cada imóvel.

        Delega para EmbeddingService (ponto fixo do framework).
        """
        if not posts:
            return []

        query_embedding = EmbeddingService.embed_text(query)
        if not query_embedding:
            return list(posts)

        def _similarity(post: Any) -> float:
            post_embedding = EmbeddingService.deserialize(
                getattr(post, "embedding", "[]")
            )
            return EmbeddingService.cosine_similarity(query_embedding, post_embedding)

        return sorted(posts, key=_similarity, reverse=True)

    # persist() herdado de AbstractSearchPool (no-op padrão)
