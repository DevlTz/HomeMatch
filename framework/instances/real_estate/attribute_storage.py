"""
framework/instances/real_estate/attribute_storage.py
──────────────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — ponto flexível 3.

Estende AbstractAttributeStorage usando os modelos Django existentes:
  - PhotoSubjectiveAttribute  → atributos por foto
  - PropertySubjectiveAttribute → agregados (média) por imóvel
  - SubjectiveAttributeRepository → operações atômicas de banco
"""

from __future__ import annotations
from typing import Any, Dict, List

from apps.ai_analysis.models import PropertySubjectiveAttribute
from apps.ai_analysis.repositories import SubjectiveAttributeRepository
from framework.abstract_attribute_storage import AbstractAttributeStorage


class RealEstateAttributeStorage(AbstractAttributeStorage):
    """
    Persistência de atributos para a Plataforma Imobiliária.

    Delega para SubjectiveAttributeRepository (ponto fixo do framework),
    que já implementa a lógica transacional e de agregação.
    """

    # ── AbstractAttributeStorage interface ────────────────────────────────────

    def save_photo_attributes(
        self, photo: Any, attributes: List[Dict[str, Any]]
    ) -> None:
        """
        Substitui todos os atributos de uma foto e recalcula as médias
        do imóvel (PropertySubjectiveAttribute).
        """
        SubjectiveAttributeRepository.replace_photo_attributes(photo, attributes)

    def refresh_post_aggregates(self, post: Any) -> None:
        """
        Recalcula médias de atributos do imóvel com base nas fotos.
        O 'post' aqui é um objeto Properties.
        """
        SubjectiveAttributeRepository.refresh_property_aggregates(post)

    def get_attributes_for_post(self, post: Any) -> List[Dict[str, Any]]:
        """
        Retorna os atributos agregados do imóvel como lista de dicts.
        """
        qs = PropertySubjectiveAttribute.objects.filter(property=post)
        return [
            {"attribute_token": a.attribute_token, "strength_mean": a.strength_mean}
            for a in qs
        ]
