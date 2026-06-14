from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

def clean_dom(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for tags in soup(["script", "style", "link", "meta", "noscript"]):
            tags.decompose()

        return str(soup)

    except Exception as e:
        print(f'[clean_dom] error: {e}')


def fetch_html(url):
    try:
        # with sync_playwright() as playwright:
        #     browser = playwright.chromium.launch(headless=True)
        #     page = browser.new_page()
        #     page.goto(url)
        #     page.wait_for_load_state("domcontentloaded", timeout=30000)
        #     content = page.content()
        #     browser.close()
        #     print(f'HTML length: {len(content)}')
        #     return clean_dom(content)
        content = requests.get(url)
        print(f'HTML length: {len(content.text)}')
        return clean_dom(content.text)

    except Exception as e:
        print(f'[fetch_html] error: {e}')
