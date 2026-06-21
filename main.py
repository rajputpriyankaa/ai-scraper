import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == '__main__':
    # uvicorn.run("ai_scraper.api:app", reload=True)
    uvicorn.run("ai_scraper.api:app", reload=False)