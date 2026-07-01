from fastapi import FastAPI
from pydantic import BaseModel
from ai_scraper.services.pipeline import run_pipeline
from ai_scraper.logging_config import logger
from ai_scraper.metrics_store import update_metrics, metrics_dic

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    fields: list[str]
    format: str = "json"


class ScrapeMeta(BaseModel):
    strategy: str
    fetch_time_ms: float
    detect_time_ms: float
    extract_time_ms: float
    fields_requested: list[str]
    fields_missing: list[str]
    ai_calls: int

class ScrapeResponse(BaseModel):
    data: list[dict]
    meta: ScrapeMeta


@app.post("/extract", response_model=ScrapeResponse)
async def scrape(req: ScrapeRequest):
    logger.info("Extractor endpoint called")
    update_metrics('total_requests')
    data, meta = await run_pipeline(
        req.url,
        req.fields,
        req.format
    )
    return ScrapeResponse(data=data, meta=meta)


@app.get("/metrics")
async def metrics():
    logger.info("Metrics endpoint called")
    metrics_dic['avg_latency_ms'] = (
    round(metrics_dic["total_latency_ms"] / metrics_dic["total_requests"], 2)
    if metrics_dic["total_requests"] > 0 else 0)
    metrics_dic['success_rate'] = (round(metrics_dic["success_count"] / metrics_dic["total_requests"], 2) if metrics_dic["total_requests"] > 0 else 0)
    return metrics_dic
