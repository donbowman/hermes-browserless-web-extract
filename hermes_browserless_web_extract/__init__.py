"""Browserless web extract plugin for Hermes.

Uses Browserless.io's REST API to fetch fully-rendered HTML from real
headless browsers, including JavaScript-rendered content.

Activates when ``web.extract_backend: browserless`` or
``web.backend: browserless`` is set in ``config.yaml`` and both
``BROWSERLESS_TOKEN`` and ``BROWSERLESS_URL`` are configured.
"""

from __future__ import annotations

from hermes_browserless_web_extract.provider import BrowserlessWebExtractProvider


def register(ctx) -> None:
    """Register the Browserless provider with the Hermes plugin context."""
    ctx.register_web_search_provider(BrowserlessWebExtractProvider())
