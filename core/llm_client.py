from __future__ import annotations

import os
from typing import Optional

from anthropic import Anthropic

_client: Optional[Anthropic] = None

MODEL = os.getenv("ANTHROPIC_CHAT_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "512"))


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def chat(
    system_prompt: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = MAX_TOKENS,
) -> str:
    resp = get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
        temperature=temperature,
    )
    return "".join(
        block.text for block in resp.content if block.type == "text"
    ).strip()
