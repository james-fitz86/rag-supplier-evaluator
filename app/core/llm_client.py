import json
from typing import Any, Dict

from app.core.config import settings


class LLMClientError(RuntimeError):
    pass


class OpenAIJsonClient:
    """
    Minimal sync client that exposes:
        chat_json(system: str, user: str) -> dict

    It forces the model to return a JSON object and parses it into a Python dict.
    """

    def __init__(self, api_key: str, model: str):
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise LLMClientError(
                "OpenAI SDK not installed. Add 'openai' to requirements.txt."
            ) from e

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def chat_json(self, system: str, user: str) -> Dict[str, Any]:
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            content = resp.choices[0].message.content or "{}"
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise LLMClientError(f"Model did not return valid JSON: {e}") from e
        except Exception as e:
            raise LLMClientError(f"LLM call failed: {e}") from e


def build_llm_client() -> OpenAIJsonClient:
    if not settings.openai_api_key:
        raise LLMClientError(
            "OPENAI_API_KEY not set. Add it to your .env to enable extraction."
        )
    return OpenAIJsonClient(api_key=settings.openai_api_key, model=settings.llm_model)
