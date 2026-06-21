from ai_scraper.extractors.data_extractor import extract_data
from ai_scraper.scrapers.requests_scraper import fetch_html
from ai_scraper.detectors.entity_detector import detect_html
from ai_scraper.logging_config import logger
import time
import pandas as pd


def run_pipeline(url, fields, format, use_mock):
    try:
        start = time.time()
        html = fetch_html(
            url
        )
        logger.info(f"Fetch took: {time.time() - start:.2f}s")

        logger.debug(f"URL: {url}")
        logger.debug(f"FIELDS: {fields}")
        logger.debug(f"FORMAT: {format}")
        logger.debug(f"HTML Length: {len(html)}")
        detect_start = time.time()
        detected_html_blocks = detect_html(html, use_mock)
        logger.info(f"Detection took: {time.time() - detect_start:.2f}s")
        extract_start = time.time()
        scraped_data = extract_data(detected_html_blocks, fields)
        # logger.info(f'type of type(scraped_data): {type(scraped_data)}')

        if format == "csv":
            df = pd.DataFrame(scraped_data)
            df.to_csv("output.csv", index=False)
        else:
            df = pd.DataFrame(scraped_data)
            df.to_json("output.json", index=False)

        logger.info(f"Extraction took: {time.time() - extract_start:.2f}s")
        return scraped_data

    except Exception as e:
        logger.error(f'[run_pipeline] error: {e}')
