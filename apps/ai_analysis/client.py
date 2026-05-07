import json
from pathlib import Path

from django.conf import settings

from apps.properties.services import generate_url
from apps.ai_analysis.schema import (
    PHOTO_ANALYSIS_RESPONSE_FORMAT,
    PHOTO_ANALYSIS_JSON_SCHEMA,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def _use_local():
    return getattr(settings, "USE_LOCAL_STORAGE", False)


class AiVisionClient:
    """Client that sends a photo (and prompt) to the AI model.

    Uses either:
    - Gemini native SDK (local files, no public URL required)
    - OpenAI‑compatible client (remote files via R2 public URLs)
    """

    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = base_url or settings.AI_API_BASE_URL
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL

        if not self.api_key:
            raise ValueError("AI_API_KEY must be configured in settings.")

        if _use_local():
            # Native Gemini SDK – raw bytes, no public URL needed
            if genai is None:
                raise ImportError(
                    "google-generativeai is required for local storage mode. "
                    "Run: pip install google-generativeai"
                )
            genai.configure(api_key=self.api_key)
            self._gemini_model = genai.GenerativeModel(self.model)
        else:
            # OpenAI-compatible client – requires public HTTPS URL (R2)
            if OpenAI is None:
                raise ImportError("openai package is required. Run: pip install openai")
            if not self.base_url:
                raise ValueError("AI_API_BASE_URL must be configured in settings.")
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def analyze_photo(self, photo, prompt: str):
        """Entry point – dispatches to local or remote call."""
        if _use_local():
            return self._analyze_local(photo, prompt)
        return self._analyze_remote(photo, prompt)

    def _analyze_local(self, photo, prompt: str):
        """Send image as raw bytes via native Gemini SDK."""
        file_path = Path(settings.MEDIA_ROOT) / photo.r2_key
        ext = file_path.suffix.lower().lstrip(".")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        # Append a compact description of the expected JSON so Gemini knows the shape.
        full_prompt = (
            f"{prompt}\n\n"
            "Return ONLY a JSON object matching this exact schema. "
            "No markdown fences, no extra text.\n"
            f"{json.dumps(PHOTO_ANALYSIS_JSON_SCHEMA)}"
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

    def _analyze_remote(self, photo, prompt: str):
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
            response_format=PHOTO_ANALYSIS_RESPONSE_FORMAT,
            max_tokens=1024,
        )


class _GeminiResponseAdapter:
    """
    Wraps the native Gemini SDK response in an OpenAI-compatible shape
    """

    def __init__(self, text: str):
        self.choices = [_Choice(text)]


class _Choice:
    def __init__(self, text: str):
        self.message = _Message(text)


class _Message:
    def __init__(self, text: str):
        # Strip markdown code fences if Gemini wraps the JSON in ```json ... ```
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[-1]
            clean = clean.rsplit("```", 1)[0].strip()
        self.content = clean
