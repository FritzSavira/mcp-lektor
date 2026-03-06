"""Async wrapper for LLM calls via the Langdock (OpenAI-compatible) API."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI

from mcp_lektor.core.models import ProofreadingConfig

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Du bist ein professioneller deutscher Lektor. Pr\u00fcfe den folgenden Text auf \
Fehler und gib Korrekturen als JSON-Array zur\u00fcck.

Regeln:
- Ignoriere Platzhalter-Text (rot markiert, in eckigen Klammern).
- Verwende deutsche typografische Konventionen.
- Gib NUR echte Fehler zur\u00fcck, keine stilistischen Vorschl\u00e4ge.
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
    "explanation": "<kurze Erkl\u00e4rung>"
  }
]

Wenn keine Fehler vorhanden sind, antworte mit einem leeren Array: []
"""


async def call_llm_for_proofreading(
    paragraphs_json: str,
    config: ProofreadingConfig,
    checks: list[str],
) -> list[dict[str, Any]]:
    """Send a batch of paragraphs to the LLM and parse corrections.

    Returns a list of raw correction dicts (not yet validated as Pydantic models).
    """
    client = AsyncOpenAI(
        api_key=config.langdock_api_key or os.environ.get("LANGDOCK_API_KEY", ""),
        base_url=config.langdock_api_base,
    )

    checks_hint = ", ".join(checks)
    user_message = (
        f"Pr\u00fcfe den folgenden Text auf: {checks_hint}.\n\n"
        f"Abs\u00e4tze (JSON):\n{paragraphs_json}"
    )

    try:
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
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        return json.loads(content)
    except (json.JSONDecodeError, IndexError, KeyError) as exc:
        logger.warning("LLM returned unparseable response: %s", exc)
        return []
    except Exception as exc:  # noqa: BLE001
        logger.error("LLM API call failed: %s", exc)
        return []
