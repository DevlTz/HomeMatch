"""
framework/instances/real_estate/attribute_set.py
─────────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — ponto flexível 1.

Estende AbstractAttributeSet com os tokens definidos em apps/ai_analysis/schema.py.
"""

from __future__ import annotations
from typing import List

from framework.abstract_attribute_set import AbstractAttributeSet


class RealEstateAttributeSet(AbstractAttributeSet):
    """
    Conjunto de atributos para a Plataforma Imobiliária.

    Os tokens espelham o ATTRIBUTE_REGISTRY de apps/ai_analysis/schema.py,
    que é a fonte da verdade do sistema de análise visual por IA.

    Estrutura dos tokens:
      aesthetics.color.visual_warmth      — calor visual (tons quentes)
      aesthetics.color.brightness         — luminosidade do ambiente
      aesthetics.color.saturation         — saturação das cores
      aesthetics.architecture.<estilo>    — estilos arquitetônicos detectados
      livability.coziness                 — aconchego
      livability.verdancy                 — presença de vegetação
      livability.humidity                 — umidade percebida
      livability.spaciousness             — sensação de espaço
      current_state.cleanliness           — limpeza visível
      current_state.ventilation           — ventilação
      current_state.leisure               — áreas de lazer visíveis
      current_state.structural_integrity  — estado das superfícies
    """

    # Tokens derivados de ATTRIBUTE_REGISTRY (schema.py)
    _ARCHITECTURAL_STYLES: List[str] = [
        "colonial_portuguese",
        "baroque",
        "neoclassical",
        "eclectic",
        "art_nouveau",
        "art_deco",
        "modernist_brazilian",
        "tropical_modernist",
        "brutalist",
        "postmodern",
        "contemporary",
        "vernacular_regional",
        "vernacular_coastal",
        "neo_colonial",
        "minimalist",
        "high_rise_modern",
        "gated_community_suburban",
    ]

    _COLOR_TOKENS: List[str] = [
        "aesthetics.color.visual_warmth",
        "aesthetics.color.brightness",
        "aesthetics.color.saturation",
    ]

    _LIVABILITY_TOKENS: List[str] = [
        "livability.coziness",
        "livability.verdancy",
        "livability.humidity",
        "livability.spaciousness",
    ]

    _CURRENT_STATE_TOKENS: List[str] = [
        "current_state.cleanliness",
        "current_state.ventilation",
        "current_state.leisure",
        "current_state.structural_integrity",
    ]

    @property
    def _all_tokens(self) -> List[str]:
        arch_tokens = [
            f"aesthetics.architecture.{style}"
            for style in self._ARCHITECTURAL_STYLES
        ]
        return self._COLOR_TOKENS + arch_tokens + self._LIVABILITY_TOKENS + self._CURRENT_STATE_TOKENS

    # ── AbstractAttributeSet interface ────────────────────────────────────────

    def getTokens(self) -> List[str]:
        """Retorna todos os tokens de atributos imobiliários."""
        return self._all_tokens

    def validate(self, token: str) -> bool:
        """Verifica se o token pertence ao vocabulário imobiliário."""
        return token in self.asValidTokensFrozenset()

    def getDefaultSet(self) -> List[str]:
        """
        Subconjunto padrão usado pela análise de IA quando não há
        instrução específica: exclui estilos arquitetônicos (muito granulares)
        e foca nos atributos de habitabilidade e estado.
        """
        return self._COLOR_TOKENS + self._LIVABILITY_TOKENS + self._CURRENT_STATE_TOKENS
