"""
Async wrapper for LLM calls via Langdock (OpenAI-compatible) or Straico API.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from openai import AsyncOpenAI

from mcp_lektor.core.models import ProofreadingConfig

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Du bist ein professioneller deutscher Lektor. Prüfe den folgenden Text auf \
Fehler und gib Korrekturen als JSON-Array zurück.

Regeln:
- Ignoriere Platzhalter-Text (rot markiert, in eckigen Klammern).
- Verwende deutsche typografische Konventionen.
- Gib NUR echte Fehler zurück, keine stilistischen Vorschläge.
- Klassifiziere jede Korrektur mit einer Kategorie und Konfidenzstufe.

Antworte AUSSCHLIESSLICH mit einem JSON-Array im folgenden Format:
[
  {
    "paragraph_index": <int>,
    "run_index": <int>,
    "char_offset_start": <int>,
    "char_offset_end": <int>,
    "original_text": "<fehlerhafter Text>",
    "suggested_text": "<korrigierter Text>",
    "category": "<Rechtschreibung|Grammatik|Zeichensetzung|Anrede-Konsistenz>",
    "confidence": "<high|medium|low>",
    "explanation": "<kurze Erklärung>"
  }
]

Wenn keine Fehler vorhanden sind, antworte mit einem leeren Array: []
"""

import asyncio

async def call_llm_for_proofreading(
    paragraphs_json: str,
    config: ProofreadingConfig,
    checks: list[str],
) -> list[dict[str, Any]]:
    """
    Send a batch of paragraphs to the LLM and parse corrections.
    Includes an exponential backoff retry mechanism for robustness (Problem 3.4).
    """
    straico_key = os.environ.get("STRAICO_API_KEY")
    max_retries = config.llm_max_retries
    delay = config.llm_retry_initial_delay_seconds
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if straico_key:
                return await _call_straico(paragraphs_json, straico_key, config, checks)
            else:
                return await _call_langdock(paragraphs_json, config, checks)
        except Exception as exc:
            last_exception = exc
            if attempt < max_retries:
                logger.warning(
                    f"LLM API attempt {attempt+1}/{max_retries+1} failed: {exc}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= 2 # Exponential backoff
            else:
                logger.error(f"LLM API final attempt failed: {exc}")
    
    return []

async def _call_langdock(
    paragraphs_json: str,
    config: ProofreadingConfig,
    checks: list[str],
) -> list[dict[str, Any]]:
    """Langdock / OpenAI-compatible call."""
    client = AsyncOpenAI(
        api_key=config.langdock_api_key or os.environ.get("LANGDOCK_API_KEY", ""),
        base_url=config.langdock_api_base,
    )

    checks_hint = ", ".join(checks)
    user_message = (
        f"Prüfe den folgenden Text auf: {checks_hint}.\n\n"
        f"Absätze (JSON):\n{paragraphs_json}"
    )

    response = await client.chat.completions.create(
        model=config.llm_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens_per_call,
    )
    content = response.choices[0].message.content or "[]"
    return _parse_json_content(content)

async def _call_straico(
    paragraphs_json: str,
    api_key: str,
    config: ProofreadingConfig,
    checks: list[str],
) -> list[dict[str, Any]]:
    """Straico API call using httpx."""
    url = "https://api.straico.com/v1/prompt/completion"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    checks_hint = ", ".join(checks)
    full_prompt = (
        f"{_SYSTEM_PROMPT}\n\n"
        f"Prüfe den folgenden Text auf: {checks_hint}.\n\n"
        f"Absätze (JSON):\n{paragraphs_json}"
    )

    payload = {
        "models": [config.llm_model or "anthropic/claude-3.5-sonnet"],
        "message": full_prompt,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        
        # Straico response structure check
        completions = data.get("data", {}).get("completions", {})
        if not completions:
            logger.warning(f"Straico returned unexpected structure: {data}")
            return []
        
        # Get the first model's completion
        first_model_data = next(iter(completions.values()))
        content = first_model_data.get("completion", {}).get("choices", [{}])[0].get("message", {}).get("content", "[]")
        
        return _parse_json_content(content)

def _parse_json_content(content: str) -> list[dict[str, Any]]:
    """Helper to clean and parse JSON from LLM string."""
    content = content.strip()
    if content.startswith("```"):
        # Remove markdown code blocks if present
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        logger.warning(f"LLM returned unparseable JSON: {exc}\nContent: {content[:100]}...")
        return []
