# The Polite Scraper

A small Python scraping pipeline built for the FlyRank Backend AI Engineering
Week 5, Assignment A9 — "The polite scraper".

## Target classification

**Target:** https://books.toscrape.com/

**Classification:** Public scraping practice sandbox.

**Why this site:** Books to Scrape is a public practice sandbox designed for
learning web scraping.

**Scope:** The scraper collects books from the first three catalogue pages only.
The catalogue's own pagination links are followed to discover pages 2 and 3.

**Expected dataset:** 60 unique books (20 books per catalogue page).

**Data collected:**

* `title`
* `product_url`
* `price_text`
* `availability_text`
* `rating_text`
* `description`
* `source_page`
* `fetched_at`

The normalized dataset additionally contains:

* `price_gbp`

I will not reuse this code on another site without checking its rules and terms first.

## Robots check

The scraper requested:

```text
https://books.toscrape.com/robots.txt
```

The server returned:

```text
HTTP 404 Not Found
```

Therefore, no `robots.txt` file was found. A missing robots file is not treated
as permission to scrape.

The assignment target is a public scraping practice sandbox, and this project
limits requests to the required catalogue and product pages.

## Politeness measures

The scraper uses the following measures:

* Identifying User-Agent header
* 10-second request timeout
* At least 500 ms delay between real product-page requests
* Local HTML caching during development
* Cached pages are reused instead of being repeatedly downloaded
* HTTP status codes are checked
* Bounded retries are used for transient failures
* Retry count is limited to 2 attempts
* Retry delay is 1 second
* HTTP 429, 500, 502, 503, and 504 are treated as transient failures
* 404 and 403 responses are not retried
* The scraper does not crawl beyond the first three catalogue pages
* Only the discovered 60 book URLs are processed

## Pipeline stages

### Stage 0 — Target classification

Completed.

The target was classified as a public scraping practice sandbox and the
`robots.txt` endpoint was checked before scraping.

### Stage 1 — Fetch and cache HTML

Completed.

Catalogue and product HTML are cached locally in:

```text
scraper/cache/
```

Cached pages are reused during development to avoid unnecessary requests.

The scraper uses a descriptive User-Agent:

```text
FlyRankInternshipA9/1.0 (+https://github.com/HK-dev118/flyrank-auth-api)
```

A 10-second timeout and HTTP status checking are used for requests.

### Stage 2 — Discover catalogue pages

Completed.

The scraper follows the catalogue's own `next` navigation to discover exactly
three catalogue pages.

Result:

```text
catalogue_pages=3
discovered=60
unique_urls=60
```

Relative product and pagination links are converted to absolute URLs using
`urljoin`.

### Stage 3 — Extract book details

Completed.

The scraper processes the 60 discovered product pages and extracts exactly
eight raw fields:

```text
title
product_url
price_text
availability_text
rating_text
description
source_page
fetched_at
```

If a description is missing, it is represented as `null`.

Raw records are stored in:

```text
scraper/output/raw_books.json
```

Final extraction result:

```text
detail_pages=60
```

### Stage 4 — Normalize and validate

Completed.

The raw records are normalized and validated with Pydantic.

The original `price_text` field is preserved while a numeric `price_gbp` field
is added.

Example:

```text
price_text: £51.77
price_gbp: 51.77
```

Every normalized record is validated against the Pydantic schema.

Validation failures are written to:

```text
scraper/output/validation_errors.json
```

Final validation result:

```text
raw_records=60
valid_records=60
validation_errors=0
```

The final normalized dataset is:

```text
scraper/output/books.json
```

### Stage 5 — Failure handling and run reporting

Completed.

The scraper handles each product page separately so that one broken page does
not terminate the entire run.

Transient request failures are retried with bounded retries. Non-retryable
HTTP errors such as 404 and 403 are not repeatedly retried.

Every run creates:

```text
scraper/output/run-report.json
```

The report contains:

* `started_at`
* `finished_at`
* `duration_seconds`
* `pages_fetched`
* `cache_hits`
* `valid_records`
* `invalid_records`
* `failed_pages`

#### Normal clean run

The final clean run produced:

