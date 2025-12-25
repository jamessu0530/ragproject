import requests
from bs4 import BeautifulSoup

def fetch_url_content(url: str) -> str | None:
    print(f"Fetching URL")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"抓取失敗：{e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    for script in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        script.extract()
    text = soup.get_text(separator="\n")
    cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]
    return "\n".join(cleaned_lines)
