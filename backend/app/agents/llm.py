"""
Thin Groq wrapper.
"""

import json
from pydantic import ValidationError
from groq import Groq
from app.config import settings

DEFAULT_MODEL = "openai/gpt-oss-120b"

_client = None


def get_llm_client():
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to backend/.env and restart.")
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def _extract_json(text):
    fence = chr(96) * 3
    text = text.replace(fence + "json", "").replace(fence, "")
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text.strip()


def call_llm_json(system_prompt, user_prompt, output_model, model=DEFAULT_MODEL,
                  temperature=0.2, max_retries=1):
    client = get_llm_client()
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or ""
            cleaned = _extract_json(raw)
            data = json.loads(cleaned)
            return output_model.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            if attempt < max_retries:
                user_prompt = user_prompt + "\n\nREMINDER: Respond with ONLY a valid JSON object."
                continue
        except Exception as e:
            raise RuntimeError("Groq call failed: " + str(e))
    raise RuntimeError("LLM returned unparseable output: " + str(last_error))
