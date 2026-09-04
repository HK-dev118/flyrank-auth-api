import time
from dataclasses import dataclass
from typing import Optional

import requests


MAX_RETRIES = 3
RETRY_DELAY = 1.0


@dataclass
class FetchResult:
    url: str
    html: Optional[str]
    status_code: Optional[int]
    attempts: int
    error: Optional[str]


def fetch_with_retry(
    url: str,
    headers: dict,
    timeout: int = 10,
) -> FetchResult:
    """
    Fetch a URL with bounded retries.

    Retries are used for transient request failures and
    server-side HTTP errors.
    """

    last_error = None
    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
            )

            last_status = response.status_code

            if response.status_code == 200:
                return FetchResult(
                    url=url,
                    html=response.text,
                    status_code=response.status_code,
                    attempts=attempt,
                    error=None,
                )

            if response.status_code in {429, 500, 502, 503, 504}:
                last_error = (
                    f"HTTP {response.status_code}"
                )

            else:
                return FetchResult(
                    url=url,
                    html=None,
                    status_code=response.status_code,
                    attempts=attempt,
                    error=f"HTTP {response.status_code}",
                )

        except requests.RequestException as exc:
            last_error = str(exc)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    return FetchResult(
        url=url,
        html=None,
        status_code=last_status,
        attempts=MAX_RETRIES,
        error=last_error or "Unknown fetch error",
    )