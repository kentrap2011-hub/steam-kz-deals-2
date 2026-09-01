from __future__ import annotations

import html as html_lib
import re
import time
from typing import Any

import requests

from giveaway_core import SourceError

HTTP_TIMEOUT_SECONDS = 25
HTTP_ATTEMPTS = 3
USER_AGENT = "steam-kz-deals-giveaway-worker/1.0 (+https://github.com/kentrap2011-hub/steam-kz-deals-2)"

def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,text/html;q=0.9,*/*;q=0.8"})
    return session

def get_json(session: requests.Session, url: str, params: dict[str, Any] | None = None) -> Any:
    last: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        try:
            response = session.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(attempt)
    raise SourceError(f"GET JSON failed after {HTTP_ATTEMPTS} attempts: {url}: {last}")

def get_text(session: requests.Session, url: str, params: dict[str, Any] | None = None) -> str:
    last: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        try:
            response = session.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(attempt)
    raise SourceError(f"GET text failed after {HTTP_ATTEMPTS} attempts: {url}: {last}")

def html_to_text(raw_html: str) -> str:
    text = re.sub(r"(?is)<script\b[^>]*>.*?</script>", " ", raw_html or " ")
    text = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return " ".join(html_lib.unescape(text).split())
