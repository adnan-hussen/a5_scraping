import os
import requests
import hashlib
import time
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError
import re

from datetime import timezone, datetime

URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")
TIMEOUT = 10.0
MAX_PAGES = 3
DELAY = 0.5
OUTPUT_DIR = "output"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None = None
    source_page: HttpUrl
    fetched_at: str

def get_cache_path(url:str) -> str:
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, url_hash)

def fetch_page(url:str) -> tuple[str | None, bool]:

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_path(url)

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding='utf-8') as f:
            html = f.read()
        print(f"cache hit - file size: {len(html)}")
        return html, True

    time.sleep(DELAY)
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 200:
            html = response.text
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"FETCH - Response size: {len(html)} characters")
            return html, False
        else:
            print(f"failed fetch, status code {response.status_code}")
            return None, False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, False


def discover_books() -> list[str]:
    current_url = URL
    discovered_urls = []
    visited_pages = 0

    while current_url and visited_pages < MAX_PAGES:
        html, _ = fetch_page(current_url)

        if not html:
            break

        visited_pages += 1
        soup = BeautifulSoup(html, "html.parser")

        book_links = soup.select("article.product_pod h3 a")

        for link in book_links:
            rel_href = link.get("href")
            abs_url = urljoin(current_url, rel_href)
            discovered_urls.append(abs_url)

        next_link = soup.select_one("ul.pager li.next a")

        if next_link and visited_pages < MAX_PAGES:
            next_href = next_link.get("href")
            if next_href:
                current_url = urljoin(current_url, next_href)
            else:
                current_url = None

    unique_urls = list(set(discovered_urls))
    print(f"catalogue_pages={visited_pages}, discovered={len(discovered_urls)}, unique_urls={len(unique_urls)}")
    return unique_urls

def get_book_details(url: str) -> dict:
    html, _ = fetch_page(url)

    if not html:
        return None

    #parse the page
    soup = BeautifulSoup(html, "html.parser")

    main_prod = soup.select_one("div.product_main")
    if not main_prod:
        return None

    #select and extract the book details
    title = main_prod.select_one("h1").get_text(strip=True)
    price_text = main_prod.select_one("p.price_color").get_text(strip=True)
    availability_text = main_prod.select_one("p.instock.availability").get_text(strip=True)

    rating_el = main_prod.select_one("p.star-rating")
    rating_text = "Unknown"
    if rating_el:
        classes = rating_el.get("class", [])
        for cls in classes:
            if cls != "star-rating":
                rating_text = cls
                break
    
    desc_header = soup.find("div", id="product_description")
    description = None
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True)
    price_match = re.search(r"[\d.]+", price_text)
    price_gbp = float(price_match.group(0)) if price_match else 0.0

    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": url,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }



def process_and_store():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fetched_books = discover_books()

    valid_records = []
    errors = []

    for book_url in fetched_books:
        book_details = get_book_details(book_url)

        if not book_details:
            errors.append({"product_url":book_url, "reason": "Extraction failed" })
            continue

        #validation
        try:
            book_record = BookRecord(**book_details)
            valid_records.append(book_record.model_dump(mode="json"))
        except ValidationError as e:
            errors.append({"product_url":book_url, "reason": e.errors() })

    with open(os.path.join(OUTPUT_DIR, "books.json",), 'w', encoding="utf-8") as f:
        json.dump(valid_records,f, indent=1)
    with open(os.path.join(OUTPUT_DIR, "errors.json"), 'w', encoding="utf-8") as f:
        json.dump(errors, f, indent=1)

    print(f"Stored {len(valid_records)} valid records in output/books.json")
    print(f"Stored {len(errors)} failed records in output/errors.json")

if __name__ == "__main__":
    process_and_store()
