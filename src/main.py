import os
import requests
import hashlib
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")
TIMEOUT = 10.0
MAX_PAGES = 3
DELAY = 0.5

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}

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
        html, isCached = fetch_page(current_url)

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

if __name__ == "__main__":
    print(discover_books())