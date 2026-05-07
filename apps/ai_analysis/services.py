"""
Service facade for AI analysis workflows.
"""

from django.conf import settings

from apps.ai_analysis.client import AiVisionClient
from apps.ai_analysis.exceptions import AiAnalysisError
from apps.ai_analysis.parser import AiAttributeParser
from apps.ai_analysis.repositories import SubjectiveAttributeRepository


class AiAnalysisService:
    """Orchestrates AI photo/property analysis.

    Validates required credentials at construction time so failures are loud
    and early rather than buried inside a request cycle.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        client: AiVisionClient | None = None,
    ) -> None:
        base_url = base_url or settings.AI_API_BASE_URL
        api_key = api_key or settings.AI_API_KEY
        model = model or settings.AI_MODEL

        if not base_url or not api_key:
            raise ValueError(
                "AI_API_BASE_URL and AI_API_KEY must be set in settings / environment."
            )

        # Build the concrete HTTP client once and inject it into use-cases.
        self.client = client or AiVisionClient(
            base_url=base_url,
            api_key=api_key,
            model=model,
        )

    def analyze_photo(self, photo, prompt: str):
        """Public API: analyze a single photo and return its attributes."""
        # handle empty prompts
        if not prompt:
            return []

        try:
            # Delegate to the AI provider
            response = self.client.analyze_photo(photo, prompt)
            # Parse the JSON into a flat list of {attribute_token, strength}
            attributes = AiAttributeParser.extract_attributes(response)
            # Persist photo attributes and refresh property aggregates
            SubjectiveAttributeRepository.replace_photo_attributes(photo, attributes)
            # Used only for testing/admin purposes (in analyze_property), not needed for the main workflow
            return attributes
        except Exception as exc: 
            raise AiAnalysisError(f"Photo {photo.pk}: {exc}") from exc

    def analyze_property(self, property_obj, prompt: str):
        """Public API: analyze all photos in a property.
        Used for on-demand analysis of existing properties, e.g. via admin action."""
        results: list[dict] = []

        for photo in property_obj.photos.all():
            attributes = self.analyze_photo(photo, prompt)
            results.append({"photo_id": photo.id, "attributes": attributes})

        return results