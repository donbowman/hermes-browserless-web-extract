"""Browserless web content extraction provider.

Subclasses :class:`agent.web_search_provider.WebSearchProvider`. Uses the
Browserless.io REST API to fetch fully-rendered HTML via the ``/content``
endpoint.

Config keys this provider responds to::

    web:
      extract_backend: "browserless"  # explicit per-capability
      backend: "browserless"          # shared fallback
      browserless_url: "https://production-sfo.browserless.io"  # optional override
      browserless_timeout: 30000      # optional, ms (default 30000)

Env var::

    BROWSERLESS_TOKEN=...    # API token from browserless.io
    BROWSERLESS_URL=...      # Instance URL (defaults to production-sfo)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

DEFAULT_BROWSERLESS_URL = "https://production-sfo.browserless.io"


class BrowserlessWebExtractProvider(WebSearchProvider):
    """Browserless web extract provider using headless Chrome."""

    @property
    def name(self) -> str:
        return "browserless"

    @property
    def display_name(self) -> str:
        return "Browserless"

    def is_available(self) -> bool:
        return bool(
            os.getenv("BROWSERLESS_TOKEN", "").strip()
            and os.getenv("BROWSERLESS_URL", "").strip()
        )

    def supports_search(self) -> bool:
        return False

    def supports_extract(self) -> bool:
        return True

    def _get_config(self) -> Dict[str, Any]:
        from hermes_cli.config import load_config

        cfg = load_config().get("web", {})
        return {
            "url": os.getenv(
                "BROWSERLESS_URL", cfg.get("browserless_url", DEFAULT_BROWSERLESS_URL)
            ),
            "token": os.getenv("BROWSERLESS_TOKEN", ""),
            "timeout": cfg.get("browserless_timeout", 30000),
        }

    def _extract_url(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        import httpx

        browserless_url = config["url"].rstrip("/")
        token = config["token"]
        timeout = config["timeout"]

        api_url = f"{browserless_url}/content?token={token}"
        payload = {
            "url": url,
            "waitForTimeout": timeout,
            "bestAttempt": True,
            "rejectResourceTypes": ["image", "media", "font"],
            "rejectRequestPattern": [
                ".*\\.(png|jpg|jpeg|gif|webp|svg|ico|css|woff2?).*",
            ],
        }

        try:
            import httpx

            response = httpx.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=max(120, timeout / 1000 + 30),
            )
            response.raise_for_status()

            content = response.text
            if not content or not content.strip():
                return {
                    "url": url,
                    "title": url,
                    "content": "",
                    "error": "Browserless returned empty content",
                }

            return {
                "url": url,
                "title": url,
                "content": content,
                "raw_content": content,
                "metadata": {"sourceURL": url},
            }

        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500] if exc.response.text else str(exc)
            return {
                "url": url,
                "title": "",
                "content": "",
                "error": f"Browserless HTTP {exc.response.status_code}: {detail}",
            }
        except httpx.RequestError as exc:
            return {
                "url": url,
                "title": "",
                "content": "",
                "error": f"Browserless request failed: {exc}",
            }

    def extract(self, urls: List[str], **kwargs: Any) -> List[Dict[str, Any]]:
        try:
            from tools.interrupt import is_interrupted

            if is_interrupted():
                return [
                    {"url": u, "error": "Interrupted", "title": ""} for u in urls
                ]

            config = self._get_config()
            if not config["token"]:
                return [
                    {
                        "url": u,
                        "title": "",
                        "content": "",
                        "error": "BROWSERLESS_TOKEN environment variable not set. "
                        "Get your token at https://browserless.io/account/",
                    }
                    for u in urls
                ]

            results: List[Dict[str, Any]] = []
            for url in urls:
                logger.info("Browserless extract: %s", url)
                try:
                    result = self._extract_url(url, config)
                    results.append(result)
                except Exception as inner_exc:
                    results.append(
                        {
                            "url": url,
                            "title": "",
                            "content": "",
                            "error": str(inner_exc),
                        }
                    )

            return results

        except Exception as exc:  # noqa: BLE001
            logger.warning("Browserless extract error: %s", exc)
            return [
                {
                    "url": u,
                    "title": "",
                    "content": "",
                    "error": f"Browserless extract failed: {exc}",
                }
                for u in urls
            ]

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "Browserless",
            "badge": "API key required",
            "tag": (
                "Fetches fully-rendered HTML via headless Chrome. "
                "Supports JavaScript-rendered content. "
                "Requires BROWSERLESS_TOKEN and BROWSERLESS_URL."
            ),
            "env_vars": [
                {
                    "key": "BROWSERLESS_TOKEN",
                    "prompt": "Browserless API token",
                    "url": "https://browserless.io/account/",
                },
                {
                    "key": "BROWSERLESS_URL",
                    "prompt": "Browserless instance URL",
                    "url": "https://docs.browserless.io/rest-apis/intro",
                },
            ],
        }


if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO)
    provider = BrowserlessWebExtractProvider()

    urls = sys.argv[1:] if len(sys.argv) > 1 else ["https://example.com"]
    print(f"Extracting {urls}...")
    results = provider.extract(urls)
    for r in results:
        print(f"\n--- {r.get('url')} ---")
        if "error" in r:
            print(f"ERROR: {r['error']}")
        else:
            print(r["content"][:500])
