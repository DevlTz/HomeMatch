"""
API usage test script for AI Analysis.

This script demonstrates how to use the OpenAI API for image analysis
with JSON schema responses. It encodes an image to base64 and sends it
to a local AI model for description.

Usage:
    python apps/ai_analysis/tests/api_usage_test.py

Requirements:
    - OpenAI package installed
    - Local AI server running on localhost:1234
    - Example image at apps/ai_analysis/tests/example_img.jpg
"""

import base64
from openai import OpenAI


def encode_image(image_path):
    """
    Encode an image file to base64 string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_path = (
    "apps/ai_analysis/tests/example_img.jpg"  # e.g., "apps/ai_analysis/tests/image.jpg"
)
base64_image = encode_image(image_path)

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)

try:
    response = client.chat.completions.create(
        model="qwen/qwen3.5-9b",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Descreva essa imagem, com foco em detalhes arquiteturais e ambientais (que interessariam um possivel morador)."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "image_description",
                "schema": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "objects": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["description"],
                },
            },
        },
    )
    print("Response:", response)
    if response.choices:
        message = response.choices[0].message
        content = message.content or message.reasoning_content
        print("Content:", content)
    else:
        print("No choices in response")
except Exception as e:
    print("Error:", e)
