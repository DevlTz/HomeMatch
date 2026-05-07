"""
Testes da funcionalidade do serviço de Análise de Inteligência Artificial.

Este módulo contém testes abrangentes para a classe AiAnalysisService,
cobrindo análise de fotos, persistência de atributos, agregação,
tratamento de erros e inicialização do serviço.
"""

import os
from unittest import skipUnless
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.ai_analysis.services import AiAnalysisService
from apps.properties.models import Condo, Properties, PropertiesPhotos, Rooms, RoomsExtras
from apps.ai_analysis.models import PhotoSubjectiveAttribute, PropertySubjectiveAttribute


class AiAnalysisServiceTest(TestCase):
    """
    Suite de testes para funcionalidade da classe AiAnalysisService.

    Os testes cobrem o fluxo completo de análise de fotos até persistência em banco de dados,
    incluindo casos extremos e condições de erro.
    """

    @override_settings(
        AI_API_BASE_URL="http://localhost:1234/v1",
        AI_API_KEY="test-api-key",
        AI_MODEL="qwen/qwen3.5-9b",
    )
    @patch("apps.ai_analysis.services.OpenAI")
    @patch("apps.ai_analysis.services.generate_url")
    def test_analyze_photo_saves_subjective_attributes(self, mock_generate_url, mock_openai_cls):
        """
        Test that analyze_photo saves attributes and creates property aggregates.

        Verifies that photo analysis creates PhotoSubjectiveAttribute records
        and corresponding PropertySubjectiveAttribute aggregates.
        """
        # Cria estrutura de teste com dados mínimos de propriedade
        rooms = Rooms.objects.create(bedrooms=1, bathrooms=1, parking_spots=0)
        extras = RoomsExtras.objects.create(living_room=True)
        condo = Condo.objects.create(name="Test Condo", address="Rua Teste 123")

        property_obj = Properties.objects.create(
            rooms=rooms,
            rooms_extras=extras,
            condo=condo,
            property_purpose="S",
            type="H",
            area=100.0,
            floors=1,
            price=100000.00,
            address="Rua Lorem, 123",
            neighborhood="Centro",
            city="Recife",
            has_mobilia=False,
            status=True,
            description="Test property",
            embedding="[]",
        )

        # Cria foto para análise
        photo = PropertiesPhotos.objects.create(
            property=property_obj,
            r2_key="properties/test.jpg",
            order=0,
        )

        # Configura mocks para simular resposta da API de IA
        mock_generate_url.return_value = "http://example.com/test.jpg"
        chat_mock = MagicMock()
        chat_mock.choices = [
            MagicMock(
                message=MagicMock(
                    content={
                        "attributes": [
                            {"attribute_token": "subjective_feature_a", "strength": 0.8},
                            {"attribute_token": "subjective_feature_b", "strength": 0.6},
                        ]
                    }
                )
            )
        ]
        mock_openai_cls.return_value.chat.completions.create.return_value = chat_mock

        # Executa análise de foto
        service = AiAnalysisService()
        attributes = service.analyze_photo(photo, "Analyze the image and return subjective attributes.")

        # Verifica se os atributos foram extraídos corretamente
        self.assertEqual(len(attributes), 2)
        # Verifica se os registros de atributos foram salvos no banco
        self.assertTrue(PhotoSubjectiveAttribute.objects.filter(photo=photo, attribute_token="subjective_feature_a").exists())
        self.assertTrue(PhotoSubjectiveAttribute.objects.filter(photo=photo, attribute_token="subjective_feature_b").exists())

        # Verifica se a agregação por propriedade foi criada corretamente
        property_attr = PropertySubjectiveAttribute.objects.get(property=property_obj, attribute_token="subjective_feature_a")
        self.assertAlmostEqual(property_attr.strength_mean, 0.8)

    @override_settings(
        AI_API_BASE_URL="http://localhost:1234/v1",
        AI_API_KEY="test-api-key",
        AI_MODEL="gpt-4o-mini",
    )
    @patch("apps.ai_analysis.services.OpenAI")
    @patch("apps.ai_analysis.services.generate_url")
    def test_multiple_photos_aggregation(self, mock_generate_url, mock_openai_cls):
        """
        Test that multiple photos correctly aggregate attribute strengths.

        Verifies that when multiple photos have the same attribute,
        the property aggregate shows the correct mean value.
        """
        # Cria estrutura de teste
        rooms = Rooms.objects.create(bedrooms=1, bathrooms=1, parking_spots=0)
        extras = RoomsExtras.objects.create(living_room=True)
        condo = Condo.objects.create(name="Test Condo", address="Rua Teste 123")

        property_obj = Properties.objects.create(
            rooms=rooms,
            rooms_extras=extras,
            condo=condo,
            property_purpose="S",
            type="H",
            area=100.0,
            floors=1,
            price=100000.00,
            address="Rua Lorem, 123",
            neighborhood="Centro",
            city="Recife",
            has_mobilia=False,
            status=True,
            description="Test property",
            embedding="[]",
        )

        # Cria duas "fotos" para teste de agregação
        photo1 = PropertiesPhotos.objects.create(
            property=property_obj,
            r2_key="properties/test1.jpg",
            order=0,
        )
        photo2 = PropertiesPhotos.objects.create(
            property=property_obj,
            r2_key="properties/test2.jpg",
            order=1,
        )

        # Configura mock da API com resposta padrão
        mock_generate_url.return_value = "http://example.com/test.jpg"
        expected_attribute_token = "comfort"
        chat_mock = MagicMock()
        chat_mock.choices = [
            MagicMock(
                message=MagicMock(
                    content={
                        "attributes": [
                            {"attribute_token": expected_attribute_token, "strength": 0.8},
                        ]
                    }
                )
            )
        ]
        mock_openai_cls.return_value.chat.completions.create.return_value = chat_mock

        # Analisa ambas as fotos
        service = AiAnalysisService()
        service.analyze_photo(photo1, "Analyze the image.")
        service.analyze_photo(photo2, "Analyze the image.")

        # Verifica se a agregação calculou a média corretamente
        property_attr = PropertySubjectiveAttribute.objects.get(property=property_obj, attribute_token=expected_attribute_token)
        self.assertAlmostEqual(property_attr.strength_mean, 0.8)

    @override_settings(
        AI_API_BASE_URL="http://localhost:1234/v1",
        AI_API_KEY="test-api-key",
        AI_MODEL="qwen/qwen3.5-9b",
    )
    @patch("apps.ai_analysis.services.OpenAI")
    @patch("apps.ai_analysis.services.generate_url")
    def test_invalid_response_handling(self, mock_generate_url, mock_openai_cls):
        """
        Test that invalid AI responses are handled gracefully.

        Verifies that malformed JSON responses don't cause crashes
        and no attributes are saved.
        """
        # Cria estrutura de teste
        rooms = Rooms.objects.create(bedrooms=1, bathrooms=1, parking_spots=0)
        extras = RoomsExtras.objects.create(living_room=True)
        condo = Condo.objects.create(name="Test Condo", address="Rua Teste 123")

        property_obj = Properties.objects.create(
            rooms=rooms,
            rooms_extras=extras,
            condo=condo,
            property_purpose="S",
            type="H",
            area=100.0,
            floors=1,
            price=100000.00,
            address="Rua Lorem, 123",
            neighborhood="Centro",
            city="Recife",
            has_mobilia=False,
            status=True,
            description="Test property",
            embedding="[]",
        )

        photo = PropertiesPhotos.objects.create(
            property=property_obj,
            r2_key="properties/test.jpg",
            order=0,
        )

        # Simula resposta inválida (JSON malformado)
        mock_generate_url.return_value = "http://example.com/test.jpg"
        chat_mock = MagicMock()
        chat_mock.choices = [
            MagicMock(
                message=MagicMock(
                    content="invalid json"
                )
            )
        ]
        mock_openai_cls.return_value.chat.completions.create.return_value = chat_mock

        # Executa análise com resposta inválida
        service = AiAnalysisService()
        attributes = service.analyze_photo(photo, "Analyze the image.")

        # Verifica que nenhum atributo foi salvo e não houve exceção
        self.assertEqual(len(attributes), 0)
        self.assertEqual(PhotoSubjectiveAttribute.objects.filter(photo=photo).count(), 0)

    @override_settings(
        AI_API_BASE_URL="http://localhost:1234/v1",
        AI_API_KEY="test-api-key",
        AI_MODEL="qwen/qwen3.5-9b",
    )
    @patch("apps.ai_analysis.services.OpenAI")
    @patch("apps.ai_analysis.services.generate_url")
    def test_photo_update_clears_old_attributes(self, mock_generate_url, mock_openai_cls):
        """
        Test that re-analyzing a photo clears old attributes.

        Verifies that when a photo is analyzed again, old attributes
        are removed and replaced with new ones.
        """
        # Cria estrutura de teste
        rooms = Rooms.objects.create(bedrooms=1, bathrooms=1, parking_spots=0)
        extras = RoomsExtras.objects.create(living_room=True)
        condo = Condo.objects.create(name="Test Condo", address="Rua Teste 123")

        property_obj = Properties.objects.create(
            rooms=rooms,
            rooms_extras=extras,
            condo=condo,
            property_purpose="S",
            type="H",
            area=100.0,
            floors=1,
            price=100000.00,
            address="Rua Lorem, 123",
            neighborhood="Centro",
            city="Recife",
            has_mobilia=False,
            status=True,
            description="Test property",
            embedding="[]",
        )

        photo = PropertiesPhotos.objects.create(
            property=property_obj,
            r2_key="properties/test.jpg",
            order=0,
        )

        # Primeira análise com um atributo
        mock_generate_url.return_value = "http://example.com/test.jpg"
        chat_mock = MagicMock()
        chat_mock.choices = [
            MagicMock(
                message=MagicMock(
                    content={
                        "attributes": [
                            {"attribute_token": "attribute_v1", "strength": 0.5},
                        ]
                    }
                )
            )
        ]
        mock_openai_cls.return_value.chat.completions.create.return_value = chat_mock

        service = AiAnalysisService()
        service.analyze_photo(photo, "Analyze the image.")

        # Verifica que o atributo antigo foi salvo
        self.assertTrue(PhotoSubjectiveAttribute.objects.filter(photo=photo, attribute_token="attribute_v1").exists())

        # Segunda análise com atributo diferente
        chat_mock.choices[0].message.content = {
            "attributes": [
                {"attribute_token": "attribute_v2", "strength": 0.9},
            ]
        }

        service.analyze_photo(photo, "Analyze the image again.")

        # Verifica que atributo antigo foi removido e novo foi adicionado
        self.assertFalse(PhotoSubjectiveAttribute.objects.filter(photo=photo, attribute_token="attribute_v1").exists())
        self.assertTrue(PhotoSubjectiveAttribute.objects.filter(photo=photo, attribute_token="attribute_v2").exists())

    @override_settings(
        AI_API_BASE_URL="http://localhost:1234/v1",
        AI_API_KEY="test-api-key",
        AI_MODEL="qwen/qwen3.5-9b",
    )
    @patch("apps.ai_analysis.services.OpenAI", None)
    def test_service_initialization_without_openai(self):
        """
        Test that service raises ImportError when OpenAI is not available.

        Verifies that the service properly handles missing OpenAI dependency.
        """
        # Verifica se ImportError é lançado quando OpenAI não está disponível
        with self.assertRaises(ImportError):
            AiAnalysisService()
