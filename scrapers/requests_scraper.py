from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ai_scraper.detectors.detect_rendering import detect_render_strategy
from ai_scraper.logging_config import logger
import requests

def clean_dom(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for tags in soup(["script", "style", "link", "meta", "noscript"]):
            tags.decompose()

        return str(soup)

    except Exception as e:
        logger.error(f'[clean_dom] error: {e}')




def fetch_html(url):
    try:
        content = requests.get(url)
        logger.debug(f'HTML length: {len(content.text)}')
        rendering_option = detect_render_strategy(content.text)
        logger.info(f'Rendering option: {rendering_option}')
        # if rendering_option == 'playwright_dom':
        #     with sync_playwright() as playwright:
        #         browser = playwright.chromium.launch(headless=True)
        #         page = browser.new_page()
        #         page.goto(url)
        #         page.wait_for_load_state("domcontentloaded", timeout=30000)
        #         page.wait_for_load_state("networkidle")
        #         # page.wait_for_timeout(random.randint(8000, 10000))
        #         content = page.content()
        #         browser.close()
        #         logger.debug(f'HTML length: {len(content)}')
        #         logger.debug(f'HTML content: {content}')
        #         return clean_dom(content)


        return clean_dom(content.text)

    except Exception as e:
        logger.error(f'[fetch_html] error: {e}',  exc_info=True)



# async def fetch_html(url: str):
#     try:
#         resp = requests.get(url, timeout=15)
#         logger.debug("HTML length: %d", len(resp.text))
#
#         rendering_option = detect_render_strategy(resp.text)
#         logger.info("Rendering option: %s", rendering_option)
#
#         if rendering_option == "playwright_dom":
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(headless=True)
#                 page = await browser.new_page()
#                 await page.goto(url, timeout=30000)
#                 await page.wait_for_load_state("domcontentloaded")
#                 html = await page.content()
#                 await browser.close()
#                 logger.debug("HTML length after Playwright: %d", len(html))
#                 return clean_dom(html)
#
#         return clean_dom(resp.text)


    except Exception as e:
        logger.error(f'[fetch_html] error: {e}',  exc_info=True)
        return None


# from ai_scraper.extractors.data_extractor import extract_data
# from ai_scraper.detectors.entity_detector import detect_html
# html = fetch_html('https://web-scraping.dev/reviews')
# detected_html_blocks = detect_html(html, False)
# scraped_data = extract_data(detected_html_blocks, [ "date", "text", "ratings"])
# print(scraped_data)