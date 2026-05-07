"""
apps/ai_analysis/schema.py
──────────────────────────
Single source of truth for every attribute token the HomeMatch AI analysis
system can produce.  The JSON schema sent to the LLM and the flat validation
table are both *derived* from ATTRIBUTE_REGISTRY.

To add, remove, or rename an attribute, edit ATTRIBUTE_REGISTRY here and
redeploy.

Token naming convention
    <category>.<subcategory>.<leaf>   →  aesthetics.color.brightness
    <category>.<leaf>                 →  livability.coziness

Confidence vs. strength
    Scalar attributes (0–1) use the word "strength" throughout the storage
    layer (legacy).  For architectural styles, the LLM field is "confidence" but 
    it is stored as "strength" in the DB so the repository layer needs no change.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# Allowed architectural style tokens.
# Constrained in the JSON schema enum so the LLM cannot hallucinate styles.
# ─────────────────────────────────────────────────────────────────────────────
ARCHITECTURAL_STYLES: list[str] = [
    "colonial_portuguese",
    "baroque",
    "neoclassical",
    "eclectic",
    "art_nouveau",
    "art_deco",
    "modernist_brazilian",
    "tropical_modernist",
    "brutalist",
    "postmodern",
    "contemporary",
    "vernacular_regional",
    "vernacular_coastal",
    "neo_colonial",
    "minimalist",
    "high_rise_modern",
    "gated_community_suburban",
]

# ─────────────────────────────────────────────────────────────────────────────
# Master registry
#
# Two shapes are supported:
#   dict  → has subcategories  (aesthetics → color, architecture)
#   list  → flat leaf list     (livability, current_state)
#
# "architecture" leaves are ARCHITECTURAL_STYLES; the LLM returns them as a
# list of {style, confidence} objects rather than plain scalars.
# ─────────────────────────────────────────────────────────────────────────────
ATTRIBUTE_REGISTRY: dict = {
    "aesthetics": {
        # Lighting & colour, all scalars in [0, 1]
        "color": ["visual_warmth", "brightness", "saturation"],
        # Architectural style influences (list of {style, confidence})
        "architecture": ARCHITECTURAL_STYLES,
    },
    "livability": [
        "coziness",  # warmth and intimacy of the space
        "verdancy",  # presence of plants or natural elements
        "humidity",  # perceived moisture (0 = dry, 1 = very humid)
        "spaciousness",  # how open the space feels
    ],
    "current_state": [
        "cleanliness",  # visible tidiness and absence of damage
        "ventilation",  # apparent airflow and window access
        "leisure",  # entertainment or relaxation areas visible
        "structural_integrity",  # condition of visible walls/floors/ceilings
    ],
}


# Flat valid-token set
def _build_valid_tokens() -> frozenset[str]:
    tokens: set[str] = set()
    for category, body in ATTRIBUTE_REGISTRY.items():
        if isinstance(body, dict):
            for subcat, attrs in body.items():
                for attr in attrs:
                    tokens.add(f"{category}.{subcat}.{attr}")
        else:
            for attr in body:
                tokens.add(f"{category}.{attr}")
    return frozenset(tokens)


VALID_TOKENS: frozenset[str] = _build_valid_tokens()

# JSON Schema 
def _scalar(description: str) -> dict:
    """Shorthand for a bounded [0, 1] number field."""
    return {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0,
        "description": description,
    }


PHOTO_ANALYSIS_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": ["aesthetics", "livability", "current_state"],
    "properties": {
        # aesthetics
        "aesthetics": {
            "type": "object",
            "additionalProperties": False,
            "required": ["color", "architecture"],
            "properties": {
                "color": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["visual_warmth", "brightness", "saturation"],
                    "properties": {
                        "visual_warmth": _scalar(
                            "Orange/red/yellow tones = 1.0; blue/green/grey = 0.0"
                        ),
                        "brightness": _scalar(
                            "Bright, well-lit space = 1.0; dark or dim = 0.0"
                        ),
                        "saturation": _scalar(
                            "Vivid, saturated colours = 1.0; grey/muted = 0.0"
                        ),
                    },
                },
                "architecture": {
                    "type": "array",
                    "description": (
                        "Detected architectural style influences, most dominant first. "
                        "List 1–3 styles; omit any with confidence below 0.15."
                    ),
                    "minItems": 1,
                    "maxItems": 3,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["style", "confidence"],
                        "properties": {
                            "style": {
                                "type": "string",
                                "enum": ARCHITECTURAL_STYLES,
                            },
                            "confidence": _scalar(
                                "How strongly this style is expressed "
                                "(1.0 = unmistakably this style)"
                            ),
                        },
                    },
                },
            },
        },
        # livability
        "livability": {
            "type": "object",
            "additionalProperties": False,
            "required": ["coziness", "verdancy", "humidity", "spaciousness"],
            "properties": {
                "coziness": _scalar("Warm, homey, intimate feeling"),
                "verdancy": _scalar("Visible plants and natural elements"),
                "humidity": _scalar("Perceived moisture/dampness (0 = dry)"),
                "spaciousness": _scalar("Open, uncluttered, airy feel"),
            },
        },
        # current_state
        "current_state": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "cleanliness",
                "ventilation",
                "leisure",
                "structural_integrity",
            ],
            "properties": {
                "cleanliness": _scalar("Visible tidiness; 1 = spotless"),
                "ventilation": _scalar("Airflow & window access; 1 = very airy"),
                "leisure": _scalar("Entertainment or relaxation areas visible"),
                "structural_integrity": _scalar(
                    "Condition of surfaces; 1 = new/perfect, 0 = damaged"
                ),
            },
        },
    },
}

# Convenience wrapper used by client.py
PHOTO_ANALYSIS_RESPONSE_FORMAT: dict = {
    "type": "json_schema",
    "json_schema": {
        "name": "photo_analysis",
        "strict": True,
        "schema": PHOTO_ANALYSIS_JSON_SCHEMA,
    },
}
