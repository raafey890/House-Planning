"""
Provider factory — selects and falls back between AI providers.

Reads AI_PRIMARY_PROVIDER and AI_FALLBACK_PROVIDER from settings.
Only provider-level failures (timeout, 5xx, rate-limit) trigger
cross-provider fallback.  Schema/validation/auth errors are raised
immediately.

Never logs API keys, JWTs, prompts, or user data.
"""

from typing import Dict, Any
from app.core.config import settings
from app.models.layout import LayoutData
from app.services.ai.base import AIPlanningProvider
import logging

logger = logging.getLogger("ai.provider_factory")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def _create_provider(name: str) -> AIPlanningProvider:
    """Instantiate a provider by its config name.  Returns None if the
    provider cannot be created (e.g. missing API key)."""
    name = name.strip().lower()

    if name == "groq":
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — cannot create GroqProvider")
            return None
        from app.services.ai.groq_provider import GroqProvider
        return GroqProvider()

    if name == "gemini":
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — cannot create GeminiProvider")
            return None
        from app.services.ai.gemini_provider import GeminiProvider
        return GeminiProvider()

    if name == "openai":
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set — cannot create OpenAI provider")
            return None
        # Future: from app.services.ai.openai_provider import OpenAIProvider
        logger.warning("OpenAI provider not yet implemented")
        return None

    logger.error("Unknown AI provider name: %s", name)
    return None


def get_provider_chain() -> list[tuple[str, AIPlanningProvider]]:
    """Return an ordered list of (name, provider) pairs to try."""
    chain = []

    primary_name = settings.AI_PRIMARY_PROVIDER
    fallback_name = settings.AI_FALLBACK_PROVIDER

    primary = _create_provider(primary_name)
    if primary:
        chain.append((primary_name, primary))
    else:
        logger.warning(
            "Primary provider '%s' could not be created", primary_name
        )

    if fallback_name and fallback_name != primary_name:
        fallback = _create_provider(fallback_name)
        if fallback:
            chain.append((fallback_name, fallback))
        else:
            logger.warning(
                "Fallback provider '%s' could not be created", fallback_name
            )

    if not chain:
        raise RuntimeError(
            "CONFIGURATION_ERROR: No AI providers could be initialized. "
            "Check API key configuration."
        )

    logger.info(
        "Provider chain: %s",
        " → ".join(name for name, _ in chain),
    )
    return chain


def generate_with_fallback(
    context: Dict[str, Any], feedback: str = None
) -> tuple[LayoutData, str]:
    """Try each provider in the chain.  Returns (layout_data, provider_name).

    Only RuntimeError with 'temporarily busy' or transient indicators
    triggers fallback to the next provider.  All other errors propagate
    immediately (schema, validation, auth, bad request).
    """
    chain = get_provider_chain()
    last_error = None

    for idx, (provider_name, provider) in enumerate(chain):
        is_last = idx == len(chain) - 1
        logger.info(
            "=== Trying provider '%s' (%d/%d) ===",
            provider_name,
            idx + 1,
            len(chain),
        )

        try:
            layout = provider.generate_layout(context, feedback)
            logger.info("Provider '%s' succeeded", provider_name)
            return layout, provider_name

        except RuntimeError as e:
            err_msg = str(e).lower()
            last_error = e

            # These are provider-level transient errors → fallback
            is_provider_failure = any(
                ind in err_msg
                for ind in [
                    "temporarily busy",
                    "timeout",
                    "timed out",
                    "deadline",
                    "unavailable",
                    "503",
                    "429",
                    "rate_limit",
                    "rate limit",
                    "connection",
                ]
            )

            if is_provider_failure and not is_last:
                logger.warning(
                    "Provider '%s' failed with transient error — falling back. Error: %s",
                    provider_name,
                    type(e).__name__,
                )
                continue

            # Non-transient RuntimeError or last provider — propagate
            raise

        except ValueError as e:
            # Schema / validation / parsing errors — do NOT fallback
            logger.error(
                "Provider '%s' returned invalid data: %s",
                provider_name,
                type(e).__name__,
            )
            raise

        except Exception as e:
            last_error = e
            if not is_last:
                logger.warning(
                    "Provider '%s' unexpected error — falling back. %s: %s",
                    provider_name,
                    type(e).__name__,
                    e,
                )
                continue
            raise

    # Should not reach here
    raise RuntimeError(
        "AI service is temporarily busy. Please try again shortly."
    )
