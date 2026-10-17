"""
Groq AI provider for floor-plan generation.

Uses the official Groq Python SDK with JSON mode to produce structured
floor-plan layouts matching the shared LayoutData Pydantic schema.

Never logs API keys, JWTs, prompts, or user data.
"""

from groq import Groq
from pydantic import ValidationError
from typing import Dict, Any
from app.core.config import settings
from app.models.layout import LayoutData
from app.models.provider_schema import GeminiLayoutData
from app.services.ai.base import AIPlanningProvider
import json
import time
import random
import re
import logging

logger = logging.getLogger("ai.groq_provider")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def _extract_json_from_text(raw: str) -> str:
    """Extract JSON from raw text that may contain markdown fences."""
    text = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    return text[start : end + 1]


# -------------------------------------------------------------------- #
#  Error classification helpers
# -------------------------------------------------------------------- #

_TRANSIENT_INDICATORS = [
    "503", "unavailable", "429", "rate_limit", "rate limit",
    "resource_exhausted", "timeout", "timed out", "deadline",
    "connection", "server_error", "internal_error",
]


def _is_transient(err_msg: str) -> bool:
    lowered = err_msg.lower()
    return any(ind in lowered for ind in _TRANSIENT_INDICATORS)


class GroqProvider(AIPlanningProvider):
    """Floor-plan generator backed by the Groq API."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.GROQ_MODEL
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            timeout=60.0,          # 60-second HTTP timeout (seconds for httpx)
            max_retries=0,         # We handle retries ourselves
        )
        logger.info(
            "GroqProvider init  |  model=%s  api_key_present=%s",
            self.model_name,
            bool(settings.GROQ_API_KEY),
        )

    # ------------------------------------------------------------------ #
    #  Core generation
    # ------------------------------------------------------------------ #
    def generate_layout(
        self, context: Dict[str, Any], feedback: str = None
    ) -> LayoutData:
        from app.services.ai.prompt_builder import build_prompt

        prompt = build_prompt(context, feedback)

        if not prompt or not prompt.strip():
            logger.error("Prompt is empty — aborting Groq call")
            raise RuntimeError("PROVIDER_BAD_REQUEST: empty prompt")

        logger.info(
            "Prompt ready  |  type=%s  length=%d chars",
            type(prompt).__name__,
            len(prompt),
        )

        # Build the JSON schema to inject into the prompt
        schema_dict = GeminiLayoutData.model_json_schema()
        schema_text = json.dumps(schema_dict, indent=2)

        # Construct system message with the full schema
        system_msg = (
            "You are an expert AI Architectural Planner that generates "
            "floor-plan layouts as structured JSON.\n\n"
            "You MUST return ONLY a raw JSON object (no markdown fences, "
            "no explanation, no extra text).\n\n"
            "The JSON MUST exactly match the following JSON Schema:\n"
            f"{schema_text}"
        )

        max_attempts = 3
        last_error = None

        for attempt in range(max_attempts):
            attempt_num = attempt + 1
            logger.info(
                ">>> Groq call  |  model '%s'  attempt %d/%d",
                self.model_name,
                attempt_num,
                max_attempts,
            )

            try:
                t0 = time.time()
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_tokens=8192,
                    response_format={"type": "json_object"},
                )
                elapsed = time.time() - t0

                # ---- Post-call diagnostics ----
                choice = response.choices[0] if response.choices else None
                finish_reason = choice.finish_reason if choice else None
                raw_text = choice.message.content if choice else None
                usage = response.usage

                logger.info(
                    "<<< Groq response  |  attempt %d  elapsed=%.2fs  "
                    "finish_reason=%s  has_text=%s  "
                    "tokens_in=%s  tokens_out=%s",
                    attempt_num,
                    elapsed,
                    finish_reason,
                    bool(raw_text),
                    usage.prompt_tokens if usage else "?",
                    usage.completion_tokens if usage else "?",
                )

                if not raw_text or not raw_text.strip():
                    raise ValueError(
                        f"Groq returned empty text. finish_reason={finish_reason}"
                    )

                # Parse JSON — extract from fences if the model wraps it
                json_str = _extract_json_from_text(raw_text)
                parsed_json = json.loads(json_str)

                # Validate with Pydantic
                layout_data = LayoutData(**parsed_json)

                total_rooms = sum(len(f.rooms) for f in layout_data.floors)
                logger.info(
                    "<<< Groq SUCCESS  |  attempt %d  rooms=%d  elapsed=%.2fs",
                    attempt_num,
                    total_rooms,
                    elapsed,
                )
                return layout_data

            except Exception as e:
                last_error = e
                err_msg = str(e)
                err_cls = type(e).__name__
                logger.warning(
                    "Groq error  |  attempt %d  |  %s: %s",
                    attempt_num,
                    err_cls,
                    err_msg,
                )

                # ---- Non-transient errors: raise immediately ----
                if "api key" in err_msg.lower() or "api_key" in err_msg.lower():
                    raise RuntimeError(f"PROVIDER_AUTH_ERROR: {e}")

                if isinstance(e, (ValidationError, json.JSONDecodeError)):
                    # Schema / parsing error — retrying with feedback might help
                    if attempt < max_attempts - 1:
                        # Use the validation error as feedback
                        prompt = build_prompt(context, str(e))
                        delay = 1.0 + random.uniform(0.1, 0.5)
                        logger.info("Validation error — retrying in %.2fs with feedback", delay)
                        time.sleep(delay)
                        continue
                    raise ValueError(
                        f"Pydantic/JSON validation failed on AI output: {e}"
                    )

                # ---- Transient errors: retry ----
                if _is_transient(err_msg):
                    if attempt < max_attempts - 1:
                        delay = 2.0 if attempt == 0 else 5.0
                        delay += random.uniform(0.1, 0.5)
                        logger.info("Transient error — retrying in %.2fs", delay)
                        time.sleep(delay)
                        continue
                    else:
                        raise RuntimeError(
                            "AI service is temporarily busy. "
                            "Please try again shortly."
                        )

                # Unknown error — propagate
                raise ValueError(f"Provider error: {e}")

        # Should not reach here
        raise RuntimeError(
            "AI service is temporarily busy. Please try again shortly."
        )
