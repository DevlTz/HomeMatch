import base64
import json
from pathlib import Path

from django.conf import settings

from apps.properties.services import generate_url

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


SUBJECTIVE_ATTRIBUTES_SCHEMA = {
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
}

SUBJECTIVE_ATTRIBUTES_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "subjective_attributes",
        "schema": SUBJECTIVE_ATTRIBUTES_SCHEMA,
    },
}


def _use_local():
    return getattr(settings, "USE_LOCAL_STORAGE", False)


class AiVisionClient:
    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = base_url or settings.AI_API_BASE_URL
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL

        if not self.api_key:
            raise ValueError("AI_API_KEY must be configured in settings.")

        if _use_local():
            # Use native Gemini SDK — supports raw bytes, no public URL needed
            if genai is None:
                raise ImportError(
                    "google-generativeai is required for local storage mode. "
                    "Run: pip install google-generativeai"
                )
            genai.configure(api_key=self.api_key)
            self._gemini_model = genai.GenerativeModel(self.model)
        else:
            # Use OpenAI-compatible client — requires public HTTPS URL (R2)
            if OpenAI is None:
                raise ImportError("openai package is required. Run: pip install openai")
            if not self.base_url:
                raise ValueError("AI_API_BASE_URL must be configured in settings.")
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def analyze_photo(self, photo, prompt):
        if _use_local():
            return self._analyze_local(photo, prompt)
        return self._analyze_remote(photo, prompt)

    def _analyze_local(self, photo, prompt):
        """Send image as raw bytes via native Gemini SDK — works without a public URL."""
        file_path = Path(settings.MEDIA_ROOT) / photo.r2_key
        ext = file_path.suffix.lower().lstrip(".")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        full_prompt = (
            f"{prompt}\n\n"
            "Respond ONLY with a JSON object matching this schema, no extra text:\n"
            f"{json.dumps(SUBJECTIVE_ATTRIBUTES_SCHEMA)}"
        )

        response = self._gemini_model.generate_content(
            [
                {"mime_type": mime, "data": image_bytes},
                full_prompt,
            ]
        )

        # Wrap response in an OpenAI-compatible shape so the existing
        # AiAttributeParser works without any changes
        return _GeminiResponseAdapter(response.text)

    def _analyze_remote(self, photo, prompt):
        """Send image as public HTTPS URL via OpenAI-compatible client (R2 mode)."""
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


class _GeminiResponseAdapter:
    """
    Wraps the native Gemini SDK response in an OpenAI-compatible shape
    so AiAttributeParser.extract_attributes() works unchanged.
    """

    def __init__(self, text):
        self.choices = [_Choice(text)]


class _Choice:
    def __init__(self, text):
        self.message = _Message(text)


class _Message:
    def __init__(self, text):
        # Strip markdown code fences if Gemini wraps the JSON in ```json ... ```
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[-1]
            clean = clean.rsplit("```", 1)[0]
        self.content = clean.strip()
