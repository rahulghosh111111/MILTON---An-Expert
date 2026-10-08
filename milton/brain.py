"""Wraps the Claude call that implements the system prompt's reasoning
pipeline: given transcript + screen_context + memory, returns the parsed
output JSON object (spoken_reply / actions / clarification_needed / status /
memory_update / notes).
"""

import json
import re
from datetime import datetime, timezone

from anthropic import Anthropic

from . import config

_client = None
_system_prompt = None


def _get_client():
    global _client
    if _client is None:
        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def get_system_prompt():
    global _system_prompt
    if _system_prompt is None:
        with open(config.SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            _system_prompt = f.read()
    return _system_prompt


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def get_response(transcript: str, screen_context: dict, memory_state: dict) -> dict:
    turn_input = {
        "transcript": transcript,
        "screen_context": screen_context,
        "memory": memory_state,
    }

    message = _get_client().messages.create(
        model=config.MODEL_NAME,
        max_tokens=1024,
        system=get_system_prompt(),
        messages=[{"role": "user", "content": json.dumps(turn_input, ensure_ascii=False)}],
    )

    raw_text = "".join(
        block.text for block in message.content if getattr(block, "type", None) == "text"
    )

    return _extract_json(raw_text)


def now_iso():
    return datetime.now(timezone.utc).isoformat()
