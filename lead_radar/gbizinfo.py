"""Minimal client for the gBizINFO REST API v2 (standard library only).

Spec: https://api.info.gbiz.go.jp/hojin/v3/api-docs/v2 (see docs/data-source-notes.md).
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.info.gbiz.go.jp/hojin/v2/hojin"
RECORD_URL = "https://info.gbiz.go.jp/hojin/ichiran?hojinBango={corporate_number}"
TOKEN_HEADER = "X-hojinInfo-api-token"


class GBizInfoError(Exception):
    pass


class GBizInfoClient:
    def __init__(self, token: str, min_interval_sec: float = 0.5):
        if not token:
            raise GBizInfoError("gBizINFO token is missing.")
        self._token = token
        self._min_interval = min_interval_sec
        self._last_call = 0.0

    def _get(self, path: str, params: dict | None = None) -> dict:
        # Polite throttling: the API terms forbid excessive access.
        wait = self._min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        url = BASE_URL + path  # no trailing slash: the API returns 500 for one
        if params:
            url += "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            url, headers={TOKEN_HEADER: self._token, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return {}
            # Never include the token in error messages.
            raise GBizInfoError(f"gBizINFO returned HTTP {err.code} for {path}") from None
        finally:
            self._last_call = time.monotonic()
        return json.loads(body)

    def search(self, **params) -> list[dict]:
        return self._get("", params).get("hojin-infos") or []

    def basic_info(self, corporate_number: str) -> dict | None:
        infos = self._get(f"/{corporate_number}", {"metadata_flg": "true"}).get("hojin-infos") or []
        return infos[0] if infos else None

    def category(self, corporate_number: str, name: str) -> list[dict]:
        """Return the records of one category (e.g. "subsidy", "certification")."""
        infos = self._get(f"/{corporate_number}/{name}", {"metadata_flg": "true"}).get("hojin-infos") or []
        return (infos[0].get(name) or []) if infos else []
