"""Unit tests for the Browserless Web Extract Provider."""

from unittest.mock import MagicMock, patch

import pytest
from hermes_browserless_web_extract.provider import BrowserlessWebExtractProvider


def test_is_available_without_vars(monkeypatch):
    monkeypatch.delenv("BROWSERLESS_TOKEN", raising=False)
    monkeypatch.delenv("BROWSERLESS_URL", raising=False)
    provider = BrowserlessWebExtractProvider()
    assert not provider.is_available()


def test_is_available_missing_url(monkeypatch):
    monkeypatch.setenv("BROWSERLESS_TOKEN", "test-token")
    monkeypatch.delenv("BROWSERLESS_URL", raising=False)
    provider = BrowserlessWebExtractProvider()
    assert not provider.is_available()


def test_is_available_missing_token(monkeypatch):
    monkeypatch.delenv("BROWSERLESS_TOKEN", raising=False)
    monkeypatch.setenv("BROWSERLESS_URL", "https://example.com")
    provider = BrowserlessWebExtractProvider()
    assert not provider.is_available()


def test_is_available_with_both(monkeypatch):
    monkeypatch.setenv("BROWSERLESS_TOKEN", "test-token")
    monkeypatch.setenv("BROWSERLESS_URL", "https://example.com")
    provider = BrowserlessWebExtractProvider()
    assert provider.is_available()


def test_supports_capabilities():
    provider = BrowserlessWebExtractProvider()
    assert not provider.supports_search()
    assert provider.supports_extract()


def test_extract_missing_token(monkeypatch):
    monkeypatch.delenv("BROWSERLESS_TOKEN", raising=False)
    monkeypatch.setenv("BROWSERLESS_URL", "https://example.com")
    provider = BrowserlessWebExtractProvider()
    results = provider.extract(["https://example.com"])
    assert len(results) == 1
    assert "BROWSERLESS_TOKEN" in results[0]["error"]


def test_extract_success(monkeypatch):
    monkeypatch.setenv("BROWSERLESS_TOKEN", "test-token")
    monkeypatch.setenv("BROWSERLESS_URL", "https://browserless.example.com")
    provider = BrowserlessWebExtractProvider()

    mock_response = MagicMock()
    mock_response.text = "<html><body>Hello World</body></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        results = provider.extract(["https://example.com/test"])

        assert len(results) == 1
        res = results[0]
        assert res["url"] == "https://example.com/test"
        assert res["content"] == "<html><body>Hello World</body></html>"
        assert res["raw_content"] == "<html><body>Hello World</body></html>"
        assert "error" not in res


def test_extract_multiple_urls(monkeypatch):
    monkeypatch.setenv("BROWSERLESS_TOKEN", "test-token")
    monkeypatch.setenv("BROWSERLESS_URL", "https://browserless.example.com")
    provider = BrowserlessWebExtractProvider()

    mock_response = MagicMock()
    mock_response.text = "<html><body>Page content</body></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        results = provider.extract(["https://example.com/1", "https://example.com/2"])

        assert len(results) == 2
        assert results[0]["url"] == "https://example.com/1"
        assert results[1]["url"] == "https://example.com/2"
        assert results[0]["content"] == "<html><body>Page content</body></html>"


def test_extract_http_error(monkeypatch):
    monkeypatch.setenv("BROWSERLESS_TOKEN", "test-token")
    monkeypatch.setenv("BROWSERLESS_URL", "https://browserless.example.com")
    provider = BrowserlessWebExtractProvider()

    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    exc = httpx.HTTPStatusError(
        "Unauthorized", request=MagicMock(), response=mock_response
    )

    with patch("httpx.post", side_effect=exc):
        results = provider.extract(["https://example.com"])
        assert len(results) == 1
        assert "error" in results[0]
        assert "401" in results[0]["error"]
