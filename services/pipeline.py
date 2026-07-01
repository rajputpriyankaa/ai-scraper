from ai_scraper.extractors.data_extractor import extract_html_data, json_extraction
from ai_scraper.scrapers.requests_scraper import fetch_html
from ai_scraper.detectors.entity_detector import detect_html
from ai_scraper.detectors.result_validator import validate_data, deduplicate_data
from ai_scraper.metrics_store import add_latency, metrics_dic, update_strategy
from ai_scraper.logging_config import logger
import time
import pandas as pd


async def run_pipeline(url, fields, format):
    try:
        start = time.time()
        response, response_type, strategy = await fetch_html(
            url,
            fields
        )
        fetch_time = time.time() - start
        logger.info(f"Fetch took: {fetch_time:.2f}s")
        logger.debug(f"URL, FIELDS & FORMAT: {url}, {fields} & {format}")
        logger.debug(f"content Length: {len(response)}")
        if response_type == 'html':
            detect_start = time.time()
            detected_html_blocks = detect_html(response)
            detect_time = time.time() - detect_start
            logger.info(f"Detection took: {detect_time:.2f}s")
            extract_start = time.time()
            scraped_data = extract_html_data(detected_html_blocks, fields)
            extract_time = time.time() - extract_start
            logger.info(f"Extraction took: {extract_time:.2f}s")

        else:
            scraped_data = json_extraction(response, fields)
            detect_time = 0.0
            extract_time = 0.0

        if not scraped_data:
            logger.error('[run_pipeline] extraction returned empty data')
            return None, None

        actual_fields = scraped_data[0].keys() if len(scraped_data) > 0 else []
        missing_fields = validate_data(fields, actual_fields)
        final_data = deduplicate_data(scraped_data, actual_fields)
        final_dict = {'data': final_data,
                      "meta": {
                          "strategy": strategy,
                          "fetch_time_ms": fetch_time,
                          "detect_time_ms": detect_time,
                          "extract_time_ms": extract_time,
                          "fields_requested": fields,
                          "fields_missing": missing_fields,
                          "ai_calls": 2 if response_type == 'html' else 1
                      }
                      }
        logger.debug(f'final_dict: {final_dict}')
        add_latency(fetch_time + detect_time + extract_time)
        update_strategy(strategy)
        if format == "csv":
            df = pd.DataFrame(final_dict['data'])
            df.to_csv("output.csv", index=False)
        else:
            df = pd.DataFrame(final_dict['data'])
            df.to_json("output.json", orient="records", indent=2)

        return final_dict['data'], final_dict['meta']

    except Exception as e:
        logger.error(f'[run_pipeline] error: {e}')
