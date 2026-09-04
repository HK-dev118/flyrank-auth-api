import json
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from reliability import fetch_with_retry


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

    cache_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

    cache_file.write_text(
        html,
        encoding="utf-8",
    )

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

        html = fetch_and_cache(
            current_url,
            cache_file,
        )

        pages.append(
            (
                current_url,
                html,
            )
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        next_link = soup.select_one("li.next a")

        if not next_link:
            break

        current_url = urljoin(
            current_url,
            next_link["href"],
        )

    return pages


def discover_book_urls(
    pages: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Discover unique book URLs and their source catalogue pages."""

    discovered = []

    for page_url, html in pages:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        for link in soup.select(
            "article.product_pod h3 a"
        ):
            book_url = urljoin(
                page_url,
                link["href"],
            )

            discovered.append(
                (
                    book_url,
                    page_url,
                )
            )

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

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    product = soup.select_one(
        "article.product_page"
    )

    if product is None:
        raise ValueError(
            "Product area not found"
        )

    title = product.select_one("h1")
    price = product.select_one(".price_color")
    availability = product.select_one(".availability")
    rating = product.select_one("p.star-rating")
    description = soup.select_one(
        "#product_description + p"
    )

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "title": (
            title.get_text(strip=True)
            if title
            else None
        ),
        "product_url": product_url,
        "price_text": (
            price.get_text(strip=True)
            if price
            else None
        ),
        "availability_text": (
            availability.get_text(
                " ",
                strip=True,
            )
            if availability
            else None
        ),
        "rating_text": (
            " ".join(
                rating.get("class", [])
            )
            if rating
            else None
        ),
        "description": (
            description.get_text(
                " ",
                strip=True,
            )
            if description
            else None
        ),
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def main():
    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    start_time = monotonic()

    pages_fetched = 0
    cache_hits = 0
    failed_pages = 0

    pages = discover_catalogue_pages()

    book_urls = discover_book_urls(
        pages
    )

    print(
        f"catalogue_pages={len(pages)}"
    )

    print(
        f"discovered={len(book_urls)}"
    )

    records = []

    for index, (
        product_url,
        source_page,
    ) in enumerate(
        book_urls,
        start=1,
    ):
        cache_file = (
            CACHE_DIR
            / f"book-{index:03d}.html"
        )

        if cache_file.exists():
            cache_hits += 1

            html = cache_file.read_text(
                encoding="utf-8"
            )

            print(
                f"CACHE HIT | status=200 | "
                f"bytes={len(html.encode('utf-8'))}"
            )

        else:
            if index > 1:
                sleep(REQUEST_DELAY)

            headers = {
                "User-Agent": USER_AGENT,
            }

            print(
                f"FETCH | url={product_url}"
            )

            result = fetch_with_retry(
                product_url,
                headers=headers,
                timeout=TIMEOUT,
            )

            if result.html is None:
                failed_pages += 1

                print(
                    f"FAILED | {product_url} | "
                    f"{result.error}"
                )

                continue

            html = result.html

            pages_fetched += 1

            cache_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            cache_file.write_text(
                html,
                encoding="utf-8",
            )

            print(
                f"FETCHED | status={result.status_code} | "
                f"bytes={len(html.encode('utf-8'))}"
            )

        try:
            record = extract_book_record(
                html,
                product_url,
                source_page,
            )

            records.append(record)

            print(
                f"EXTRACTED | {index}/60 | "
                f"{record['title']}"
            )

        except Exception as exc:
            failed_pages += 1

            print(
                f"FAILED | {product_url} | "
                f"{exc}"
            )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        OUTPUT_DIR / "raw_books.json"
    )

    output_file.write_text(
        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    duration = (
        monotonic() - start_time
    )

    report = {
        "started_at": started_at,
        "finished_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "duration_seconds": round(
            duration,
            3,
        ),
        "pages_fetched": pages_fetched,
        "cache_hits": cache_hits,
        "valid_records": len(records),
        "invalid_records": 0,
        "failed_pages": failed_pages,
    }

    report_file = (
        OUTPUT_DIR / "run-report.json"
    )

    report_file.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"detail_pages={len(records)}"
    )

    print(
        f"saved={output_file}"
    )

    print(
        f"run_report={report_file}"
    )


if __name__ == "__main__":
    main()