```json
{
  "duration_seconds": 1.516,
  "pages_fetched": 0,
  "cache_hits": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

The zero `pages_fetched` value is expected for this run because all 60 product
pages were already available in the local cache.

#### Deliberate failure test

A temporary fake product URL was deliberately added to verify failure
handling:

```text
https://books.toscrape.com/catalogue/this-page-does-not-exist/index.html
```

The server returned HTTP 404. The scraper logged the failure, skipped the
broken page, and completed normally.

The failure-test run produced:

```text
detail_pages=60
valid_records=60
failed_pages=1
```

This verified that one broken page does not prevent the remaining 60 valid
records from being produced.

The fake URL was removed after the test and is not part of the final scraper.

### Stage 6 — Documentation and evidence

Completed.

The repository contains the scraper implementation, normalized dataset,
validation results, failure report, and run report.

The cache directory is excluded from Git so downloaded HTML is not published.

## Project structure

```text
scraper/
├── README.md
├── cache/
├── output/
│   ├── books.json
│   ├── failure_report.json
│   ├── raw_books.json
│   ├── run-report.json
│   └── validation_errors.json
└── src/
    ├── main.py
    ├── models.py
    ├── normalize.py
    ├── reliability.py
    └── failure_report.py
```

The `cache/` directory is ignored by Git because it contains development
copies of downloaded HTML pages.

## Language and dependencies

Python 3.10+

Install dependencies with:

```powershell
pip install requests beautifulsoup4 pydantic
```

The project uses:

* `requests`
* `beautifulsoup4`
* `pydantic`

## Running the scraper

From the repository root, run:

```powershell
python scraper\src\main.py
```

This discovers the first three catalogue pages, processes the 60 discovered
books, and writes:

```text
scraper/output/raw_books.json
scraper/output/run-report.json
```

Then normalize and validate:

```powershell
python scraper\src\normalize.py
```

This creates:

```text
scraper/output/books.json
scraper/output/validation_errors.json
```

A failure summary can also be generated with:

```powershell
python scraper\src\failure_report.py
```

This creates:

```text
scraper/output/failure_report.json
```

## Data schema

Each final book record contains:

```text
title              string
product_url        absolute URL
price_text         string
price_gbp          number
availability_text  string
rating_text        string
description        string or null
source_page        absolute URL
fetched_at         ISO timestamp
```

`price_text` is retained as the original raw value while `price_gbp` provides
a numeric representation for downstream analysis.

## Caching

Downloaded catalogue and product HTML pages are cached locally during
development.

This prevents unnecessary repeated requests when testing extraction and
normalization.

The cache directory is excluded from version control.

A rerun using the existing cache produces `CACHE HIT` messages instead of
re-downloading the same pages.

## Scope limitations

This scraper intentionally does not attempt to crawl the entire website.

It is limited to:

1. The main catalogue page
2. Catalogue page 2
3. Catalogue page 3
4. The 60 unique book product pages discovered from those catalogue pages

The scraper is designed specifically for the FlyRank assignment and is not
intended to be a general-purpose crawler.

**Limitation:** The scraper is tailored to the current HTML structure of Books
to Scrape, so changes to the site's markup could require parser updates.

## Why no browser is needed

A browser automation tool is unnecessary because the target pages provide the
required catalogue and product information directly in server-rendered HTML.
The scraper can therefore use ordinary HTTP requests and HTML parsing instead
of incurring the extra complexity and resource cost of browser automation.

## Ethical and responsible scraping

This project follows a limited and polite scraping approach:

* The target is a public scraping practice sandbox.
* The `robots.txt` endpoint was checked before scraping.
* Requests use an identifying User-Agent.
* Requests have a timeout.
* Requests are rate-limited.
* Development caching reduces repeated requests.
* The crawler has a strict page scope.
* Transient failures use bounded retries.
* The scraper does not attempt to bypass access restrictions.
* Only the data required by the assignment is collected.

If an official API exists for a target website, it should be preferred where
appropriate.

This scraper must not be used to bypass login systems, paywalls, access
controls, or blocking mechanisms.

Before scraping a different website, its robots rules, terms, and applicable
policies should be checked first.

## Final result

The completed pipeline successfully produced:

```text
3 catalogue pages
60 unique books
60 product pages
60 valid records
0 validation errors
0 failures in the final clean run
```

The main final dataset is:

```text
scraper/output/books.json
```

The run evidence is:

```text
scraper/output/run-report.json
```

The validation error file is:

```text
scraper/output/validation_errors.json
```

The failure summary is:

```text
scraper/output/failure_report.json
```
