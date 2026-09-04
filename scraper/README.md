# The Polite Scraper

A small Python scraping pipeline built for the FlyRank Backend AI Engineering
Week 5, Assignment A9 — "The polite scraper".

## Target classification

**Target:** https://books.toscrape.com/

**Why this site:** Books to Scrape is a public practice sandbox designed for
learning web scraping.

**Scope:** The scraper collects books from the first three catalogue pages only.
The catalogue's own pagination links are followed to discover pages 2 and 3.

**Expected dataset:** 60 unique books (20 books per catalogue page).

**Data collected:**

- `title`
- `product_url`
- `price_text`
- `price_gbp`
- `availability_text`
- `rating_text`
- `description`
- `source_page`
- `fetched_at`

I will not reuse this scraper on another site without checking that site's
rules and terms first.

## Robots check

The scraper requested:

https://books.toscrape.com/robots.txt

The server returned:

**HTTP 404 Not Found**

Therefore, no `robots.txt` file was found. A missing robots file is not treated
as permission to scrape.

The assignment target is a public scraping practice sandbox, and this project
limits requests to the required catalogue and product pages.

## Politeness measures

The scraper uses the following measures:

- Identifying User-Agent header
- 10-second request timeout
- At least 500 ms delay before each real product-page request
- Local HTML caching during development
- Cached pages are reused instead of being repeatedly downloaded
- HTTP status codes are checked
- Bounded retries are used for transient failures
- Retry count is limited to 3 attempts
- Retry delay is 1 second
- The scraper does not crawl beyond the first three catalogue pages
- Only the discovered 60 book URLs are processed

## Pipeline stages

### Stage 0 — Target classification

Completed.

The target was classified as a public scraping practice sandbox and the
`robots.txt` endpoint was checked before scraping.

### Stage 1 — Fetch and cache HTML

Completed.

Catalogue HTML is downloaded and cached locally in:

```text
scraper/cache/
```
Cached pages are reused during development to avoid unnecessary requests.

### Stage 2 — Discover catalogue pages

Completed.

The scraper follows the catalogue's `next` navigation to discover exactly three catalogue pages.

Result:

```text
catalogue_pages=3
discovered=60
unique_urls=60
```

### Stage 3 — Extract book details

Completed.

All 60 discovered product pages were fetched and extracted successfully.

Raw records are stored in:

```text
scraper/output/raw_books.json
```

### Stage 4 — Normalize and validate

Completed.

The raw records are normalized and validated with Pydantic.

The `price_text` field is preserved while a numeric `price_gbp` field is added.

Final validated records:

```text
60
```

Validation errors:

```text
0
```

Output files:

```text
scraper/output/books.json
scraper/output/validation_errors.json
```

### Stage 5 — Failure handling and reporting

Completed.

The project includes bounded retry handling for transient HTTP failures and request exceptions.

A failure report is generated at:

```text
scraper/output/failure_report.json
```

The completed run produced:

```text
validation_failures=0
fetch_failures=0
total_failures=0
```

### Stage 6 — Documentation and evidence

Completed.

The repository contains the scraper implementation, cached development structure, raw data, normalized data, validation results, and failure report.

## Project structure

```text
scraper/
├── README.md
├── cache/
├── output/
│   ├── books.json
│   ├── failure_report.json
│   ├── raw_books.json
│   └── validation_errors.json
└── src/
    ├── main.py
    ├── models.py
    ├── normalize.py
    ├── reliability.py
    └── failure_report.py
```

The `cache/` directory is ignored by Git because it contains development copies of downloaded HTML pages.

## Python version

Python 3.10+

## Dependencies

The project uses:

* `requests`
* `beautifulsoup4`
* `pydantic`

Install dependencies with:

```powershell
pip install requests beautifulsoup4 pydantic
```

## Running the scraper

From the repository root:

```powershell
python scraper\src\main.py
```

This discovers the first three catalogue pages, processes the 60 discovered books, and writes:

```text
scraper/output/raw_books.json
```

## Normalizing and validating

Run:

```powershell
python scraper\src\normalize.py
```

This creates:

```text
scraper/output/books.json
scraper/output/validation_errors.json
```

## Generating the failure report

Run:

```powershell
python scraper\src\failure_report.py
```

This creates:

```text
scraper/output/failure_report.json
```

## Evidence from the completed run

The extraction run completed with:

```text
catalogue_pages=3
discovered=60
detail_pages=60
```

Normalization completed with:

```text
raw_records=60
valid_records=60
validation_errors=0
```

The failure report completed with:

```text
validation_failures=0
fetch_failures=0
total_failures=0
```

The final dataset therefore contains 60 validated book records.

## Data normalization

The scraper preserves the original `price_text` field and creates a numeric `price_gbp` field for reliable downstream use.

For example:

```text
price_text: Â£51.77
price_gbp: 51.77
```

Some raw text from the target site may contain encoding artifacts such as `Â£` in the original price text. The numeric `price_gbp` field is normalized from the price value so it can be used reliably for analysis.

## Failure handling

Transient request failures are retried up to three times.

The retry mechanism handles:

* Request exceptions
* HTTP 429
* HTTP 500
* HTTP 502
* HTTP 503
* HTTP 504

Other HTTP errors are recorded without repeatedly retrying them.

Validation failures are recorded separately in:

```text
scraper/output/validation_errors.json
```

The overall run summary is stored in:

```text
scraper/output/failure_report.json
```

## Caching

During development, downloaded catalogue and product HTML pages are cached locally.

This prevents unnecessary repeated requests when testing extraction and normalization.

The cache directory is excluded from version control.

## Scope limitations

This scraper intentionally does not attempt to crawl the entire website.

It is limited to:

1. The main catalogue page
2. Catalogue page 2
3. Catalogue page 3
4. The 60 unique book product pages discovered from those catalogue pages

The scraper is designed specifically for the FlyRank assignment and is not intended to be a general-purpose crawler.

## Ethical and responsible scraping

This project follows a limited and polite scraping approach:

* The target is a public scraping practice sandbox.
* The robots endpoint was checked before scraping.
* Requests use an identifying User-Agent.
* Requests have a timeout.
* Requests are rate-limited.
* Development caching reduces repeated requests.
* The crawler has a strict page scope.
* Transient failures use bounded retries.
* The scraper does not attempt to bypass access restrictions.

The same approach should not automatically be applied to another website.

Before scraping a different website, its robots rules, terms, and applicable policies should be checked.

## Final result

The completed pipeline successfully discovered and processed:

```text
3 catalogue pages
60 unique books
60 product pages
60 valid records
0 validation errors
0 reported failures
```

The main final dataset is:

```text
scraper/output/books.json
```
