# 🕷️ AI-Powered Web Scraper

An intelligent web scraping system that combines adaptive rendering detection, HTML scoring, and LLM-based extraction into a single FastAPI pipeline. Instead of blindly feeding entire pages to an AI, the system routes each URL through the right strategy and minimizes AI usage to only where it's needed.

---

## 🧠 How It Works

```
POST /scrape  { url, fields[] }
        │
        ▼
┌─────────────────────────────┐
│   HTTP Request (requests)   │  ← Fast, lightweight first attempt
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│             Render Strategy Detector                │
│                                                     │
│  • Measure visible text after stripping scripts     │
│  • Scan for GraphQL client hints (Apollo, urql)     │
│  • Scan for fetch/XHR/API patterns in inline JS     │
│  • Check for SPA framework markers (Next, Nuxt, ng) │
└─────────────────────────────────────────────────────┘
        │
        ├──── requests_ok ──────────────────────────────────────┐
        │                                                       │
        ├──── playwright_dom ────────────────────────┐          │
        │                                            │          │
        └──── playwright_network ──────┐             │          │
                                       │             │          │
                    ┌──────────────────▼──┐   ┌──────▼──┐  ┌───▼───┐
                    │ Intercept XHR/fetch │   │Rendered │  │  Raw  │
                    │  JSON / GraphQL     │   │  DOM    │  │  HTML │
                    └──────────┬──────────┘   └────┬────┘  └───┬───┘
                               │                   │           │
                               └───────────────────┴───────────┘
                                                   │
                                                   ▼
                    ┌──────────────────────────────────────────────┐
                    │              HTML / JSON Cleaner             │
                    │  • Strip boilerplate (nav, footer, ads)      │
                    │  • Normalize whitespace                      │
                    │  • Detect content type (HTML tree vs JSON)   │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │           Chunk Scoring Engine               │
                    │                                              │
                    │  Each HTML block scored on:                  │
                    │  • Text density                              │
                    │  • Keyword overlap with requested fields     │
                    │  • Semantic entity signals                   │
                    │  • Tag structure (tables, lists, dl/dt)      │
                    │                                              │
                    │  → Only top-scoring chunk goes to AI         │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │           Entity Pre-Detection               │
                    │  • Regex + heuristics for prices, dates,     │
                    │    names, ratings, URLs before AI call       │
                    │  • Skips Gemini if all fields resolved       │
                    └──────────────────────┬───────────────────────┘
                                           │
                              ┌────────────▼────────────┐
                              │   Fields already done?  │
                              └────────────┬────────────┘
                                  NO       │      YES
                                   │       └──────────────────────┐
                                   ▼                              │
                    ┌──────────────────────────┐                  │
                    │     Gemini Extraction     │                  │
                    │  Input: scored chunk +   │                  │
                    │  requested fields        │                  │
                    │  Output: { field: value }│                  │
                    └──────────────┬───────────┘                  │
                                   └──────────────────────────────┘
                                                   │
                                                   ▼
                                    ┌──────────────────────────┐
                                    │    FastAPI Response      │
                                    │  { fields, strategy,    │
                                    │    confidence, latency } │
                                    └──────────────────────────┘
```

---

## ✨ Key Design Decisions

**Why chunk scoring before AI?**
Feeding an entire page to an LLM is expensive and noisy. The scoring engine identifies the single most relevant HTML block, reducing token usage dramatically and improving extraction accuracy.

**Why entity pre-detection?**
Prices, ratings, and dates follow predictable patterns. Resolving them with regex before hitting Gemini means many fields are extracted for free, with zero API cost.

**Why tiered rendering?**
Not all sites need a browser. Running Playwright on a static HTML page wastes time and resources. The detector makes this decision upfront from the raw HTML, not via a trial-and-error fallback.

**Why JSON interception over HTML parsing for JS-heavy sites?**
When a site loads data via background API calls, that JSON is already structured and clean. Passing it directly to Gemini is faster, cheaper, and more accurate than parsing a rendered DOM.

---

## 🚀 API Usage

```bash
POST /scrape
Content-Type: application/json

{
  "url": "https://example.com/product/123",
  "fields": ["title", "price", "rating", "description"]
}
```

Response:
```json
{
  "data": {
    "title": "Product Name",
    "price": "$29.99",
    "rating": "4.5",
    "description": "..."
  },
  "meta": {
    "strategy": "requests_ok",
    "chunk_score": 0.87,
    "ai_used": true,
    "latency_ms": 420
  }
}
```

---

## 🧪 Tested On

| Site | Type | Strategy Used |
|------|------|---------------|
| [web-scraping.dev/products](https://web-scraping.dev/products) | Static HTML, paginated mock e-commerce | `requests_ok` |
| [webscraper.io/test-sites/e-commerce/allinone](https://webscraper.io/test-sites/e-commerce/allinone) | Static HTML, nested category navigation | `requests_ok` |
| [books.toscrape.com](https://books.toscrape.com) | Static HTML, pagination + detail pages | `requests_ok` |
| [quotes.toscrape.com](https://quotes.toscrape.com) | Static HTML, author + tag metadata | `requests_ok` |
| [sandbox.oxylabs.io/products](https://sandbox.oxylabs.io/products) | Next.js SSR, 3000+ product catalogue | `requests_ok` (SSR content in response) |

---

## 🛠️ Tech Stack

- **FastAPI** — REST API layer and payload routing
- **requests** — Primary HTTP client for static pages
- **Playwright** — Browser rendering for JS-heavy sites and network interception
- **BeautifulSoup** — HTML parsing and chunk extraction
- **Gemini API** — LLM extraction on scored chunks
- **Python** — Core pipeline logic

---

## 📁 Project Structure

```
ai-scraper/
├── api.py                        # FastAPI entry point, route definitions
├── logging_config.py             # Logging setup
│
├── detectors/
│   ├── detect_rendering.py       # Render strategy detection (requests_ok / playwright_dom / playwright_network)
│   └── entity_detector.py        # Chunk scoring + Gemini-based entity selection
│
├── extractors/
│   └── data_extractor.py         # Gemini field extraction from scored chunk
│
├── scrapers/
│   └── requests_scraper.py       # HTTP fetch + DOM cleaning + Playwright (stubbed)
│
└── services/
    └── pipeline.py               # Orchestrates fetch → detect → score → extract
```

---

## 🔮 Roadmap

- [ ] Playwright network interception for GraphQL / XHR JSON responses
- [ ] Redis caching layer (URL + fields hash → cached result)
- [ ] Async job queue with polling endpoint
- [ ] Confidence scoring on Gemini output
- [ ] Proxy rotation and User-Agent fingerprinting
- [ ] React UI for live demo