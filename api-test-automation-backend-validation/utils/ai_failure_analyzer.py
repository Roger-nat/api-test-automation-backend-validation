from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from app.config import LLM_API_KEY, LLM_API_URL, LLM_MODEL, LLM_TIMEOUT_SECONDS, ROOT_DIR
from utils.logger import get_logger

LOGGER = get_logger(__name__)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if key.lower() in {"password", "token", "access_token", "authorization"}:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def build_safe_context(test_name: str, exchange, traceback_text: str) -> str:
    payload = {
        "test_name": test_name,
        "method": exchange.method if exchange else None,
        "endpoint": exchange.url if exchange else None,
        "request": _redact(exchange.request_body if exchange else None),
        "status_code": exchange.status_code if exchange else None,
        "response": _redact(exchange.response_body if exchange else None),
        "traceback": traceback_text,
    }
    return json.dumps(payload, indent=2, default=str)


def analyze_failure(test_name: str, exchange, traceback_text: str) -> Path:
    out_dir = ROOT_DIR / "artifacts" / "failure_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{test_name.replace('::', '__').replace('/', '_')}.md"

    context = build_safe_context(test_name, exchange, traceback_text)

    if not (LLM_API_URL and LLM_API_KEY and LLM_MODEL):
        output.write_text(
            "# AI Failure Analysis\n\n"
            "AI analysis was skipped because LLM_API_URL, LLM_API_KEY or "
            "LLM_MODEL is not configured.\n\n"
            "The failure context was still captured locally with secrets redacted.\n",
            encoding="utf-8",
        )
        return output

    prompt = f"""
You are a QA test failure analyst.

Analyze the following sanitized API test failure.

{context}

Return only these three sections:

## Failure Summary
Explain what failed in simple technical language.

## Likely Cause
Give the most likely cause using only evidence present in the failure context. If evidence is insufficient, say so.

## Suggested Next Step
Give one or two practical debugging steps.
""".strip()

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You analyze software test failures conservatively and do not invent evidence.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    try:
        response = requests.post(
            LLM_API_URL,
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        output.write_text(
            "# AI Failure Analysis\n\n" + content.strip() + "\n",
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("AI analysis failed: %s", exc)
        output.write_text(
            "# AI Failure Analysis\n\n"
            f"AI analysis request failed: {exc}\n",
            encoding="utf-8",
        )

    return output
