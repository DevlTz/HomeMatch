"""
framework/instances/real_estate/ai_analyzer.py
───────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — ponto flexível 2.

Estende AbstractAIAnalyzer usando os módulos padrão do framework:
  - AiVisionClient  → envia a foto para o modelo de visão
  - AiAttributeParser → parseia a resposta JSON em tokens planos
  - SubjectiveAttributeRepository → persiste os atributos no banco

Esta classe é essencialmente um adaptador entre AbstractAIAnalyzer e
o AiAnalysisService existente (apps/ai_analysis/services.py).
"""

from __future__ import annotations
from typing import Any, Dict, List

from django.conf import settings

from apps.ai_analysis.client import AiVisionClient
from apps.ai_analysis.exceptions import AiAnalysisError
from apps.ai_analysis.parser import AiAttributeParser
from apps.ai_analysis.repositories import SubjectiveAttributeRepository
from framework.abstract_ai_analyzer import AbstractAIAnalyzer


class RealEstateAIAnalyzer(AbstractAIAnalyzer):
    """
    Analisador de fotos de imóveis — usa o pipeline de visão computacional
    padrão do framework (AiVisionClient + AiAttributeParser).

    Não há lógica nova aqui: o ponto de extensão é satisfeito delegando
    ao módulo padrão, demonstrando que a instância imobiliária adota
    o comportamento default sem personalização.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        client: AiVisionClient | None = None,
    ) -> None:
        base_url = base_url or getattr(settings, "AI_API_BASE_URL", None)
        api_key = api_key or getattr(settings, "AI_API_KEY", None)
        model = model or getattr(settings, "AI_MODEL", None)

        self._client = client or AiVisionClient(
            base_url=base_url,
            api_key=api_key,
            model=model,
        )

    # ── AbstractAIAnalyzer interface ──────────────────────────────────────────

    def analyze_photo(self, photo: Any, prompt: str) -> List[Dict[str, Any]]:
        """
        Analisa uma foto de imóvel com o módulo padrão de visão do framework.

        1. Envia a foto + prompt para o modelo de IA (AiVisionClient)
        2. Parseia a resposta JSON em lista de {attribute_token, strength}
        3. Persiste os atributos no banco e recalcula os agregados da propriedade
        """
        if not prompt:
            return []

        try:
            response = self._client.analyze_photo(photo, prompt)
            attributes = AiAttributeParser.extract_attributes(response)
            SubjectiveAttributeRepository.replace_photo_attributes(photo, attributes)
            return attributes
        except Exception as exc:
            raise AiAnalysisError(f"Foto {photo.pk}: {exc}") from exc

    # analyze_post() herdado de AbstractAIAnalyzer (itera sobre photo em post.photos)
