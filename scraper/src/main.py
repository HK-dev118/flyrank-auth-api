from pathlib import Path

import requests


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/HK-dev118/flyrank-auth-api)"
)

TIMEOUT = 10


def fetch_and_cache(url: str, cache_file: Path) -> str:
    """Fetch a page once and reuse the cached copy during development."""

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(
            f"CACHE HIT | status=200 "
            f"| bytes={len(html.encode('utf-8'))}"
        )
        return html

    cache_file.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": USER_AGENT,
    }

    print(f"FETCH | url={url}")

    response = requests.get(
        url,
        headers=headers,
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch {url}: HTTP {response.status_code}"
        )

    html = response.text
    cache_file.write_text(html, encoding="utf-8")

    print(
        f"FETCHED | status={response.status_code} "
        f"| bytes={len(html.encode('utf-8'))}"
    )

    return html


def main() -> None:
    fetch_and_cache(BASE_URL, CACHE_FILE)


if __name__ == "__main__":
    main()