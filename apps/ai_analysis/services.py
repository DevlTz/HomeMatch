"""Service facade for AI analysis workflows.

Follows the layered architecture: View -> Service -> UseCase -> Repository.
"""

from django.conf import settings

from apps.ai_analysis.client import AiVisionClient, OpenAI
from apps.ai_analysis.use_cases import AnalyzePhotoUseCase, AnalyzePropertyUseCase


class AiAnalysisService:
    """Orchestrates AI photo/property analysis.

    Validates required credentials at construction time so failures are loud
    and early rather than buried inside a request cycle.
    """

    def __init__(self, base_url=None, api_key=None, model=None):
        base_url = base_url or settings.AI_API_BASE_URL
        api_key = api_key or settings.AI_API_KEY
        model = model or settings.AI_MODEL

        if not base_url or not api_key:
            raise ValueError(
                "AI_API_BASE_URL and AI_API_KEY must be set in settings / environment."
            )
        if OpenAI is None:
            raise ImportError(
                "openai package is required. Install it with `pip install openai`."
            )

        # Build the concrete HTTP client once and inject it into use-cases.
        client = AiVisionClient(base_url=base_url, api_key=api_key, model=model)
        analyze_photo_uc = AnalyzePhotoUseCase(client=client)

        self.analyze_photo_use_case = analyze_photo_uc
        self.analyze_property_use_case = AnalyzePropertyUseCase(
            analyze_photo_use_case=analyze_photo_uc
        )

    def analyze_photo(self, photo, prompt):
        return self.analyze_photo_use_case.execute(photo, prompt)

    def analyze_property(self, property_obj, prompt):
        return self.analyze_property_use_case.execute(property_obj, prompt)
