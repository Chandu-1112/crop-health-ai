import os

from google import genai
from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def ask_farmer_question(
    question: str,
    language: str = "en",
    crop: str | None = None,
    disease: str | None = None
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

    crop_context = crop or "unknown"
    disease_context = disease or "not diagnosed"

    prompt = f"""
You are a helpful agricultural assistant
for farmers.

Answer the farmer's question clearly and simply.

Farmer's language:
{selected_language}

Crop:
{crop_context}

Possible diagnosed disease or pest:
{disease_context}

Farmer's question:
{question}

Instructions:

- Answer in {selected_language}.
- Use simple farmer-friendly language.
- Give practical and safe advice.
- Prefer Integrated Pest Management (IPM).
- Do not recommend pesticides solely based on an AI diagnosis.
- If pesticide use is discussed, tell the farmer to follow
  the product label and local agricultural guidance.
- Do not invent pesticide doses.
- If the question requires expert confirmation,
  recommend contacting an agricultural expert.
- Keep the answer concise but useful.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()