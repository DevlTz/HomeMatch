import json
import logging
from typing import Any, Dict, List, Optional

from apps.ai_analysis.schema import VALID_TOKENS

logger = logging.getLogger(__name__)


class AiAttributeParser:
    """Parses the AI response (now a hierarchical JSON) into a flat list of
    namespaced {attribute_token, strength} dicts.
    """

    @staticmethod
    def extract_attributes(response) -> List[Dict[str, Any]]:
        """
        Takes either an OpenAI chat-like response or the adapted Gemini
        response, extracts the JSON content, and returns a flat list.
        """
        content = AiAttributeParser._get_content(response)
        if not content:
            return []

        data = AiAttributeParser._parse_json(content)
        if not isinstance(data, dict):
            logger.warning("AI response is not a dict; skipping")
            return []

        # Flatten to list of {attribute_token, strength}
        flat = []
        AiAttributeParser._flatten(data, prefix="", flat=flat)

        # filter out unknown tokens to guard against model errors
        valid_flat = [item for item in flat if item["attribute_token"] in VALID_TOKENS]
        if len(valid_flat) < len(flat):
            skipped = set(item["attribute_token"] for item in flat) - set(
                item["attribute_token"] for item in valid_flat
            )
            logger.debug("Skipped invalid tokens: %s", skipped)

        return valid_flat
    # Private helpers
    @staticmethod
    def _get_content(response) -> Optional[str]:
        """Extract the raw string content from the response object."""
        if not response.choices:
            return None

        choice = response.choices[0]
        # OpenAI chat completion
        if hasattr(choice, "message") and choice.message:
            return choice.message.content
        # Direct text attribute (some adapters, fallback)
        if hasattr(choice, "text"):
            return choice.text
        return None

    @staticmethod
    def _parse_json(content: str) -> Any:
        """Parse string content to Python object, with error handling."""
        if not isinstance(content, str):
            return content

        content = content.strip()
        if not content:
            return {}

        # Strip markdown code fences
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response JSON: %s", e)
            return {}

    @staticmethod
    def _flatten(obj: Any, prefix: str, flat: List[Dict[str, Any]]):
        """Recursively walk the hierarchical response and produce flat tokens.

        Scalars become `prefix + key` → {attribute_token, strength}.
        The special 'architecture' list yields tokens like
        `prefix + "architecture." + style` with strength = confidence.
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_prefix = f"{prefix}{key}" if prefix else key
                if key == "architecture" and isinstance(value, list):
                    # Architecture list: each item has {style, confidence}
                    for item in value:
                        if isinstance(item, dict):
                            style = item.get("style")
                            confidence = item.get("confidence")
                            if style and confidence is not None:
                                token = f"{new_prefix}.{style}"
                                AiAttributeParser._add_token(token, confidence, flat)
                elif isinstance(value, (int, float)):
                    # Leaf scalar
                    AiAttributeParser._add_token(new_prefix, value, flat)
                elif isinstance(value, dict):
                    # Nested group (like color)
                    AiAttributeParser._flatten(value, new_prefix + ".", flat)
                elif isinstance(value, list):
                    # Unexpected list
                    pass
        # ignore other types

    @staticmethod
    def _add_token(token: str, strength: float, flat: List[Dict[str, Any]]):
        try:
            strength = float(strength)
        except (TypeError, ValueError):
            return
        if 0.0 <= strength <= 1.0:
            flat.append({"attribute_token": token, "strength": strength})
        else:
            logger.debug(
                "Ignoring out-of-range strength for token %s: %s", token, strength
            )
