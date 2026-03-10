"""
Async wrapper for LLM calls via Langdock (OpenAI-compatible) or Straico API (v.0).
"""

from __future__ import annotations

import json
import logging
import os
import asyncio
from typing import Any

import httpx
from openai import AsyncOpenAI

from mcp_lektor.config.models import ProofreadingConfig

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

WICHTIG: Alle Textwerte müssen valider JSON-Code sein. Doppelte Anführungszeichen innerhalb von Texten MÜSSEN mit einem Backslash maskiert werden (\").

Wenn keine Fehler vorhanden sind, antworte mit einem leeren Array: []
"""

async def call_llm_for_proofreading(
    paragraphs_json: str,
    config: ProofreadingConfig,
    checks: list[str],
) -> list[dict[str, Any]]:
    """
    Send a batch of paragraphs to the LLM and parse corrections.
    """
    straico_key = os.environ.get("STRAICO_API_KEY")
    max_retries = config.llm_max_retries
    delay = config.llm_retry_initial_delay_seconds
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if straico_key:
                return await _call_straico_v0(paragraphs_json, straico_key, config, checks)
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
                delay *= 2
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
        model=config.llm_model or "anthropic/claude-sonnet-4.5",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens_per_call,
    )
    content = response.choices[0].message.content or "[]"
    return _parse_json_content(content)

async def _call_straico_v0(
    paragraphs_json: str,
    api_key: str,
    config: ProofreadingConfig,
    checks: list[str],
) -> list[dict[str, Any]]:
    """Straico API call using v.0 prompt completion."""
    url = "https://api.straico.com/v0/prompt/completion"
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

    # v.0 Payload construction
    payload = {
        "message": full_prompt,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens_per_call,
    }

    # Decide between smart_llm_selector and specific model
    if config.smart_llm_selector:
        payload["smart_llm_selector"] = config.smart_llm_selector
    else:
        payload["model"] = config.llm_model or "anthropic/claude-sonnet-4.5"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=90.0)
        
        if response.status_code == 422:
            logger.error(f"Straico v.0 422 Error: {response.text}")
            
        response.raise_for_status()
        data = response.json()
        
        # v.0 Response structure: data.completion.choices[0].message.content
        try:
            content = data["data"]["completion"]["choices"][0]["message"]["content"]
            model_used = data["data"]["completion"].get("model", "unknown")
            logger.info(f"Straico used model: {model_used}")
            return _parse_json_content(content)
        except (KeyError, IndexError) as exc:
            logger.error(f"Failed to parse Straico v.0 response: {exc}. Data: {data}")
            return []

def _parse_json_content(content: str) -> list[dict[str, Any]]:
    """Helper to clean and parse JSON from LLM string with self-healing."""
    import re
    
    # 1. Basic cleaning
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```[a-z]*\n", "", content)
        content = re.sub(r"\n```$", "", content)
    content = content.strip()
    
    # 2. Extract array part
    if not (content.startswith("[") and content.endswith("]")):
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            content = match.group(0)
    
    # 3. Trailing commas
    content = re.sub(r",\s*([\]}])", r"\1", content)
    
    # First attempt: standard parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.info("Standard JSON parse failed, attempting repair...")
        pass

    # Second attempt: Targeted repair of unescaped quotes and newlines
    try:
        # This regex looks for values inside "key": "value" patterns
        # It specifically targets our known fields to avoid breaking the JSON structure
        fields = "original_text|suggested_text|explanation|category|confidence"
        
        def repair_value(match):
            prefix = match.group(1) # "field": "
            value = match.group(3)  # the actual value content
            suffix = match.group(4) # "
            # Escape unescaped double quotes
            # But don't double-escape already escaped ones
            value = re.sub(r'(?<!\\)"', r'\"', value)
            # Replace real newlines with \n
            value = value.replace("\n", "\\n").replace("\r", "")
            return f'{prefix}{value}{suffix}'

        # Pattern: "field" : " (value) " followed by , or }
        pattern = rf'("({fields})"\s*:\s*")(.*?)("(?=\s*[,}}]))'
        fixed_content = re.sub(pattern, repair_value, content, flags=re.DOTALL)
        
        return json.loads(fixed_content)
    except Exception as exc:
        logger.warning(f"JSON repair failed: {exc}\nPartial content: {content[:200]}...")
        return []
