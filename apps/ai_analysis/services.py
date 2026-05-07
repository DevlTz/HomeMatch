"""
Service facade for AI analysis workflows.
"""

from django.conf import settings

from apps.ai_analysis.client import AiVisionClient
from apps.ai_analysis.exceptions import AiAnalysisError
from apps.ai_analysis.parser import AiAttributeParser
from apps.ai_analysis.repositories import SubjectiveAttributeRepository


class AnalyzePhotoUseCase:
    """Use case that sends a single photo to the AI provider and persists
    the returned attributes.
    """

    def __init__(self, client: AiVisionClient | None = None) -> None:
        self.client = client or AiVisionClient()

    def execute(self, photo, prompt: str):
        # handle empty prompts
        if not prompt:
            return []
        # Delegate to the AI provider
        response = self.client.analyze_photo(photo, prompt)
        # Parse the JSON into a flat list of {attribute_token, strength}
        attributes = AiAttributeParser.extract_attributes(response)
        # Persist photo attributes and refresh property aggregates
        SubjectiveAttributeRepository.replace_photo_attributes(photo, attributes)
        return attributes


class AnalyzePropertyUseCase:
    """Use case that iterates through all photos of a property and runs
    photo analysis for each one.

    A separate use case class keeps this loop logic reusable and testable.
    Even though it lives in the same module as the service, it remains
    independent of controller concerns.
    """

    def __init__(self, analyze_photo_use_case: AnalyzePhotoUseCase | None = None) -> None:
        self.analyze_photo_use_case = analyze_photo_use_case or AnalyzePhotoUseCase()

    def execute(self, property_obj, prompt: str):
        results: list[dict] = []
        for photo in property_obj.photos.all():
            attributes = self.analyze_photo_use_case.execute(photo, prompt)
            results.append({"photo_id": photo.id, "attributes": attributes})
        return results


class AiAnalysisService:
    """Orchestrates AI photo/property analysis.

    Validates required credentials at construction time so failures are loud
    and early rather than buried inside a request cycle.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None) -> None:
        base_url = base_url or settings.AI_API_BASE_URL
        api_key = api_key or settings.AI_API_KEY
        model = model or settings.AI_MODEL

        if not base_url or not api_key:
            raise ValueError(
                "AI_API_BASE_URL and AI_API_KEY must be set in settings / environment."
            )

        # Validate that an OpenAI‑compatible client is installed when using remote analysis.
        # Import inside the constructor to avoid circular imports and to give a clear
        # error message at startup rather than during the first call.
        try:
            from apps.ai_analysis.client import OpenAI
        except ImportError:
            OpenAI = None
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

    def analyze_photo(self, photo, prompt: str):
        """Public API: analyze a single photo and return its attributes."""
        try:
            return self.analyze_photo_use_case.execute(photo, prompt)
        except Exception as exc:  # noqa: BLE001  # bubble up domain errors as service errors
            raise AiAnalysisError(f"Photo {photo.pk}: {exc}") from exc

    def analyze_property(self, property_obj, prompt: str):
        """Public API: analyze all photos in a property."""
        return self.analyze_property_use_case.execute(property_obj, prompt)