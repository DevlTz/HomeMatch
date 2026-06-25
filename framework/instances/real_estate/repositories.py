"""
framework/instances/real_estate/repositories.py
─────────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — pontos flexíveis 6 e 7.

RealEstateUserRepository → estende AbstractUserRepository
RealEstatePostRepository → estende AbstractPostRepository

Ambas delegam para os repositórios Django existentes (apps/users e
apps/properties), demonstrando que a instância imobiliária reutiliza
a camada de dados original sem reimplementação.
"""

from __future__ import annotations
from typing import Any, List, Optional

from apps.properties.models import Properties
from apps.properties.repositories import PropertyRepository
from apps.users.repositories import UserRepository as _DjangoUserRepo
from framework.abstract_post_repository import AbstractPostRepository
from framework.abstract_user_repository import AbstractUserRepository


# ─────────────────────────────────────────────────────────────────────────────
# Ponto flexível 6 — Repositório de usuários
# ─────────────────────────────────────────────────────────────────────────────

class RealEstateUserRepository(AbstractUserRepository):
    """
    Repositório de usuários para a Plataforma Imobiliária.
    Delega para apps.users.repositories.UserRepository (ponto fixo).
    """

    def create_user(
        self, *, email: str, name: str, user_type: str, password: str
    ) -> Any:
        return _DjangoUserRepo.create_user(
            email=email, name=name, user_type=user_type, password=password
        )

    def email_exists(self, email: str) -> bool:
        return _DjangoUserRepo.email_exists(email)

    def save_user(self, user: Any) -> Any:
        return _DjangoUserRepo.save_user(user)

    def get_by_email(self, email: str) -> Optional[Any]:
        from apps.users.models import User
        return User.objects.filter(email=email).first()


# ─────────────────────────────────────────────────────────────────────────────
# Ponto flexível 7 — Repositório de postagens (imóveis)
# ─────────────────────────────────────────────────────────────────────────────

class RealEstatePostRepository(AbstractPostRepository):
    """
    Repositório de postagens para a Plataforma Imobiliária.
    A "postagem" aqui é um objeto Properties (imóvel).
    """

    def create_post(self, *, owner: Any, validated_data: dict) -> Any:
        """
        Cria um imóvel.  validated_data deve incluir rooms, rooms_extras e
        condo já resolvidos (ou None para condo).
        """
        rooms_data = validated_data.pop("rooms", {})
        rooms_extras_data = validated_data.pop("rooms_extras", {})
        condo_data = validated_data.pop("condo", None)

        rooms, _ = PropertyRepository.get_or_create_rooms(rooms_data)
        rooms_extras, _ = PropertyRepository.get_or_create_rooms_extras(rooms_extras_data)
        condo = None
        if condo_data:
            condo, _ = PropertyRepository.get_or_create_condo(condo_data)

        validated_data["owner"] = owner
        return PropertyRepository.create_property(
            rooms=rooms,
            rooms_extras=rooms_extras,
            condo=condo,
            validated_data=validated_data,
        )

    def save_post(self, post: Any) -> Any:
        return PropertyRepository.save_model(post)

    def list_posts(self) -> List[Any]:
        return list(PropertyRepository.list_properties_with_order())

    def get_post_by_id(self, post_id: Any) -> Optional[Any]:
        return Properties.objects.filter(pk=post_id).first()
