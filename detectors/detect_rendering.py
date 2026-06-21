from bs4 import BeautifulSoup
from ai_scraper.logging_config import logger

def detect_render_strategy(html: str) -> str:
    """
         Returns: 'requests_ok' | 'playwright_dom' | 'playwright_network'
    """
    try:

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        visible_text = soup.get_text(separator=" ", strip=True)

        if len(visible_text) < 500:
            raw_html = html.lower()

            ### commented for now

            # check GraphQL / API hints/ XHR/fetch patterns
            # api_hints = ["graphql", "apolloclient", "gql`", "__typename", "fetch(", "xmlhttprequest", "axios", "/api/", "/v1/", "/v2/", "apollo", "relay", "urql"]
            # if any(hint in raw_html for hint in api_hints):
            #     return "playwright_network"
            #
            # # check Known SPA frameworks - needs rendering
            # dom_hints = ["__next_data__", "ng-version", "data-reactroot", "__nuxt__"]
            # if any(hint in raw_html for hint in dom_hints):
            #     return "playwright_dom"


            return "playwright_dom"

        # Enough visible text — requests is fine
        return "requests_ok"

    except Exception as e:
        logger.error(f'Exception: {e}')


# debugging
# with open('../output.html', 'r') as f:
#     text = detect_render_strategy(f.read())
#     print(text)