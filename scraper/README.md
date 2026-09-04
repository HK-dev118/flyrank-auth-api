# The Polite Scraper

A small Python scraping pipeline built for FlyRank Backend AI Engineering — Week 5, Assignment A9.

## Target classification

**Target:** [Books to Scrape](https://books.toscrape.com/)

**Why this site:** Books to Scrape is a public practice sandbox designed for learning web scraping.

**Scope:** The scraper will collect books from the first three catalogue pages only, discovering the links from the catalogue's own navigation.

**Data collected:** Book title, product URL, price text, availability text, rating text, description, source page, and fetch timestamp.

**Robots check:** Checked `https://books.toscrape.com/robots.txt` before writing the scraper. The result will be recorded here after the check.

**Why this is appropriate:** This assignment uses a public practice sandbox specifically intended for scraping exercises and limits collection to the required three catalogue pages.

I will not reuse this code on another site without checking its rules and terms first.

## Project status

* [ ] Stage 0 — Target classification
* [ ] Stage 1 — Fetch and cache HTML
* [ ] Stage 2 — Discover three catalogue pages
* [ ] Stage 3 — Extract book details
* [ ] Stage 4 — Validate normalized records
* [ ] Stage 5 — Survive failures and report the run
* [ ] Stage 6 — Publish scraper evidence

## Python version

Python 3.10+

## Installation

```bash
pip install -r requirements.txt
```

## Run

The run command will be documented after the scraper is implemented.
