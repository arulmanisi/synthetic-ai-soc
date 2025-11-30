import json
import os
from typing import Optional, Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str: ...


class OpenAIClient:
    """Thin wrapper around OpenAI Chat Completions."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate(self, prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a SOC analyst that responds in JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""


def build_llm_client() -> Optional[LLMClient]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        return None
    try:
        return OpenAIClient(api_key=api_key, model=model)
    except Exception:
        return None
