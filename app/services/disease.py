import os
import json

from google import genai
from google.genai import types
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")


# Create Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_crop_image(
    image_bytes: bytes,
    crop: str,
    mime_type: str,
    language: str = "en"
):
    language_names = {
        "en": "English",
        "te": "Telugu",
        "hi": "Hindi"
    }

    selected_language = language_names.get(
        language,
        "English"
    )

    prompt = f"""
You are an agricultural crop disease diagnosis assistant.

Analyze the provided crop/plant image.

Crop: {crop}

Identify the most likely:
1. Disease or pest
2. Confidence from 0 to 1
3. Severity: low, medium, or high
4. Approximate affected leaf/plant area percentage
5. Short explanation of the visible symptoms

The farmer's preferred language is:
{selected_language}

Return the disease or pest name in English.

Return the explanation in {selected_language}.

Return ONLY valid JSON in this exact format:

{{
    "disease": "disease or pest name",
    "confidence": 0.0,
    "severity": "low",
    "affected_area": 0.0,
    "explanation": "short explanation"
}}

Rules:

- confidence must be a number between 0 and 1.
- severity must be one of:
  "low", "medium", "high"
- affected_area must be a number between 0 and 100.
- If the image is unclear, use:
  "disease": "Unable to determine"
- If the image does not contain a crop or plant, use:
  "disease": "Unable to determine"
- If the image is unclear or does not contain a plant, confidence must be below 0.3.
- Do not include Markdown.
- Do not include ```json.
- Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),
            prompt
        ]
    )

    text = response.text.strip()

    # Remove Markdown code fences if Gemini returns them
    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Convert JSON text into Python dictionary
    try:
        result = json.loads(text)

    except json.JSONDecodeError:
        raise ValueError(
            f"Gemini returned invalid JSON: {text}"
        )

    return result