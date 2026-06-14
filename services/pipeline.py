from ai_scraper.extractors.data_extractor import extract_data
from ai_scraper.scrapers.requests_scraper import fetch_html
from ai_scraper.detectors.entity_detector import detect_html
import time
import pandas as pd


def run_pipeline(url, fields, format, use_mock):
    try:
        start = time.time()
        html = fetch_html(
            url
        )
        print(f"Fetch took: {time.time() - start:.2f}s")

        print("URL:", url)
        print("FIELDS:", fields)
        print("FORMAT:", format)
        print(f"HTML Length: {len(html)}")
        detect_start = time.time()
        detected_html_blocks = detect_html(html, use_mock)
        print(f"Detection took: {time.time() - detect_start:.2f}s")
        extract_start = time.time()
        scraped_data = extract_data(detected_html_blocks, fields)
        print(f'type of type(scraped_data): {type(scraped_data)}')
        # print(f'scraped_data: {scraped_data}')
        if format == "csv":
            df = pd.DataFrame(scraped_data)
            df.to_csv("output.csv", index=False)
        else:
            df = pd.DataFrame(scraped_data)
            df.to_json("output.json", index=False)

        print(f"Extraction took: {time.time() - extract_start:.2f}s")
        return scraped_data

    except Exception as e:
        print(f'[run_pipeline] error: {e}')
