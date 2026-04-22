"""Compatibility facade for AI analysis workflows."""

from apps.ai_analysis import client as ai_client_module
from apps.ai_analysis.client import OpenAI
from apps.ai_analysis.use_cases import AnalyzePhotoUseCase, AnalyzePropertyUseCase
from apps.properties.services import generate_url


class AiAnalysisService:
    def __init__(self, base_url=None, api_key=None, model=None):
        ai_client_module.OpenAI = OpenAI
        ai_client_module.generate_url = generate_url
        self.analyze_photo_use_case = AnalyzePhotoUseCase(
            client=ai_client_module.AiVisionClient(base_url=base_url, api_key=api_key, model=model)
        )
        self.analyze_property_use_case = AnalyzePropertyUseCase(
            analyze_photo_use_case=self.analyze_photo_use_case
        )

    def analyze_photo(self, photo, prompt):
        return self.analyze_photo_use_case.execute(photo, prompt)

    def analyze_property(self, property_obj, prompt):
        return self.analyze_property_use_case.execute(property_obj, prompt)
