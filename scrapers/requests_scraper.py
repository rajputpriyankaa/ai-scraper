import asyncio
import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from ai_scraper.detectors.detect_rendering import detect_render_strategy
from ai_scraper.logging_config import logger
import tls_client
from ai_scraper.utils.env_loader import get_env_var
import os
import random

def clean_dom(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for tags in soup(["script", "style", "link", "meta", "noscript"]):
            tags.decompose()

        return str(soup)

    except Exception as e:
        logger.error(f'[clean_dom] error: {e}')


async def playwright_network(proxy, fields, url):
    best_response = []
    best_score = 0
    candidates = []
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True, proxy=proxy)
            page = await browser.new_page()

            async def handle_response(response):
                nonlocal best_response, best_score
                content_type = response.headers.get('content-type')
                logger.debug(f'response: {response}')
                if 'json' not in content_type.lower():
                    return
                try:
                    body = await response.json()
                    body_str = str(body).lower()
                    score = sum(1 for field in fields if field in body_str)
                    candidates.append({
                        "url": response.url,
                        "score": score,
                        "body": body
                    })
                    if score > best_score:
                        best_score = score
                        best_response = body

                except Exception:
                    pass

            page.on('response', handle_response)
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            await page.wait_for_load_state("networkidle")
            await browser.close()
            for c in sorted(candidates, key=lambda x: x['score'], reverse=True):
                logger.debug(f"score: {c['score']}, url: {c['url']}")
            return best_response

    except Exception as e:
        logger.error(f'[playwright_dom] error: {e}', exc_info=True)


async def playwright_dom(proxy, url):
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True, proxy=proxy)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            await page.wait_for_load_state("networkidle")
            content = await page.content()
            await browser.close()
            # logger.debug(f'HTML length: {len(content)}')
            return content

    except Exception as e:
        logger.error(f'[playwright_dom] error: {e}', exc_info=True)


async def fetch_html(url, fields):
    logger.info(f"DEBUG LOOP TYPE: {type(asyncio.get_event_loop())}")
    logger.info(f'GEMINI_API_KEY: {get_env_var("PROXY_LIST")}')
    proxies = os.getenv("PROXY_LIST").split(",")
    proxy = random.choice(proxies)
    logger.info(f'proxy used: {proxy}')
    try:
        session = tls_client.Session(random_tls_extension_order=True, client_identifier='chrome_120')
        def sync_request():
            return session.get(url, proxy=proxy)

        content = await asyncio.to_thread(sync_request)
        logger.debug(f'HTML length: {len(content.text)}')
        rendering_option = detect_render_strategy(content.text)
        logger.info(f'Rendering option: {rendering_option}')
        proxy_params = re.split(r'[//:@]', proxy)
        proxy = {
            "server": f"http://{proxy_params[5]}:{proxy_params[6]}",
            "username": proxy_params[3],
            "password": proxy_params[4]
        }
        if rendering_option == 'playwright_dom':
            content = await playwright_dom(proxy, url)
            return clean_dom(content), 'html'

        elif rendering_option == 'playwright_network':
            content = await playwright_network(proxy, fields, url)
            return content, 'json'

        return clean_dom(content.text), 'html'

    except Exception as e:
        logger.error(f'[fetch_html] error: {e}',  exc_info=True)



# from ai_scraper.extractors.data_extractor import extract_data
# from ai_scraper.detectors.entity_detector import detect_html
# asyncio.run(fetch_html('https://web-scraping.dev/reviews', ['date', 'rating', 'text']))
# detected_html_blocks = detect_html(html, False)
# scraped_data = extract_data(detected_html_blocks, [ "date", "text", "ratings"])
# print(scraped_data)
