import json


class AiAttributeParser:
    @staticmethod
    def extract_attributes(response):
        if not response.choices:
            return []

        choice = response.choices[0]
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None) if message is not None else None
        if content is None:
            content = getattr(choice, "text", None)

        parsed_content = AiAttributeParser._parse_content(content)
        attributes = (
            parsed_content.get("attributes") or parsed_content.get("subjective_attributes") or []
            if isinstance(parsed_content, dict)
            else []
        )
        return AiAttributeParser._normalize(attributes)

    @staticmethod
    def _parse_content(content):
        if isinstance(content, str):
            content = content.strip()
            if not content:
                return {}
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {}
        return content

    @staticmethod
    def _normalize(attributes):
        normalized = []
        for item in attributes:
            token = item.get("attribute_token") or item.get("token") or item.get("name")
            strength = item.get("strength") if item.get("strength") is not None else item.get("value")
            if token is None or strength is None:
                continue
            try:
                normalized.append({"attribute_token": str(token).strip(), "strength": float(strength)})
            except (TypeError, ValueError):
                continue
        return normalized
