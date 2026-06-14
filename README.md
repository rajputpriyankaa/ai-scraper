# AI Scraper

A generic AI-powered extraction platform that:

- Detects entity blocks automatically
- Extracts user-requested fields
- Supports JSON and CSV output
- Exposes a FastAPI API

## Example

POST /extract

{
  "url": "https://books.toscrape.com",
  "fields": [
    "title",
    "price"
  ]
}