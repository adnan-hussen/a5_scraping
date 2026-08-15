# FlyRank internship - W5-A9: The Polite Scraper

A polite, deterministic web scraping pipeline in Python that extracts book data from the Books to Scrape sandbox, normalizes messy HTML, validates records against a strict schema, and continues running smoothly even when encountering broken pages.

---

## Target Classification

* **Target Site**: `https://books.toscrape.com/`
* **Scope**: First 3 catalogue pages (60 unique book URLs).
* **Collected Data**: Title, product URL, raw price, numeric price (GBP), stock status, rating, description, source page provenance, and fetch timestamp.
* **Robots Exclusion Check**: Checked `https://books.toscrape.com/robots.txt` (`404 Not Found`—no specific rules defined).
* **Permission & Rules**: *I will not reuse this code on another site without checking its rules and terms first.*

---

## Requirements & Setup

### Environment
* Python 3.10+

### Installation
```bash
pip install requests beautifulsoup4 pydantic
