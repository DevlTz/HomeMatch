from django.conf import settings

from apps.properties.services import generate_url

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


SUBJECTIVE_ATTRIBUTES_RESPONSE_FORMAT = {
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
}


class AiVisionClient:
    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = base_url or settings.AI_API_BASE_URL
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL

        if not self.base_url or not self.api_key:
            raise ValueError("AI_API_BASE_URL and AI_API_KEY must be configured in settings.")
        if OpenAI is None:
            raise ImportError(
                "openai package is required to use AiAnalysisService. "
                "Install it with `pip install openai`."
            )
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def analyze_photo(self, photo, prompt):
        photo_url = generate_url(photo.r2_key)
        return self.client.chat.completions.create(
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
            response_format=SUBJECTIVE_ATTRIBUTES_RESPONSE_FORMAT,
            max_tokens=1024,
        )
