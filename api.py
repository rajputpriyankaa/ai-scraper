from fastapi import FastAPI
from pydantic import BaseModel
from ai_scraper.services.pipeline import run_pipeline
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")
app = FastAPI()
print("Current working directory:", os.getcwd())
print(f'GEMINI_API_KEY: {os.getenv("GEMINI_API_KEY")}')

class ScrapeRequest(BaseModel):
    url: str
    fields: list[str]
    format: str = "json"
    use_mock: bool = False


@app.post("/extract")
def scrape(req: ScrapeRequest):
    return run_pipeline(
        req.url,
        req.fields,
        req.format,
        req.use_mock
    )
