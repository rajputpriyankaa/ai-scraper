from ai_scraper.extractors.data_extractor import extract_html_data, json_extraction
from ai_scraper.scrapers.requests_scraper import fetch_html
from ai_scraper.detectors.entity_detector import detect_html
from ai_scraper.logging_config import logger
import time
import pandas as pd


async def run_pipeline(url, fields, format):
    try:
        start = time.time()
        response, response_type = await fetch_html(
            url,
            fields
        )
        logger.info(f"Fetch took: {time.time() - start:.2f}s")

        logger.debug(f"URL, FIELDS & FORMAT: {url}, {fields} & {format}")
        logger.debug(f"content Length: {len(response)}")
        if response_type == 'html':
            detect_start = time.time()
            detected_html_blocks = detect_html(response)
            logger.info(f"Detection took: {time.time() - detect_start:.2f}s")
            extract_start = time.time()
            scraped_data = extract_html_data(detected_html_blocks, fields)
            logger.info(f"Extraction took: {time.time() - extract_start:.2f}s")

        else:
            scraped_data = json_extraction(response, fields)

        if format == "csv":
            df = pd.DataFrame(scraped_data)
            df.to_csv("output.csv", index=False)
        else:
            df = pd.DataFrame(scraped_data)
            df.to_json("output.json", index=False)

        return scraped_data

    except Exception as e:
        logger.error(f'[run_pipeline] error: {e}')
