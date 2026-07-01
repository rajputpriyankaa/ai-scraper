from ai_scraper.logging_config import logger
from ai_scraper.metrics_store import update_metrics

def validate_data(requested_fields: list, actual_fields: list) -> list:
    missing_fields = []
    try:
        for field in requested_fields:
            if field not in actual_fields:
                missing_fields.append(field)

        if len(missing_fields) == 0:
            update_metrics('success_count')
        else:
            logger.info(f'[validate_data] fields missing: {missing_fields}')

        return missing_fields


    except Exception as e:
        logger.error(f'[validate_data] error: {e}', exc_info=True)
        return []


def deduplicate_data(scraped_data: list, actual_fields: list) -> list:
    seen = []
    result = []
    try:
        for record in scraped_data:
            key = [record[field] for field in actual_fields if field in record]
            if key not in seen:
                seen.append(key)
                result.append(record)
        return result


    except Exception as e:
        logger.error(f'[deduplicate_data] error: {e}')
        return scraped_data