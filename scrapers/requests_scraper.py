import asyncio
import re
import urllib
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from ai_scraper.detectors.detect_rendering import detect_render_strategy
from ai_scraper.logging_config import logger
import tls_client
from ai_scraper.utils.env_loader import get_env_var
import os
import random


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
]
sec_ch_headers = {'142': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
                 '140': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                 '141': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                 '143': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
                 '144': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
                 '145': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
                 '146': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
                 '147': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
                 '149': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"'
                }

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
                content_type = response.headers.get('content-type', '')
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
    logger.info(f'PROXY_LIST: {get_env_var("PROXY_LIST")}')
    try:
        proxies = os.getenv("PROXY_LIST").split(",")
        proxy = random.choice(proxies)
        logger.info(f'proxy used: {proxy}')
        user_agent = random.choice(user_agents)
        ua_chrome_version = re.findall('Chrome\/(\d+)', user_agent)[0]
        sec_ch = sec_ch_headers[ua_chrome_version]
        headers = { 'sec-ch-ua': sec_ch,
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i'}
        session = tls_client.Session(random_tls_extension_order=True, client_identifier='chrome_120')
        def sync_request():
            return session.get(url, headers=headers, proxy=proxy)

        content = await asyncio.to_thread(sync_request)
        logger.debug(f'HTML length: {len(content.text)}')
        rendering_option = detect_render_strategy(content.text)
        logger.info(f'Rendering option: {rendering_option}')
        proxy_params = urllib.parse.urlparse(proxy)
        proxy = {
            "server": f"{proxy_params.scheme}://{proxy_params.hostname}:{proxy_params.port}",
            "username": proxy_params.username,
            "password": proxy_params.password
        }
        if rendering_option == 'playwright_dom':
            content = await playwright_dom(proxy, url)
            return clean_dom(content), 'html', 'playwright_dom'

        elif rendering_option == 'playwright_network':
            content = await playwright_network(proxy, fields, url)
            return content, 'json', 'playwright_network'

        return clean_dom(content.text), 'html', 'tls_client'


    except Exception as e:
        logger.error(f'[fetch_html] error: {e}',  exc_info=True)



# from ai_scraper.extractors.data_extractor import extract_data
# from ai_scraper.detectors.entity_detector import detect_html
# asyncio.run(fetch_html('https://web-scraping.dev/reviews', ['date', 'rating', 'text']))
# detected_html_blocks = detect_html(html, False)
# scraped_data = extract_data(detected_html_blocks, [ "date", "text", "ratings"])
# print(scraped_data)
