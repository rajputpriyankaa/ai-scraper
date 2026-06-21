from fastapi import FastAPI
from pydantic import BaseModel
from ai_scraper.services.pipeline import run_pipeline
from ai_scraper.logging_config import logger

app = FastAPI()


class ScrapeRequest(BaseModel):
    url: str
    fields: list[str]
    format: str = "json"


@app.post("/extract")
async def scrape(req: ScrapeRequest):
    logger.info("Extractor endpoint called")
    return await run_pipeline(
        req.url,
        req.fields,
        req.format
    )
