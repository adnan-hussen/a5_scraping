import os
import requests

URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")
TIMEOUT = 10.0

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}

def fetch_and_cache():

    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding='utf-8') as f:
            html = f.read()
        print(f"cache hit - file size: {len(html)}")
        return html

    else:
        try:
            response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
            if response.status_code == 200:
                html = response.text
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"FETCH - Response size: {len(html)} characters")
                return html
            else:
                print(f"failed fetch, status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_cache()