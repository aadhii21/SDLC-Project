"""Shared Gemini model factory for every OpenAI-Agents-SDK `Agent` in this
project. Uses Google's official OpenAI-SDK-compatible endpoint for Gemini
(https://ai.google.dev/gemini-api/docs/openai) -- keeping this factory in
one file means switching providers again later means changing one small
file, not every agent definition.

Known limitations:
- Google's own docs describe this compatibility layer as "still in beta
  while we extend feature support" -- treat it as a request-shape
  convenience, not full feature parity.
- Like the Anthropic endpoint, this is a Chat Completions-compatible shim,
  not Gemini's native API -- it does not support OpenAI's hosted
  Responses-API tools (e.g. `WebSearchTool`).
- The free tier no longer includes any Pro-tier model (removed April
  2026) and has tight per-minute limits on Flash-tier models -- a burst of
  concurrent calls (e.g. search_planer_agent's 5 parallel web searches)
  can exceed it well before the pipeline finishes one request. Check
  https://aistudio.google.com/rate-limit for this account's actual current
  numbers -- they're account-specific and Google revises them without notice.
"""
from openai import AsyncOpenAI

from agents import OpenAIChatCompletionsModel
from config.settings import settings

# gemini-2.5-flash / gemini-2.5-flash-lite are deprecated for new API keys
# (confirmed live: 404 "no longer available to new users"). Google's error
# message recommended gemini-3.6-flash / gemini-3.5-flash-lite as
# replacements -- confirmed both reliable (3/3 live test calls). The
# newest gemini-3.8-flash was NOT used despite being available: it burns
# heavy hidden reasoning tokens even for trivial output (~104 tokens to
# say "OK") and returned intermittent 503 "high demand" errors in testing
# (2/3 success rate) -- real capacity instability, not a fluke.
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
LIGHT_GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        # Placeholder key keeps import-time construction safe even before
        # GEMINI_API_KEY is configured -- Agent(model=get_gemini_model())
        # evaluates at module import time.
        _client = AsyncOpenAI(api_key=settings.gemini_api_key or "not-configured", base_url=GEMINI_BASE_URL)
    return _client


def get_gemini_model(model_name: str = DEFAULT_GEMINI_MODEL) -> OpenAIChatCompletionsModel:
    return OpenAIChatCompletionsModel(model=model_name, openai_client=_get_client())
