from google import genai
from google.genai import types
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

# Module-level logger. Never logs secrets, prompts, or user data.
logger = logging.getLogger("ai.gemini_provider")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def strip_unsupported_keys(schema_node):
    """Remove JSON Schema keys that the Gemini API does not accept."""
    if isinstance(schema_node, dict):
        for key in ["title", "default", "additionalProperties"]:
            schema_node.pop(key, None)
        if "anyOf" in schema_node:
            types_found = []
            for sub in schema_node["anyOf"]:
                if "type" in sub and sub["type"] != "null":
                    types_found.append(sub["type"])
            if types_found:
                schema_node["type"] = types_found[0]
            del schema_node["anyOf"]
        for _k, v in schema_node.items():
            strip_unsupported_keys(v)
    elif isinstance(schema_node, list):
        for item in schema_node:
            strip_unsupported_keys(item)
    return schema_node


def _extract_json_from_text(raw: str) -> str:
    """Extract JSON from raw text that may contain markdown fences or preamble."""
    text = raw.strip()
    # Remove ```json ... ``` fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    # Find the outermost { ... }
    start = text.find("{")
    if start == -1:
        return text  # let json.loads raise the error
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


class GeminiProvider(AIPlanningProvider):
    def __init__(self, model_name: str = "gemini-3.8-flash"):
        self.model_name = model_name
        self.fallback_model = "gemini-3.1-flash-lite"
        # Timeout in MILLISECONDS (google-genai SDK uses ms, not seconds).
        # 60000 ms = 60 seconds per request — enough for structured JSON generation.
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options={"timeout": 60000},
        )
        # Log SDK version once at init
        sdk_version = getattr(genai, "__version__", "unknown")
        logger.info(
            "GeminiProvider init  |  primary=%s  fallback=%s  sdk=%s  api_key_present=%s",
            self.model_name,
            self.fallback_model,
            sdk_version,
            bool(settings.GEMINI_API_KEY),
        )

    # ------------------------------------------------------------------ #
    #  Core generation
    # ------------------------------------------------------------------ #
    def generate_layout(
        self, context: Dict[str, Any], feedback: str = None
    ) -> LayoutData:
        from app.services.ai.prompt_builder import build_prompt

        prompt = build_prompt(context, feedback)

        # ---- Pre-call guards ----
        if not prompt or not prompt.strip():
            logger.error("Prompt is empty — aborting Gemini call")
            raise RuntimeError("PROVIDER_BAD_REQUEST: empty prompt")

        logger.info(
            "Prompt ready  |  type=%s  length=%d chars",
            type(prompt).__name__,
            len(prompt),
        )

        schema_dict = GeminiLayoutData.model_json_schema()
        clean_schema = strip_unsupported_keys(schema_dict)

        if not clean_schema:
            logger.error("Cleaned schema is empty — aborting")
            raise RuntimeError("PROVIDER_SCHEMA_ERROR: empty schema after cleaning")

        logger.debug("Clean schema top-level keys: %s", list(clean_schema.keys()))

        # ---- Build two configs ----
        # Mode A: Structured JSON output (preferred when API supports it)
        structured_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema,
            temperature=0.2,
        )
        # Mode B: Plain text fallback — prompt instructs the model to return
        #         raw JSON; we parse and validate ourselves.
        text_config = types.GenerateContentConfig(
            temperature=0.2,
        )

        models_to_try = [
            {"model": self.model_name, "max_attempts": 3, "label": "PRIMARY"},
            {"model": self.fallback_model, "max_attempts": 2, "label": "FALLBACK"},
        ]

        # Track whether structured-output 503s occur so we can switch mode
        structured_mode_unavailable = False

        for stage, model_cfg in enumerate(models_to_try):
            current_model = model_cfg["model"]
            max_attempts = model_cfg["max_attempts"]
            label = model_cfg["label"]

            for attempt in range(max_attempts):
                attempt_num = attempt + 1

                # Decide which config to use
                if structured_mode_unavailable:
                    use_config = text_config
                    mode_label = "TEXT_FALLBACK"
                    # In text fallback mode, explicitly give the schema
                    prompt_to_use = prompt + "\n\nYOU MUST RETURN A JSON OBJECT EXACTLY MATCHING THIS SCHEMA:\n" + json.dumps(clean_schema, indent=2)
                else:
                    use_config = structured_config
                    mode_label = "STRUCTURED"
                    prompt_to_use = prompt

                logger.info(
                    ">>> Gemini call  |  %s model '%s'  attempt %d/%d  mode=%s",
                    label,
                    current_model,
                    attempt_num,
                    max_attempts,
                    mode_label,
                )

                try:
                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=prompt_to_use,
                        config=use_config,
                    )

                    # ---- Post-call diagnostics ----
                    self._log_response_diagnostics(response, label, attempt_num)

                    raw_text = response.text
                    if not raw_text or not raw_text.strip():
                        diag = self._build_empty_response_diagnostic(response)
                        logger.error("Empty response.text  |  %s", diag)
                        raise ValueError(
                            f"Gemini returned empty text. Diagnostic: {diag}"
                        )

                    # Parse JSON — in text-fallback mode we may need to
                    # extract JSON from markdown fences or preamble text.
                    if mode_label == "TEXT_FALLBACK":
                        json_str = _extract_json_from_text(raw_text)
                    else:
                        json_str = raw_text

                    parsed_json = json.loads(json_str)
                    layout_data = LayoutData(**parsed_json)
                    logger.info(
                        "<<< Gemini SUCCESS  |  %s '%s' attempt %d  mode=%s  rooms=%d",
                        label,
                        current_model,
                        attempt_num,
                        mode_label,
                        sum(len(f.rooms) for f in layout_data.floors),
                    )
                    return layout_data

                except Exception as e:
                    err_msg = str(e).lower()
                    err_cls = type(e).__name__
                    logger.warning(
                        "Gemini error  |  %s '%s' attempt %d  mode=%s  |  %s: %s",
                        label,
                        current_model,
                        attempt_num,
                        mode_label,
                        err_cls,
                        e,
                    )

                    # ---- Check if structured JSON mode is overloaded ----
                    is_structured_503 = (
                        mode_label == "STRUCTURED"
                        and ("503" in err_msg or "unavailable" in err_msg)
                    )

                    if is_structured_503 and not structured_mode_unavailable:
                        # Switch to text-fallback mode and retry THIS attempt
                        logger.info(
                            "Structured JSON mode returned 503 — switching to TEXT_FALLBACK mode"
                        )
                        structured_mode_unavailable = True
                        # Don't count this as a spent attempt — retry immediately
                        # with text mode (but do a brief pause to be polite)
                        time.sleep(1.0 + random.uniform(0.1, 0.5))
                        # We need to re-enter the loop for this attempt, so we
                        # break out of the inner except and use a flag.
                        # Simplest: just recurse by restarting the model loop.
                        # But to keep it clean, we'll re-call directly.
                        try:
                            logger.info(
                                ">>> Gemini RETRY  |  %s model '%s'  attempt %d/%d  mode=TEXT_FALLBACK",
                                label,
                                current_model,
                                attempt_num,
                                max_attempts,
                            )
                            # Explicitly give schema for fallback
                            prompt_to_use = prompt + "\n\nYOU MUST RETURN A JSON OBJECT EXACTLY MATCHING THIS SCHEMA:\n" + json.dumps(clean_schema, indent=2)
                            response = self.client.models.generate_content(
                                model=current_model,
                                contents=prompt_to_use,
                                config=text_config,
                            )
                            self._log_response_diagnostics(response, label, attempt_num)
                            raw_text = response.text
                            if not raw_text or not raw_text.strip():
                                diag = self._build_empty_response_diagnostic(response)
                                raise ValueError(
                                    f"Gemini returned empty text. Diagnostic: {diag}"
                                )
                            json_str = _extract_json_from_text(raw_text)
                            parsed_json = json.loads(json_str)
                            layout_data = LayoutData(**parsed_json)
                            logger.info(
                                "<<< Gemini SUCCESS  |  %s '%s' attempt %d  mode=TEXT_FALLBACK  rooms=%d",
                                label,
                                current_model,
                                attempt_num,
                                sum(len(f.rooms) for f in layout_data.floors),
                            )
                            return layout_data
                        except Exception as e2:
                            err_msg = str(e2).lower()
                            err_cls = type(e2).__name__
                            logger.warning(
                                "TEXT_FALLBACK also failed  |  %s: %s",
                                err_cls,
                                e2,
                            )
                            e = e2  # fall through to normal retry logic

                    # ---- Classify: transient vs fatal ----
                    is_transient = any(
                        indicator in err_msg
                        for indicator in [
                            "503",
                            "unavailable",
                            "429",
                            "resource_exhausted",
                            "timeout",
                            "timed out",
                            "deadline",
                        ]
                    )

                    if is_transient:
                        if attempt < max_attempts - 1:
                            delay = 2.0 if attempt == 0 else 5.0
                            retry_match = re.search(
                                r"retry.*?([\d.]+)\s*s", err_msg
                            )
                            if retry_match:
                                try:
                                    delay = float(retry_match.group(1))
                                except ValueError:
                                    pass
                            delay += random.uniform(0.1, 0.5)
                            logger.info(
                                "Transient error — retrying in %.2fs", delay
                            )
                            time.sleep(delay)
                            continue
                        else:
                            logger.warning(
                                "Exhausted %d attempts on %s model '%s'",
                                max_attempts,
                                label,
                                current_model,
                            )
                            if stage < len(models_to_try) - 1:
                                logger.info("Falling back to next model…")
                                break
                            else:
                                raise RuntimeError(
                                    "AI service is temporarily busy. "
                                    "Please try again shortly."
                                )

                    # ---- Non-transient: classify and raise immediately ----
                    if "api key" in err_msg or "api_key" in err_msg:
                        raise RuntimeError(f"PROVIDER_AUTH_ERROR: {e}")
                    if (
                        "additionalproperties" in err_msg
                        or "schema" in err_msg
                    ):
                        raise RuntimeError(f"PROVIDER_SCHEMA_ERROR: {e}")
                    if "400" in err_msg:
                        raise RuntimeError(f"PROVIDER_BAD_REQUEST: {e}")

                    if isinstance(e, (ValidationError, json.JSONDecodeError)):
                        raise ValueError(
                            f"Pydantic/JSON validation failed on AI output: {e}"
                        )

                    raise ValueError(f"Provider error: {e}")

        raise RuntimeError(
            "AI service is temporarily busy. Please try again shortly."
        )

    # ------------------------------------------------------------------ #
    #  Diagnostic helpers (never log secrets or user content)
    # ------------------------------------------------------------------ #
    def _log_response_diagnostics(self, response, label: str, attempt: int):
        """Log safe diagnostics from a Gemini response object."""
        try:
            candidates = getattr(response, "candidates", None)
            candidate_count = len(candidates) if candidates else 0
            finish_reason = None
            has_text = bool(response.text) if response.text else False
            parts_summary = []

            if candidates:
                first = candidates[0]
                finish_reason = getattr(first, "finish_reason", None)
                content = getattr(first, "content", None)
                if content:
                    parts = getattr(content, "parts", []) or []
                    for p in parts:
                        if getattr(p, "text", None):
                            parts_summary.append(
                                f"text({len(p.text)} chars)"
                            )
                        elif getattr(p, "function_call", None):
                            parts_summary.append("function_call(!)")
                        else:
                            parts_summary.append(type(p).__name__)

            prompt_feedback = getattr(response, "prompt_feedback", None)

            logger.info(
                "<<< Response diag  |  %s attempt %d  "
                "|  candidates=%d  finish_reason=%s  has_text=%s  "
                "parts=%s  prompt_feedback=%s",
                label,
                attempt,
                candidate_count,
                finish_reason,
                has_text,
                parts_summary or "none",
                prompt_feedback,
            )
        except Exception as diag_err:
            logger.debug("Could not log response diagnostics: %s", diag_err)

    def _build_empty_response_diagnostic(self, response) -> str:
        """Build a safe diagnostic string when response.text is empty."""
        parts = []
        try:
            candidates = getattr(response, "candidates", None)
            if not candidates:
                parts.append("no_candidates")
            else:
                first = candidates[0]
                fr = getattr(first, "finish_reason", None)
                parts.append(f"finish_reason={fr}")
                content = getattr(first, "content", None)
                if not content:
                    parts.append("no_content")
                else:
                    raw_parts = getattr(content, "parts", []) or []
                    if not raw_parts:
                        parts.append("no_parts")
                    for p in raw_parts:
                        if getattr(p, "function_call", None):
                            parts.append("has_function_call")
                        elif getattr(p, "text", None) is not None:
                            parts.append(f"text_len={len(p.text)}")
                        else:
                            parts.append(f"part_type={type(p).__name__}")

            pf = getattr(response, "prompt_feedback", None)
            if pf:
                block = getattr(pf, "block_reason", None)
                if block:
                    parts.append(f"blocked={block}")
        except Exception as err:
            parts.append(f"diag_error={err}")

        return "; ".join(parts) if parts else "unknown"
