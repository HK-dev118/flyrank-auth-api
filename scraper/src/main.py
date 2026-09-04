from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

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


def discover_catalogue_pages() -> list[tuple[str, str]]:
    """Discover and cache the first three catalogue pages."""

    pages = []
    current_url = BASE_URL

    for page_number in range(1, 4):
        cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

        html = fetch_and_cache(current_url, cache_file)
        pages.append((current_url, html))

        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.select_one("li.next a")

        if not next_link:
            break

        current_url = urljoin(current_url, next_link["href"])

    return pages


def main() -> None:
    pages = discover_catalogue_pages()

    all_book_urls = []

    for page_url, html in pages:
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_url = urljoin(page_url, link["href"])
            all_book_urls.append(book_url)

    unique_urls = list(dict.fromkeys(all_book_urls))

    print(f"catalogue_pages={len(pages)}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")


if __name__ == "__main__":
    main()