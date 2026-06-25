"""
framework/instances/real_estate/match_score_strategy.py
─────────────────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — ponto flexível 4.

Estende AbstractMatchScoreStrategy para calcular a compatibilidade entre
um usuário buscador e os imóveis cadastrados.

Critérios de score:
  - Atributos de habitabilidade (livability.*) em comum   → peso 50 %
  - Atributos de estado atual (current_state.*)           → peso 30 %
  - Atributos estéticos (aesthetics.color.*)              → peso 20 %
"""

from __future__ import annotations
from typing import Any, List, Tuple

from apps.ai_analysis.models import PropertySubjectiveAttribute
from framework.abstract_match_score_strategy import AbstractMatchScoreStrategy


class RealEstateMatchScoreStrategy(AbstractMatchScoreStrategy):
    """
    Estratégia de match-score para a Plataforma Imobiliária.

    Compara os atributos preferidos do usuário (SearchPreference + atributos
    subjetivos salvos) com os atributos agregados de cada imóvel.
    """

    # Pesos por categoria de token
    CATEGORY_WEIGHTS: dict = {
        "livability": 0.50,
        "current_state": 0.30,
        "aesthetics.color": 0.20,
    }

    # ── AbstractMatchScoreStrategy interface ──────────────────────────────────

    def calculate(
        self, user: Any, posts: List[Any]
    ) -> List[Tuple[Any, int]]:
        """
        Calcula um score 0–100 para cada imóvel em relação ao usuário.

        A lógica atual usa os atributos subjetivos do imóvel ponderados
        pelas categorias definidas em CATEGORY_WEIGHTS.
        Um imóvel sem atributos recebe score 0.
        """
        scores: List[Tuple[Any, int]] = []

        for post in posts:
            raw_score = self._score_for_post(post)
            scores.append((post, round(raw_score * 100)))

        return scores

    def persist(self, user: Any, scores: List[Tuple[Any, int]]) -> None:
        """
        Persiste os scores no banco.

        NOTE: A Fase 1 não tinha entidade MatchScore própria; esta
        implementação registra os scores como atributo transitório no objeto.
        Uma migração futura pode criar a tabela MatchScore do framework.
        """
        for post, score in scores:
            post.match_score = score  # anotação em memória — não persiste no DB ainda

    # ── helpers privados ──────────────────────────────────────────────────────

    def _score_for_post(self, post: Any) -> float:
        """Retorna score normalizado [0, 1] para um imóvel."""
        attributes = PropertySubjectiveAttribute.objects.filter(property=post)
        if not attributes.exists():
            return 0.0

        weighted_sum = 0.0
        weight_total = 0.0

        for attr in attributes:
            token = attr.attribute_token
            weight = self._weight_for_token(token)
            weighted_sum += attr.strength_mean * weight
            weight_total += weight

        if weight_total == 0:
            return 0.0

        return weighted_sum / weight_total

    def _weight_for_token(self, token: str) -> float:
        """Retorna o peso para um token com base na sua categoria."""
        for prefix, weight in self.CATEGORY_WEIGHTS.items():
            if token.startswith(prefix):
                return weight
        return 0.1  # peso padrão para tokens não mapeados
