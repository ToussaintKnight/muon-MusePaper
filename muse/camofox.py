"""Camofox Browser REST API client.

Thin wrapper around ``http://localhost:9377`` — create tab, navigate,
get snapshot, close tab.  Mirrors the CLI from ``camofox.sh``.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Proxy-aware session — bypass SOCKS5 for localhost
# ---------------------------------------------------------------------------
_NO_PROXY = {"http": "", "https": ""}  # empty proxy = direct connect


def _session() -> requests.Session:
    """Create a session that bypasses ALL_PROXY for localhost connections."""
    s = requests.Session()
    # Force direct connection (bypass SOCKS5 proxy for localhost Camofox)
    s.trust_env = False  # ignore HTTP_PROXY/ALL_PROXY env vars
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

_DEFAULT_API = "http://localhost:9377"
_DEFAULT_USER = "pixie-muon"
_NAVIGATION_WAIT = 3  # seconds after navigate before snapshot
_MAX_SNAPSHOT_CHARS = 80_000


class CamofoxTab:
    """A managed Camofox browser tab with automatic cleanup."""

    def __init__(self, tab_id: str, api_url: str, user_id: str):
        self.tab_id = tab_id
        self._api = api_url
        self._user = user_id
        self._closed = False

    def navigate(self, url: str, wait: float = _NAVIGATION_WAIT) -> None:
        """Navigate to a URL and wait for page load."""
        if self._closed:
            raise RuntimeError(f"Tab {self.tab_id} is closed")
        resp = _session().post(
            f"{self._api}/tabs/{self.tab_id}/navigate",
            json={"userId": self._user, "url": url},
            timeout=15,
        )
        resp.raise_for_status()
        time.sleep(wait)

    def snapshot(self) -> str:
        """Get accessibility tree snapshot as text."""
        if self._closed:
            raise RuntimeError(f"Tab {self.tab_id} is closed")
        resp = _session().get(
            f"{self._api}/tabs/{self.tab_id}/snapshot",
            params={"userId": self._user},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("snapshot") or "")[:_MAX_SNAPSHOT_CHARS]

    def links(self, limit: int = 50) -> list[dict]:
        """Get page links."""
        if self._closed:
            raise RuntimeError(f"Tab {self.tab_id} is closed")
        resp = _session().get(
            f"{self._api}/tabs/{self.tab_id}/links",
            params={"userId": self._user, "limit": limit},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("links", [])

    def close(self) -> None:
        if self._closed:
            return
        try:
            _session().delete(
                f"{self._api}/tabs/{self.tab_id}",
                params={"userId": self._user},
                timeout=5,
            )
        except Exception:
            pass
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class CamofoxClient:
    """Camofox browser REST client."""

    def __init__(self, api_url: str = _DEFAULT_API, user_id: str = _DEFAULT_USER):
        self.api = api_url.rstrip("/")
        self.user = user_id
        self._session = _session()

    def health(self) -> dict:
        resp = self._session.get(f"{self.api}/health", timeout=5)
        resp.raise_for_status()
        return resp.json()

    def new_tab(self, url: str, session_key: str = "muse") -> CamofoxTab:
        """Create a new browser tab and navigate to *url*."""
        resp = self._session.post(
            f"{self.api}/tabs",
            json={"userId": self.user, "sessionKey": session_key, "url": url},
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to create tab: {resp.status_code} {resp.text[:200]}"
            )
        data = resp.json()
        tab_id = data.get("tabId")
        if not tab_id:
            raise RuntimeError(f"Create tab response missing tabId: {data}")
        return CamofoxTab(tab_id, self.api, self.user)

    def crawl_page(self, url: str, wait: float = _NAVIGATION_WAIT) -> CamofoxTab:
        """Open *url* in a new tab, wait for load, return the tab (caller must close)."""
        tab = self.new_tab(url)
        tab.navigate(url, wait=wait)
        return tab


# Global singleton (same pattern as TrendRadar's myFetch)
_client: Optional[CamofoxClient] = None


def get_client() -> CamofoxClient:
    global _client
    if _client is None:
        _client = CamofoxClient()
    return _client


def check_available() -> bool:
    """Probe Camofox server health."""
    try:
        return get_client().health().get("ok", False)
    except Exception:
        return False
