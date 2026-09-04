from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/HK-dev118/flyrank-auth-api)"
)

TIMEOUT = 10
REQUEST_DELAY = 0.5


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


def discover_book_urls(
    pages: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """Discover unique book URLs and their source catalogue pages."""

    discovered = []

    for page_url, html in pages:
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_url = urljoin(page_url, link["href"])
            discovered.append((book_url, page_url))

    unique = {}
    for book_url, source_page in discovered:
        if book_url not in unique:
            unique[book_url] = source_page

    return list(unique.items())


def extract_book_record(
    html: str,
    product_url: str,
    source_page: str,
) -> dict:
    """Extract the eight required raw fields from a book page."""

    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("article.product_page")

    if product is None:
        raise ValueError("Product area not found")

    title = product.select_one("h1")
    price = product.select_one(".price_color")
    availability = product.select_one(".availability")
    rating = product.select_one("p.star-rating")
    description = soup.select_one("#product_description + p")

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title.get_text(strip=True) if title else None,
        "product_url": product_url,
        "price_text": price.get_text(strip=True) if price else None,
        "availability_text": (
            availability.get_text(" ", strip=True)
            if availability
            else None
        ),
        "rating_text": (
            " ".join(rating.get("class", []))
            if rating
            else None
        ),
        "description": (
            description.get_text(" ", strip=True)
            if description
            else None
        ),
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def main() -> None:
    pages = discover_catalogue_pages()
    book_urls = discover_book_urls(pages)

    print(f"catalogue_pages={len(pages)}")
    print(f"discovered={len(book_urls)}")

    records = []

    for index, (product_url, source_page) in enumerate(book_urls, start=1):
        cache_file = CACHE_DIR / f"book-{index:03d}.html"

        if not cache_file.exists():
            sleep(REQUEST_DELAY)

        try:
            html = fetch_and_cache(product_url, cache_file)

            record = extract_book_record(
                html,
                product_url,
                source_page,
            )

            records.append(record)
            print(f"EXTRACTED | {index}/60 | {record['title']}")

        except Exception as exc:
            print(f"FAILED | {product_url} | {exc}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    import json

    output_file = OUTPUT_DIR / "raw_books.json"
    output_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"detail_pages={len(records)}")
    print(f"saved={output_file}")


if __name__ == "__main__":
    main()