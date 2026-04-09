"""
AI Analysis service for processing property photos with AI vision models.

This module provides the AiAnalysisService class for analyzing property photos
using AI vision models to extract subjective attributes like "comfortable" or "spacious".
"""

import json
from django.conf import settings
from django.db.models import Avg
from apps.properties.services import generate_url
from apps.ai_analysis.models import PhotoSubjectiveAttribute, PropertySubjectiveAttribute

try:
    from openai import OpenAI
except ImportError:
    # Permite que o módulo seja importado mesmo sem openai instalado
    OpenAI = None


class AiAnalysisService:
    """
    Service for analyzing property photos using AI vision models.

    Handles communication with AI APIs, extracts subjective attributes from responses,
    and persists the data to the database with proper aggregation.

    Attributes:
        base_url (str): Base URL for the AI API.
        api_key (str): API key for authentication.
        model (str): AI model to use for analysis.
        client (OpenAI): Configured OpenAI client instance.
    """

    # Serviço responsável pela análise de fotos de imóveis com modelos de visão de IA

    def __init__(self, base_url=None, api_key=None, model=None):
        """
        Initialize the AI analysis service.

        Args:
            base_url (str, optional): AI API base URL. Defaults to settings.AI_API_BASE_URL.
            api_key (str, optional): AI API key. Defaults to settings.AI_API_KEY.
            model (str, optional): AI model name. Defaults to settings.AI_MODEL.

        Raises:
            ValueError: If base_url or api_key are not configured.
            ImportError: If OpenAI package is not available.
        """
        # Carrega configurações da API de IA a partir de settings ou parâmetros
        self.base_url = base_url or settings.AI_API_BASE_URL
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL

        # Valida que as configurações obrigatórias foram fornecidas
        if not self.base_url or not self.api_key:
            raise ValueError("AI_API_BASE_URL and AI_API_KEY must be configured in settings.")

        # Valida que o pacote OpenAI está instalado
        if OpenAI is None:
            raise ImportError(
                "openai package is required to use AiAnalysisService. "
                "Install it with `pip install openai`."
            )

        # Inicializa cliente OpenAI com configurações fornecidas
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def analyze_photo(self, photo, prompt):
        """
        Analyze a single property photo using AI vision model.

        Sends the photo to the AI API with the given prompt, extracts attributes
        from the response, saves them to the database, and updates property aggregates.

        Args:
            photo: PropertiesPhotos instance to analyze.
            prompt (str): Analysis prompt describing what attributes to extract.

        Returns:
            list: List of extracted attributes with 'attribute_token' and 'strength' keys.

        Raises:
            Exception: If AI API call fails or response parsing encounters errors.
        """
        # Valida se o prompt foi fornecido
        if not prompt:
            return []

        # Gera URL pública da foto para envio à API de IA
        photo_url = generate_url(photo.r2_key)
        # Chama API com esquema JSON para garantir formato consistente
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": photo_url}},
                    ],
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "subjective_attributes",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "attributes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "attribute_token": {"type": "string"},
                                        "strength": {"type": "number"},
                                    },
                                    "required": ["attribute_token", "strength"],
                                },
                            }
                        },
                        "required": ["attributes"],
                    },
                },
            },
            max_tokens=1024,
        )

        # Extrai atributos da resposta da API com tratamento de erros
        attributes = self._extract_attributes(response)
        # Persiste atributos no banco de dados e atualiza agregações
        self.save_photo_attributes(photo, attributes)
        return attributes

    def analyze_property(self, property_obj, prompt):
        """
        Analyze all photos of a property.

        Iterates through all photos of the given property and analyzes each one.

        Args:
            property_obj: Properties instance to analyze.
            prompt (str): Analysis prompt for all photos.

        Returns:
            list: List of analysis results, each containing photo_id and attributes.
        """
        # Obtém todas as fotos associadas à propriedade
        photos = property_obj.photos.all()
        results = []
        # Processa cada foto individualmente
        for photo in photos:
            results.append({"photo_id": photo.id, "attributes": self.analyze_photo(photo, prompt)})
        return results

    def save_photo_attributes(self, photo, attributes):
        """
        Save extracted attributes for a photo to the database.

        Deletes existing attributes for the photo, creates new ones in bulk,
        and updates the property's aggregated attributes.

        Args:
            photo: PropertiesPhotos instance.
            attributes (list): List of attribute dicts with 'attribute_token' and 'strength'.
        """
        # Remove atributos anteriores se a foto for reanalisada
        PhotoSubjectiveAttribute.objects.filter(photo=photo).delete()
        objects = []

        # Prepara objetos para inserção em massa
        for attribute in attributes:
            objects.append(
                PhotoSubjectiveAttribute(
                    property=photo.property,
                    photo=photo,
                    attribute_token=attribute["attribute_token"],
                    strength=attribute["strength"],
                )
            )

        # Insere todos os atributos em uma única operação de banco de dados
        if objects:
            PhotoSubjectiveAttribute.objects.bulk_create(objects)

        # Recalcula agregações da propriedade com novos atributos
        self.update_property_aggregates(photo.property)

    def update_property_aggregates(self, property_obj):
        """
        Update aggregated subjective attributes for a property.

        Calculates mean strength values for each attribute across all photos
        of the property and updates the PropertySubjectiveAttribute records.

        Args:
            property_obj: Properties instance to update aggregates for.
        """
        # Agrupa atributos por token e calcula a média de força
        grouped = (
            PhotoSubjectiveAttribute.objects
            .filter(property=property_obj)
            .values("attribute_token")
            .annotate(strength_mean=Avg("strength"))
        )

        # Atualiza ou cria registros agregados com as novas médias
        current_tokens = set()
        for item in grouped:
            current_tokens.add(item["attribute_token"])
            PropertySubjectiveAttribute.objects.update_or_create(
                property=property_obj,
                attribute_token=item["attribute_token"],
                defaults={"strength_mean": item["strength_mean"]},
            )

        # Remove agregações de atributos que não existem mais
        PropertySubjectiveAttribute.objects.filter(property=property_obj).exclude(attribute_token__in=current_tokens).delete()

    def _extract_attributes(self, response):
        """
        Extract and normalize attributes from AI API response.

        Handles different response formats and normalizes attribute data.

        Args:
            response: AI API response object.

        Returns:
            list: Normalized list of attributes with 'attribute_token' and 'strength'.
        """
        # Valida se a resposta contém 'choices'
        if not response.choices:
            return []

        # Extrai a primeira escolha da resposta
        choice = response.choices[0]
        message = getattr(choice, "message", None)
        content = None

        # Navega para encontrar o conteúdo da mensagem em diferentes formatos
        if message is not None:
            content = getattr(message, "content", None)
        if content is None:
            content = getattr(choice, "text", None)

        # Processa conteúdo em formato string (JSON)
        if isinstance(content, str):
            content = content.strip()
            if not content:
                return []
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                # Retorna lista vazia se JSON for inválido
                return []

        # Extrai lista de atributos com suporte a múltiplas chaves
        if isinstance(content, dict):
            attributes = content.get("attributes") or content.get("subjective_attributes") or []
        else:
            attributes = []

        # Normaliza cada atributo com validação e conversão de tipos
        normalized = []
        for item in attributes:
            # Tenta encontrar token em diferentes formatos de resposta
            token = item.get("attribute_token") or item.get("token") or item.get("name")
            # Tenta encontrar força em diferentes formatos de resposta
            strength = item.get("strength") if item.get("strength") is not None else item.get("value")
            if token is None or strength is None:
                continue
            try:
                # Normaliza token para string e força para float
                normalized.append({"attribute_token": str(token).strip(), "strength": float(strength)})
            except (TypeError, ValueError):
                # Ignora itens que não podem ser convertidos
                continue

        return normalized
